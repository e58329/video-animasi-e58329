# ============================================================
# pipeline/assets.py — Vector Asset Auto-Fetcher (v1)
# ------------------------------------------------------------
# Tujuan: kalau sebuah `visual:` di content YAML TIDAK ada fungsi
# gambar manualnya (VISUALS registry), pipeline otomatis:
#   1. Cari vektor di internet (iconify / wikimedia / github raw)
#   2. Cek lisensi (allowlist SPDX, tolak lisensi tidak dikenal)
#   3. Download + validasi struktur SVG (harus aman untuk manim)
#   4. Simpan ke assets/svg_auto/ + index.json + credits.json
#   5. SVGMobject import di sisi manim (scenes/templates/asset_visual.py)
#
# CLI:
#   python -m pipeline.assets search <query> [--provider iconify] [--limit 8]
#   python -m pipeline.assets fetch <visual_name> [--query ...] [--color ...]
#   python -m pipeline.assets prefetch <content.yaml>
#   python -m pipeline.assets credits
#
# Catatan lisensi: CC-BY / CC-BY-SA / MIT dsb. WAJIB atribusi.
# Jalankan `python -m pipeline.assets credits` sebelum publish video,
# lalu tempel isi ASSETS-ATTRIBUTION.md ke deskripsi video.
# ============================================================
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets" / "svg_auto"
INDEX_PATH = ASSET_DIR / "index.json"
CREDITS_PATH = ASSET_DIR / "credits.json"
ATTR_PATH = ROOT / "ASSETS-ATTRIBUTION.md"

TIMEOUT = 10
UA = "stickman3.7-pipeline/1.0 (educational video production)"

# ---------- LISENSI ----------
# (spdx, butuh_atribusi?)  — kalau lisensi tidak ada di sini => TOLAK
LICENSE_ALLOW = {
    "CC0-1.0": False, "CC-BY-4.0": True, "CC-BY-3.0": True,
    "CC-BY-SA-4.0": True, "CC-BY-SA-3.0": True,
    "MIT": True, "Apache-2.0": True, "ISC": True,
    "BSD-2-Clause": True, "BSD-3-Clause": True,
    # Wikimedia kadang menulis begini:
    "Public domain": False, "CC BY 4.0": True, "CC BY-SA 4.0": True,
    "CC BY 3.0": True, "CC BY-SA 3.0": True,
}

ICONIFY_API = "https://api.iconify.design"
# Ranking koleksi: 0 = paling disukai (flat, colorful, cocok gaya channel)
ICONIFY_RANK = {
    "fluent-emoji": 0, "fluent-emoji-flat": 0, "twemoji": 1, "noto": 1,
    "mdi": 2, "material-symbols": 2, "ic": 2,
    "tabler": 3, "lucide": 3, "ri": 3, "ph": 3, "solar": 3,
    "fa6-solid": 3, "game-icons": 4, "streamline-emojis": 1,
}


class AssetError(Exception):
    pass


# ---------- UTIL ----------
def _slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get(url, **kw):
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA}, **kw)
    r.raise_for_status()
    return r


# ---------- VALIDASI SVG (aman-untuk-manim) ----------
FORBIDDEN_TAGS = {"text", "tspan", "image", "script", "foreignObject", "style"}
MAX_NODES = 400          # terlalu kompleks = manim lambat & sering rusak
MAX_BYTES = 300_000


def validate_svg(svg_bytes, force_color=None):
    """Parse SVG, tolak kalau tidak aman untuk SVGMobject.
    Return (ok, info, kenapa) — info berisi n_nodes & multicolor.
    Catatan: manim tidak render <defs> gradient dengan benar, jadi SVG
    yang SEMUA path-nya isi gradient ditolak (biar kandidat berikutnya
    yang flat dipakai)."""
    if len(svg_bytes) > MAX_BYTES:
        return False, {}, "SVG terlalu besar (>%dKB)" % (MAX_BYTES // 1000)
    try:
        root = ET.fromstring(svg_bytes)
    except ET.ParseError as e:
        return False, {}, f"XML tidak valid: {e}"

    def local(t):
        return t.split("}")[-1].lower()

    if local(root.tag) != "svg":
        return False, {}, "root bukan <svg>"

    STRUCTURAL = {"defs", "clippath", "lineargradient", "radialgradient",
                  "mask", "filter", "pattern", "symbol", "metadata",
                  "title", "desc"}
    DRAW = {"g", "path", "circle", "ellipse", "rect", "polygon",
            "polyline", "line"}
    n = 0
    n_grad = 0
    fills = set()

    def walk(el):
        nonlocal n, n_grad
        for child in list(el):
            t = local(child.tag)
            if t in FORBIDDEN_TAGS:
                raise _VRej(f"elemen <{t}> tidak didukung manim (pakai ikon path-only)")
            if t in STRUCTURAL:
                continue          # skip seluruh subtree defs/mask/dll
            if t in DRAW:
                n += 1
                f = (child.get("fill") or "").lower()
                if f.startswith("url(#"):
                    n_grad += 1
                elif f not in ("", "none", "currentcolor"):
                    fills.add(f)
            else:
                raise _VRej(f"elemen <{t}> tidak dikenal")
            if n > MAX_NODES:
                raise _VRej(f"terlalu kompleks (>{MAX_NODES} node)")
            walk(child)

    class _VRej(Exception):
        pass

    try:
        walk(root)
    except _VRej as e:
        return False, {}, str(e)

    if n == 0:
        return False, {}, "tidak ada elemen gambar"
    if n_grad == n and not fills:
        return False, {"n_nodes": n}, \
            "semua path pakai gradient (manim tidak render gradient SVG) -> butuh ikon flat"
    if root.get("viewBox") is None and root.get("width") is None:
        return False, {}, "tanpa viewBox/width"
    return True, {"n_nodes": n, "multicolor": len(fills) > 1,
                  "has_gradient": n_grad > 0}, ""


# ---------- PROVIDER: ICONIFY ----------
def iconify_search(query, limit=16):
    d = _get(f"{ICONIFY_API}/search",
             params={"query": query, "limit": limit}).json()
    out = []
    for full in d.get("icons", []):
        prefix, _, name = full.partition(":")
        out.append({"provider": "iconify", "prefix": prefix, "name": name,
                    "id": full, "url_api": f"{ICONIFY_API}/{prefix}/{name}.svg"})
    return out, d.get("collections", {})


def iconify_license(prefixes):
    if not prefixes:
        return {}
    try:
        d = _get(f"{ICONIFY_API}/collections",
                 params={"prefixes": ",".join(prefixes)}).json()
        # API: dengan prefixes -> dict langsung; tanpa -> dibungkus "collections"
        if "collections" in d and "license" not in d.get("collections", {}) and isinstance(d.get("collections"), dict):
            d = d["collections"]
        out = {}
        for k, v in d.items():
            if isinstance(v, dict) and "license" in v:
                out[k] = v.get("license") or {}
        return out
    except Exception:
        return {}


def _score_icon(icon, query_words):
    name = icon["name"].lower()
    q = " ".join(query_words)
    s = 0
    rank = ICONIFY_RANK.get(icon["prefix"], 5)
    s += (5 - min(rank, 5))
    clean = name.replace("-filled", "").replace("-alt", "").replace("-regular", "")
    if clean in query_words:
        s += 8
    elif q and (q in name or clean == q.replace(" ", "-")):
        s += 6
    elif any(w in name for w in query_words):
        s += 3
    if name.endswith("-filled"):
        s += 2
    return s


def iconify_pick(query, color=None, collection=None, limit=24):
    """Cari & pilih ikon terbaik. Return dict kandidat + svg_bytes.
    Tangga pencarian (degradasi halus):
      1. query penuh, difilter koleksi (kalau user minta koleksi)
      2. query penuh, bebas (koleksi tetap dapat bonus skor)
      3. kata pertama query, bebas (mis. 'rocket launch' -> 'rocket')"""
    query_words = [w for w in re.split(r"[\s_\-]+", query.lower()) if w]

    def _pool(q, coll):
        """Return hasil search; kalau coll diisi, HANYA ikon koleksi itu
        (boleh kosong — degradasi ditangani tangga di caller)."""
        icons, _ = iconify_search(q, limit=limit)
        if coll:
            return [i for i in icons if i["prefix"] == coll]
        return icons

    def _direct(qwords, coll):
        """Search iconify kadang gak nge-index koleksi tertentu (mis.
        fluent-emoji). Coba tebak nama ikon langsung: rocket, rocket-filled,
        rocket-launch, dst. Return list 0/1 kandidat."""
        if not coll:
            return []
        names = []
        for n in ("-".join(qwords), qwords[0]):
            for cand in (n, n + "-filled", n + "-regular", n + "-outline"):
                if cand and cand not in names:
                    names.append(cand)
        for n in names:
            url = f"{ICONIFY_API}/{coll}/{n}.svg"
            try:
                if _get(url).status_code == 200:
                    print(f"[assets] search gak nemu, tebak langsung OK: {coll}:{n}")
                    return [{"provider": "iconify", "prefix": coll, "name": n,
                             "id": f"{coll}:{n}", "url_api": url}]
            except Exception:
                continue
        return []

    pool = []
    if collection:
        # hormati dulu keinginan koleksi: query penuh, lalu kata pertama
        pool = _pool(query, collection)
        if not pool and len(query_words) > 1:
            pool = _pool(query_words[0], collection)
        if not pool:
            pool = _direct(query_words, collection)
        if pool:
            print(f"[assets] pakai koleksi '{collection}'")
        else:
            print(f"[assets] koleksi '{collection}' gak punya kandidat "
                  f"'{query}' -> cari bebas")
    if not pool:
        pool = _pool(query, None)
    if not pool and len(query_words) > 1:
        pool = _pool(query_words[0], None)
    if not pool:
        raise AssetError(f"iconify: tidak ada hasil untuk '{query}'")

    def _try_pool(pool):
        """Skor + download + validasi kandidat. Return dict atau None."""
        lic = iconify_license(sorted({i["prefix"] for i in pool}))
        scored = []
        for i in pool:
            L = lic.get(i["prefix"], {})
            spdx = L.get("spdx") or L.get("title") or ""
            if spdx not in LICENSE_ALLOW:
                continue
            s = _score_icon(i, query_words)
            if collection and i["prefix"] == collection:
                s += 4          # bonus: sesuai permintaan user walau fallback bebas
            scored.append((s, i, spdx, L.get("title", spdx)))
        scored.sort(key=lambda x: -x[0])
        # DUA-PASS: pass 1 hanya kandidat TANPA gradient (paling aman di
        # manim), pass 2 baru izinkan yang ada gradientnya.
        for allow_grad in (False, True):
            for score, icon, spdx, ltitle in scored:
                params = {"height": "512"}
                if color and color.lower() not in ("auto", "none"):
                    params["color"] = color
                try:
                    svg = _get(icon["url_api"], params=params).content
                except Exception:
                    continue
                ok, info, why = validate_svg(svg)
                if ok and (allow_grad or not info.get("has_gradient")):
                    return {"svg": svg, "id": icon["id"], "spdx": spdx,
                            "license_title": ltitle,
                            "multicolor": info["multicolor"],
                            "source": icon["url_api"],
                            "attribution": f"{icon['id']} — {ltitle} — via Iconify (api.iconify.design)"}
        return None

    picked = _try_pool(pool)
    if picked is None and collection:
        # kandidat koleksi gak lolos validasi (gradient/kompleks/lisensi)
        # -> degradasi terakhir: cari bebas
        print("[assets] kandidat koleksi gak lolos validasi -> cari bebas")
        pool2 = _pool(query, None)
        if not pool2 and len(query_words) > 1:
            pool2 = _pool(query_words[0], None)
        if pool2:
            picked = _try_pool(pool2)
    if picked is None:
        raise AssetError(f"iconify: semua kandidat '{query}' gagal validasi/lisensi")
    return picked


# ---------- PROVIDER: WIKIMEDIA COMMONS ----------
WM_API = "https://commons.wikimedia.org/w/api.php"


def _wm_license(info):
    meta = info.get("extmetadata", {})
    def g(k):
        v = meta.get(k, {}).get("value", "") or ""
        return re.sub(r"<[^>]+>", "", v).strip()
    short = g("LicenseShortName")
    for key in LICENSE_ALLOW:
        if short.lower() == key.lower() or short == key:
            return key, key
    # map longgar
    m = re.match(r"(?i)cc\s*([^- ]*)\s*(-sa)?\s*([\d.]+)?", short)
    if m:
        typ, sa, ver = m.groups()
        ver = (ver or "4.0").rstrip(".")
        spdx = f"CC-BY{'-SA' if sa else ''}-{ver}"
        if spdx in LICENSE_ALLOW:
            return spdx, short
    if "public domain" in short.lower() or g("UsageTerms").lower().startswith("public domain"):
        return "Public domain", short or "Public domain"
    return None, short


def wikimedia_pick(query):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:svg {query}", "gsrlimit": 12, "gsrnamespace": 6,
        "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
    }
    try:
        d = _get(WM_API, params=params).json()
    except requests.RequestException as e:
        kode = getattr(e.response, "status_code", "?")
        raise AssetError(
            f"wikimedia: request gagal (HTTP {kode}" 
            f"{'; 429 = rate-limit, tunggu sebentar / pakai iconify' if kode == 429 else ''})")
    pages = (d.get("query") or {}).get("pages") or {}
    cands = []
    for p in pages.values():
        for ii in p.get("imageinfo", []):
            if ii.get("mime") != "image/svg+xml":
                continue
            spdx, ltitle = _wm_license(ii)
            if not spdx or spdx not in LICENSE_ALLOW:
                continue
            meta = ii.get("extmetadata", {})
            artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "") or "").strip()
            cands.append({"title": p.get("title", ""), "url": ii.get("url"),
                          "size": ii.get("size", 0), "spdx": spdx, "ltitle": ltitle,
                          "artist": artist})
    if not cands:
        raise AssetError(f"wikimedia: tidak ada SVG '{query}' dengan lisensi di allowlist")
    cands.sort(key=lambda c: c["size"])   # kecil = biasanya ikon/vektor sederhana
    for c in cands[:6]:
        try:
            svg = _get(c["url"]).content
        except Exception:
            continue
        ok, info, why = validate_svg(svg)
        if ok:
            attr = c["title"].replace("File:", "")
            if c["artist"]:
                attr += f" oleh {c['artist']}"
            attr += f" — {c['ltitle']} — Wikimedia Commons"
            return {"svg": svg, "id": c["title"], "spdx": c["spdx"],
                    "license_title": c["ltitle"], "multicolor": info["multicolor"],
                    "source": c["url"], "attribution": attr}
    raise AssetError(f"wikimedia: semua kandidat '{query}' gagal validasi manim")


# ---------- PROVIDER: GITHUB (raw) ----------
def github_pick(spec):
    """spec: 'owner/repo/path/file.svg' (raw). Token opsional via GITHUB_TOKEN.
    Lisensi dibaca dari LICENSE repo (naive match SPDX)."""
    m = re.match(r"^([\w.\-]+)/([\w.\-]+)/(.+\.svg)$", spec)
    if not m:
        raise AssetError("github: format harus 'owner/repo/path/file.svg'")
    owner, repo, path = m.groups()
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"User-Agent": UA}
    if token:
        headers["Authorization"] = f"token {token}"
    branch = None
    for br in ("main", "master"):
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{br}/{path}"
        try:
            r = requests.get(url, timeout=TIMEOUT, headers=headers)
            if r.status_code == 200:
                branch = br
                svg = r.content
                break
        except Exception:
            continue
    if branch is None:
        raise AssetError(f"github: gagal download {owner}/{repo}/{path} (main/master)")
    lic_spdx, lic_title = "MIT", "MIT (asumsi)"   # default; coba baca LICENSE
    try:
        lr = requests.get(
            f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/LICENSE",
            timeout=TIMEOUT, headers=headers)
        txt = lr.text[:4000].lower()
        for spdx in ("apache-2.0", "mit", "bsd-3-clause", "bsd-2-clause", "isc", "cc0-1.0"):
            if spdx in txt:
                lic_spdx, lic_title = spdx, spdx
                break
    except Exception:
        pass
    if lic_spdx not in LICENSE_ALLOW:
        raise AssetError(f"github: lisensi repo '{lic_spdx}' tidak di allowlist")
    ok, info, why = validate_svg(svg)
    if not ok:
        raise AssetError(f"github: SVG gagal validasi: {why}")
    return {"svg": svg, "id": f"{owner}/{repo}/{path}", "spdx": lic_spdx,
            "license_title": lic_title, "multicolor": info["multicolor"],
            "source": f"https://github.com/{owner}/{repo}/blob/{branch}/{path}",
            "attribution": f"{owner}/{repo} (file {path}) — {lic_title} — GitHub"}


# ---------- RESOLVE UTAMA ----------
def _spec_hash(spec):
    """Hash spesifikasi (query/color/provider/collection) — dipakai untuk
    mendeteksi perubahan override YAML: kalau berubah, fetch ulang."""
    canon = json.dumps({k: v for k, v in sorted(spec.items())
                        if k in ("provider", "query", "color", "collection", "github")},
                       sort_keys=True)
    return __import__("hashlib").sha1(canon.encode()).hexdigest()[:10]


def resolve(name, spec=None, force=False):
    """Ambil aset untuk visual `name`. spec (opsional):
       {provider: iconify|wikimedia|github, query: str, color: '#RRGGBB',
        collection: str, github: 'owner/repo/path.svg'}
       Return dict entry index. Cache: assets/svg_auto/<name>.svg
       Cache invalid otomatis kalau spec override berubah."""
    spec = spec or {}
    index = _load_json(INDEX_PATH, {})
    h = _spec_hash(spec)
    if not force and name in index and index[name].get("spec_hash") == h \
       and (ASSET_DIR / f"{_slug(name)}.svg").exists():
        return index[name]

    provider = spec.get("provider")
    if spec.get("github"):
        provider = "github"
    query = spec.get("query") or name.replace("_", " ")
    color = spec.get("color", "#FFFFFF")

    if provider is None:
        # auto: github spec menang, kalau tidak default iconify
        provider = "iconify"

    if provider == "github":
        picked = github_pick(spec["github"])
    elif provider == "wikimedia":
        picked = wikimedia_pick(query)
    else:
        picked = iconify_pick(query, color=color,
                              collection=spec.get("collection"))

    svg_path = ASSET_DIR / f"{_slug(name)}.svg"
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_bytes(picked["svg"])

    entry = {
        "file": str(svg_path.relative_to(ROOT)),
        "provider": provider, "query": query, "spec_hash": h,
        "asset_id": picked["id"], "source": picked["source"],
        "license": picked["spdx"], "license_title": picked["license_title"],
        "attribution": picked["attribution"],
        "needs_attribution": LICENSE_ALLOW.get(picked["spdx"], True),
        "multicolor": picked["multicolor"],
        "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    index[name] = entry
    _save_json(INDEX_PATH, index)

    credits = _load_json(CREDITS_PATH, [])
    if not any(c.get("asset_id") == picked["id"] and c.get("visual") == name
               for c in credits):
        credits.append({"visual": name, **entry})
        _save_json(CREDITS_PATH, credits)
    return entry


# ---------- PREFETCH (scan YAML) ----------
def prefetch(yaml_path):
    import yaml as _yaml
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = _yaml.safe_load(f)
    overrides = data.get("asset_overrides") or {}
    needed = []
    for sec in data.get("sections", []):
        for p in sec.get("points", []):
            v = p.get("visual") if isinstance(p, dict) else None
            if v:
                needed.append(v)
    ok, fail = [], []
    for v in needed:
        try:
            e = resolve(v, overrides.get(v))
            ok.append((v, e["license"]))
        except AssetError as ex:
            fail.append((v, str(ex)))
        time.sleep(0.2)
    return ok, fail


# ---------- ATTRIBUTION BUILDER ----------
def build_attribution_md():
    credits = _load_json(CREDITS_PATH, [])
    if not credits:
        return "Belum ada aset eksternal yang dipakai."
    lines = ["# Atribusi Aset Eksternal",
             "",
             "Aset vektor berikut dipakai dalam produksi video.",
             "Tempel daftar ini ke deskripsi video yang memakainya.",
             ""]
    for c in credits:
        lic = c.get("license", "?")
        tag = " (atribusi wajib)" if c.get("needs_attribution") else ""
        lines.append(f"- `{c.get('visual','?')}` — {c.get('attribution', lic)} [{lic}]{tag}  ")
        lines.append(f"  Sumber: {c.get('source','')}")
    return "\n".join(lines) + "\n"


# ---------- CLI ----------
def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="stickman3.7 vector asset fetcher")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("search")
    s1.add_argument("query")
    s1.add_argument("--provider", default="iconify")
    s1.add_argument("--limit", type=int, default=12)

    s2 = sub.add_parser("fetch")
    s2.add_argument("name")
    s2.add_argument("--query")
    s2.add_argument("--provider", default="iconify")
    s2.add_argument("--color", default="#FFFFFF")
    s2.add_argument("--collection")
    s2.add_argument("--github", help="owner/repo/path/file.svg")
    s2.add_argument("--force", action="store_true")

    s3 = sub.add_parser("prefetch")
    s3.add_argument("yaml_path")

    sub.add_parser("credits")
    sub.add_parser("list")

    a = ap.parse_args()
    if a.cmd == "search":
        if a.provider == "wikimedia":
            cands = []
            d = _get(WM_API, params={
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": f"filetype:svg {a.query}", "gsrlimit": a.limit,
                "gsrnamespace": 6, "prop": "imageinfo",
                "iiprop": "url|extmetadata|mime"}).json()
            for p in ((d.get("query") or {}).get("pages") or {}).values():
                for ii in p.get("imageinfo", []):
                    if ii.get("mime") != "image/svg+xml":
                        continue
                    spdx, lt = _wm_license(ii)
                    cands.append((p.get("title", ""), lt or "?",
                                  "OK" if spdx else "TOLAK"))
            for t, l, st in cands:
                print(f"  [{st:>5}] {t}  ({l})")
        else:
            icons, _ = iconify_search(a.query, limit=a.limit)
            lic = iconify_license(sorted({i["prefix"] for i in icons}))
            qw = [w for w in re.split(r"[\s_\-]+", a.query.lower()) if w]
            for i in sorted(icons, key=lambda x: -_score_icon(x, qw)):
                L = lic.get(i["prefix"], {})
                spdx = L.get("spdx", "?")
                flag = "OK " if spdx in LICENSE_ALLOW else "TOL"
                print(f"  [{flag}] {i['id']:<40} {spdx}")
    elif a.cmd == "fetch":
        spec = {"provider": a.provider, "color": a.color}
        if a.query:
            spec["query"] = a.query
        if a.collection:
            spec["collection"] = a.collection
        if a.github:
            spec["github"] = a.github
        try:
            e = resolve(a.name, spec, force=a.force)
        except AssetError as ex:
            print(f"❌ {a.name}: {ex}")
            raise SystemExit(1)
        print(f"✅ {a.name} -> {e['file']}")
        print(f"   {e['asset_id']} | lisensi {e['license']} | "
              f"{'MULTICOLOR' if e['multicolor'] else 'mono'}")
        if e["needs_attribution"]:
            print("   ⚠️ lisensi butuh atribusi — jangan lupa `python -m pipeline.assets credits`")
    elif a.cmd == "prefetch":
        ok, fail = prefetch(a.yaml_path)
        for v, l in ok:
            print(f"  ✅ {v} ({l})")
        for v, why in fail:
            print(f"  ❌ {v}: {why}")
        print(f"\n{len(ok)} sukses, {len(fail)} gagal")
    elif a.cmd == "credits":
        ATTR_PATH.write_text(build_attribution_md(), encoding="utf-8")
        print(f"✅ ditulis: {ATTR_PATH}")
    elif a.cmd == "list":
        idx = _load_json(INDEX_PATH, {})
        if not idx:
            print("(kosong — belum ada aset yang di-fetch)")
        for k, e in idx.items():
            print(f"  {k:<28} {e['asset_id']:<32} {e['license']}")


if __name__ == "__main__":
    _cli()

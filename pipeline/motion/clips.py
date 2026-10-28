# ============================================================
# pipeline/motion/clips.py — Motion graphics generator (pymotion)
# ------------------------------------------------------------
# Template motion graphics yang dirender LOKAL (gak perlu internet,
# gak ada isu lisensi) lalu diembed ke scene Manim sebagai frame
# PNG transparan (scenes/templates/motion_visual.py).
#
# Alur: vis_motion() -> ensure_clip(template, spec, dur)
#       -> motion/cache/<template>-<hash>/f%04d.png (cache spec-hash)
#
# CATATAN ENGINE (pymotion 3.7.0) — penting biar gak ngulik ulang:
#   - SEMUA durasi dalam FRAME, bukan detik.
#   - ShapeClip/TextClip = STATIC (render sekali, di-cache). Geometry
#     lewat params/classmethod (rect/ellipse/polygon/line) —
#     _position/_scale TIDAK dikonsumsi renderer statis.
#   - Yang dinamis per-frame: NumberCounter, ProgressBar, KineticText
#     (render ulang tiap frame), dan OPACITY semua clip (dievaluasi
#     di level composite). Jadi animasi = reveal opacity berjenjang
#     + clip native yang memang bergerak.
#
# CLI:
#   python -m pipeline.motion.clips list
#   python -m pipeline.motion.clips render route_map --spec '{"title":"X"}' --dur 6
# ============================================================
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = ROOT / "motion" / "cache"
FPS_DEFAULT = 30
W_DEFAULT, H_DEFAULT = 800, 450   # 16:9, cukup buat zona kartu explainer

try:
    from pymotion import (Composition, Track, TextClip, ShapeClip,
                          NumberCounter, ProgressBar, KineticText, Color, Vec2)
except Exception as e:  # pymotion belum terinstall -> modul mati sopan
    Composition = None
    Vec2 = None
    _IMPORT_ERR = str(e)


class MotionError(Exception):
    pass


# ---------- helpers ----------
def _smooth(p):
    """smoothstep 0..1 -> easing halus tanpa jerks."""
    p = max(0.0, min(1.0, p))
    return p * p * (3.0 - 2.0 * p)


def _brand(spec):
    """Warna brand channel (bisa dioverride via spec). Font default:
    Montserrat bawaan repo (path langsung, biar konsisten semua mesin)."""
    fm = ROOT / "assets" / "fonts" / "Montserrat-Bold.ttf"
    font = str(fm) if fm.is_file() else spec.get("font", "Montserrat Bold")
    return {
        "primary": spec.get("primary", "#1E88E5"),
        "accent":  spec.get("accent",  "#FFC107"),
        "ink":     spec.get("ink",     "#F5F7FA"),
        "mist":    spec.get("mist",    "#90A4AE"),
        "deep":    spec.get("deep",    "#0F2A4A"),
        "navy":    spec.get("navy",    "#0B1426"),
        "sea":     spec.get("sea",     "#134B7C"),
        "green":   spec.get("green",   "#2E7D5B"),
        "coral":   spec.get("coral",   "#EF5350"),
        "font":    spec.get("font",    font),
    }


def _add(comp, *clips):
    tr = Track(name=f"t{len(comp.tracks)}")
    for c in clips:
        tr.add(c)
    comp.add_track(tr)
    return tr


_GLYPH = None
def _probe_tw(text, font, size, color="#FFFFFF"):
    """Ukur lebar teks (px) via glyph renderer pymotion.
    Fallback: estimasi 0.62*size per karakter."""
    global _GLYPH
    try:
        if _GLYPH is None:
            from pymotion.clip.text import TextClip as _TC
            _GLYPH = _TC._glyph_renderer
        img = _GLYPH.render_text(str(text), font, float(size), Color.parse(color))
        return float(img.shape[1])
    except Exception:
        return max(40.0, 0.62 * float(size) * len(str(text)))


def _txt_center(text, b, size, color, y, W, N, fade=4.0):
    """TextClip statis CENTER horizontal di y, fade-in opacity."""
    tw = _probe_tw(text, b["font"], size, color)
    t = TextClip(text, font=b["font"], size=float(size), color=color,
                 align="center")
    t.set_duration(N)
    t.set_position((W - tw) / 2.0, y)
    t.set_expression("opacity", lambda c, fd=fade: _smooth(c.progress * fd))
    return t


def _poly(pts):
    return ShapeClip.polygon([(float(x), float(y)) for x, y in pts])


# ---------- TEMPLATE 1: route_map ----------
def _tpl_route_map(spec, W, H, N, fps):
    """Peta jalur: panel laut + pulau + jalur titik menyala berurutan +
    cincin dest pulse. (Marker gak bisa meluncur — engine statis —
    jadi bahasanya 'reveal rute' + pulse.)"""
    b = _brand(spec)
    pts = spec.get("points") or [[0.10, 0.60], [0.38, 0.32], [0.64, 0.56], [0.88, 0.26]]
    pts = [[float(x) * W, float(y) * H] for x, y in pts]
    comp = Composition(width=W, height=H, fps=fps, duration=N,
                       background=spec.get("bg", "#00000000"))

    # panel laut (fade in cepat)
    sea = ShapeClip.rect(8, 8, W - 16, H - 16, fill=b["deep"])
    sea.set_duration(N)
    sea.set_expression("opacity", lambda c: 0.62 * _smooth(c.progress * 4))
    _add(comp, sea)

    # daratan (fade in belakangan)
    l1 = _poly([[0.55*W, 0.06*H], [0.97*W, 0.12*H], [0.99*W, 0.46*H],
                [0.82*W, 0.64*H], [0.60*W, 0.50*H], [0.53*W, 0.30*H]])
    l1.set_fill(b["green"])
    l1.set_duration(N)
    l1.set_expression("opacity", lambda c: 0.34 * _smooth((c.progress - 0.08) * 5))
    _add(comp, l1)

    l2 = _poly([[0.03*W, 0.76*H], [0.30*W, 0.72*H], [0.42*W, 0.94*H],
                [0.10*W, 0.98*H]])
    l2.set_fill(b["green"])
    l2.set_duration(N)
    l2.set_expression("opacity", lambda c: 0.26 * _smooth((c.progress - 0.14) * 5))
    _add(comp, l2)

    # jalur putus-putus: titik muncul berurutan sepanjang polyline
    def _len(pp):
        return [0.0] + [math.dist(pp[i-1], pp[i]) for i in range(1, len(pp))]

    seg = _len(pts)
    total = sum(seg)
    n_dots = int(spec.get("dots", 14))
    r_dot = float(spec.get("dot_r", 4.0))
    for i in range(n_dots):
        target = total * (i + 1) / (n_dots + 1)
        acc, pos = 0.0, pts[0]
        for k in range(1, len(pts)):
            acc += seg[k]
            if target <= acc:
                t = (target - (acc - seg[k])) / max(seg[k], 1e-6)
                pos = [pts[k-1][0] + (pts[k][0]-pts[k-1][0]) * t,
                       pts[k-1][1] + (pts[k][1]-pts[k-1][1]) * t]
                break
            pos = pts[-1]
        d = ShapeClip.ellipse(pos[0], pos[1], r_dot, r_dot,
                              fill=spec.get("route", b["accent"]))
        d.set_duration(N)
        d.set_expression("opacity",
                         lambda c, k=i: _smooth(c.progress * (n_dots + 3) - k))
        _add(comp, d)

    # origin dot (permanen) + dest marker + cincin pulse
    o = ShapeClip.ellipse(pts[0][0], pts[0][1], 7, 7, fill=b["ink"])
    o.set_duration(N)
    o.set_expression("opacity", lambda c: _smooth(c.progress * 6))
    _add(comp, o)

    last = pts[-1]
    mk = ShapeClip.ellipse(last[0], last[1], 9, 9, fill=b["ink"])
    mk.set_duration(N)
    mk.set_expression("opacity", lambda c: _smooth((c.progress - 0.45) * 4))
    _add(comp, mk)

    for k, rr in enumerate((20, 30)):
        ring = ShapeClip.ellipse(last[0], last[1], rr, rr, fill=b["accent"])
        ring.set_duration(N)
        ring.set_expression("opacity",
                            lambda c, ph=k * 0.5: 0.35 * (0.5 + 0.5 * math.sin(
                                (c.progress * 2.4 + ph) * 2 * math.pi)))
        _add(comp, ring)

    # label origin & dest (statis, fade saat rute lewat)
    for (px, py), txt, delay in ((pts[0], str(spec.get("origin", "")), 0.18),
                                 (last, str(spec.get("dest", "")), 0.55)):
        if not txt:
            continue
        t = TextClip(txt, font=b["font"], size=24, color=b["ink"], align="left")
        t.set_duration(N)
        t.set_position(min(px + 16, W - 180), max(py - 30, 12))
        t.set_expression("opacity",
                         lambda c, dd=delay: _smooth((c.progress - dd) * 5))
        _add(comp, t)

    # judul kiri-atas + sub kiri-bawah
    title = TextClip(str(spec.get("title", "Jalur Perjalanan")), font=b["font"],
                     size=40, color=b["ink"], align="left")
    title.set_duration(N)
    title.set_position(26, 24)
    title.set_expression("opacity", lambda c: _smooth(c.progress * 3))
    _add(comp, title)

    sub_txt = str(spec.get("sub", ""))
    if sub_txt:
        sub = TextClip(sub_txt, font=b["font"], size=24, color=b["mist"],
                       align="left")
        sub.set_duration(N)
        sub.set_position(26, H - 44)
        sub.set_expression("opacity",
                           lambda c: _smooth(max(c.progress - 0.35, 0) * 4))
        _add(comp, sub)
    return comp


# ---------- TEMPLATE 2: stat_counter ----------
def _tpl_stat_counter(spec, W, H, N, fps):
    """Angka besar count-up (native) + label + progress bar (native)."""
    b = _brand(spec)
    comp = Composition(width=W, height=H, fps=fps, duration=N,
                       background=spec.get("bg", "#00000000"))

    val_to = float(spec.get("value_to", 3800))
    val_from = float(spec.get("value_from", 0))
    fmt = str(spec.get("fmt", "{:,.0f}"))
    suffix = str(spec.get("suffix", ""))
    count_f = max(int(N * 0.62), 2)

    label_txt = str(spec.get("label", "STATISTIK")).upper()
    _add(comp, _txt_center(label_txt, b, 30, b["mist"], 64, W, N, fade=4.0))

    counter = NumberCounter(start_value=val_from, end_value=val_to,
                            count_duration=count_f, font=b["font"],
                            size=110.0, color=Color.parse(b["ink"]),
                            padding=(0, 0, 0, 0))
    counter.set_duration(N)
    counter.format_fn = (lambda v, f=fmt, s=suffix: f.format(v) + s) \
        if suffix else (lambda v, f=fmt: f.format(v))
    counter.set_expression("opacity", lambda c: _smooth(c.progress * 5))
    _add(comp, counter)

    bar_w = float(spec.get("bar_w", 420))
    bar = ProgressBar(value=lambda f: _smooth(f / max(count_f, 1)),
                      bar_width=bar_w, bar_height=9.0,
                      fill_color=Color.parse(b["accent"]),
                      bg_color=Color.parse(b["navy"]), radius=9999,
                      padding=(0, 0, 0, 0))
    bar.set_duration(N)
    # SEMANTIK: posisi ProgressBar = CENTER bar, bukan pojok kiri-atas
    bar.set_position(W / 2.0, H * 0.70)
    bar.set_expression("opacity", lambda c: _smooth(c.progress * 5))
    _add(comp, bar)

    cap = str(spec.get("caption", ""))
    if cap:
        _add(comp, _txt_center(cap, b, 24, b["ink"], H - 72, W, N, fade=0))
        # caption muncul belakangan: override opacity expr terakhir
        comp.tracks[-1].clips[-1].set_expression(
            "opacity", lambda c: _smooth(max(c.progress - 0.42, 0) * 5))
    return comp


# ---------- TEMPLATE 3: kinetic_hook ----------
def _tpl_kinetic_hook(spec, W, H, N, fps):
    """Kata-kata besar muncul berurutan per baris (KineticText native:
    spring slide-in dari kanan). Satu clip per baris, warna selang-seli."""
    b = _brand(spec)
    comp = Composition(width=W, height=H, fps=fps, duration=N,
                       background=spec.get("bg", "#00000000"))
    lines = [str(x) for x in (spec.get("lines") or
                              ["TAHU GAK", "SIH?"])]
    lines = [x for x in lines if x.strip()] or ["..."]
    colors = list(spec.get("colors") or [b["ink"], b["accent"], b["ink"],
                                         b["accent"]])
    size = float(spec.get("size", 84))
    gap = max(int(N * 0.72 / len(lines)), 6)   # jeda antar baris (frame)

    lh = size * 1.24
    y0 = H / 2 - (len(lines) - 1) * lh / 2
    for i, line in enumerate(lines):
        txt = TextClip(line, font=b["font"], size=size,
                       color=colors[i % len(colors)])
        tw = _probe_tw(line, b["font"], size, colors[i % len(colors)])
        k = KineticText(text=line, font_size=size,
                        color=Color.parse(colors[i % len(colors)]),
                        frames_per_word=max(int(fps * 0.32), 4),
                        position=Vec2((W - tw) / 2.0, y0 + i * lh - size * 0.62))
        k.start = i * gap
        k.set_duration(N - k.start)
        del txt
        _add(comp, k)

    # garis aksen di bawah, fade belakangan
    bar = ShapeClip.rect(W * 0.30, H * 0.86, W * 0.40, 6, fill=b["accent"])
    bar.set_duration(N)
    bar.set_expression("opacity",
                       lambda c: _smooth(max(c.progress - 0.55, 0) * 4) * 0.9)
    _add(comp, bar)
    return comp


# ---------- TEMPLATE 4: bar_compare ----------
def _tpl_bar_compare(spec, W, H, N, fps):
    """Perbandingan batang: fill 'blocky' via segmen opacity berjenjang
    (engine statis -> cara paling bersih bikin kesan tumbuh)."""
    b = _brand(spec)
    comp = Composition(width=W, height=H, fps=fps, duration=N,
                       background=spec.get("bg", "#00000000"))
    bars = list(spec.get("bars") or
                [{"label": "A", "value": 60}, {"label": "B", "value": 100}])
    bars = bars[:5]
    vals = [max(float(x.get("value", 1)), 0.001) for x in bars]
    vmax = max(vals)
    unit = str(spec.get("unit", ""))
    hi = int(spec.get("hi", len(bars) - 1))
    rows = len(bars)

    top = 92 if spec.get("title") else 52
    row_h = (H - top - 40) / rows
    x_label, x_bar, bar_max_w = 26, 170, W - 290
    n_seg = 12

    title = str(spec.get("title", ""))
    if title:
        t = TextClip(title, font=b["font"], size=36, color=b["ink"],
                     align="left")
        t.set_duration(N)
        t.set_position(26, 28)
        t.set_expression("opacity", lambda c: _smooth(c.progress * 4))
        _add(comp, t)

    for i, item in enumerate(bars):
        y = top + row_h * (i + 0.5)
        frac = vals[i] / vmax
        gs = i * N * 0.10                      # mulai tumbuh (frame)
        fill_f = N * 0.58                      # durasi tumbuh
        col = item.get("color") or (b["accent"] if i == hi else b["primary"])

        lb = TextClip(str(item.get("label", f"#{i+1}")), font=b["font"],
                      size=26, color=b["mist"], align="left")
        lb.set_duration(N)
        lb.set_position(x_label, y - 14)
        lb.set_expression("opacity",
                          lambda c, gs_=gs: _smooth((c.frame - gs_) / max(N*0.10, 1)))
        _add(comp, lb)

        tr = ShapeClip.rect(x_bar, y - row_h * 0.22, bar_max_w, row_h * 0.44,
                            fill=b["navy"])
        tr.set_duration(N)
        tr.set_expression("opacity", lambda c: 0.55)
        _add(comp, tr)

        fw = bar_max_w * frac
        seg_w = fw / n_seg
        for j in range(n_seg):
            sg = ShapeClip.rect(x_bar + j * seg_w, y - row_h * 0.22,
                                max(seg_w - 2.0, 1.0), row_h * 0.44, fill=col)
            sg.set_duration(N)
            sg.set_expression("opacity",
                              lambda c, gs_=gs, j_=j: _smooth(
                                  (c.frame - gs_) / max(fill_f, 1) * n_seg - j_))
            _add(comp, sg)

        vtxt = TextClip(f"{vals[i]:,.0f}{unit}", font=b["font"], size=26,
                        color=b["ink"], align="left")
        vtxt.set_duration(N)
        vtxt.set_position(x_bar + fw + 14, y - 14)
        vtxt.set_expression("opacity",
                            lambda c, gs_=gs: _smooth(
                                (c.frame - gs_ - fill_f * 0.72) / max(N * 0.12, 1)))
        _add(comp, vtxt)
    return comp


# ---------- registry + cache ----------
TEMPLATES = {
    "route_map":    ("Peta jalur: reveal rute + pulse dest", _tpl_route_map),
    "stat_counter": ("Angka count-up + progress bar",        _tpl_stat_counter),
    "kinetic_hook": ("Kata besar slide-in per baris",        _tpl_kinetic_hook),
    "bar_compare":  ("Perbandingan batang blocky-fill",      _tpl_bar_compare),
}


def _spec_hash(template, spec, frames, fps):
    raw = json.dumps([template, spec, frames, fps], sort_keys=True,
                     ensure_ascii=False)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def ensure_clip(template, spec, dur_s, fps=FPS_DEFAULT, size=(W_DEFAULT, H_DEFAULT)):
    """Render (atau ambil dari cache) clip motion -> (folder, files, fps).

    Raise MotionError kalau template unknown / render gagal.
    """
    if Composition is None:
        raise MotionError(f"pymotion tidak terinstall: {_IMPORT_ERR}")
    if template not in TEMPLATES:
        raise MotionError(f"template '{template}' tidak ada. pilihan: "
                          f"{', '.join(TEMPLATES)}")
    spec = dict(spec or {})
    frames = max(int(round(float(dur_s) * fps)), 8)
    h = _spec_hash(template, spec, frames, fps)
    out = CACHE_DIR / f"{template}-{h}"
    meta = out / "meta.json"

    if meta.exists():
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
            if m.get("frames") == frames and m.get("fps") == fps:
                files = sorted(out.glob("f*.png"))
                if len(files) >= frames:
                    return out, files, fps
        except Exception:
            pass

    W, H = size
    comp = TEMPLATES[template][1](spec, W, H, frames, fps)
    out.mkdir(parents=True, exist_ok=True)
    try:
        comp.render(str(out / "f%04d.png"), preset="frame_sequence_png")
    except Exception as e:
        raise MotionError(f"render pymotion gagal: {e}")

    files = sorted(out.glob("f*.png"))
    if len(files) < frames:
        raise MotionError(f"frame kurang: {len(files)}/{frames}")
    meta.write_text(json.dumps({"template": template, "spec": spec,
                                "frames": frames, "fps": fps, "hash": h},
                               ensure_ascii=False), encoding="utf-8")
    return out, files, fps


def list_templates():
    return {k: v[0] for k, v in TEMPLATES.items()}


# ---------- CLI ----------
def _cli():
    if len(sys.argv) < 2 or sys.argv[1] in ("list", "-l"):
        print("Template motion tersedia:")
        for k, desc in list_templates().items():
            print(f"  {k:14s} {desc}")
        return 0
    if sys.argv[1] == "render":
        if len(sys.argv) < 3:
            print("pakai: python -m pipeline.motion.clips render <template> "
                  "[--spec JSON] [--dur detik]"); return 1
        tpl = sys.argv[2]
        spec, dur = {}, 6.0
        a = sys.argv[3:]
        for i, x in enumerate(a):
            if x == "--spec" and i + 1 < len(a):
                spec = json.loads(a[i + 1])
            if x == "--dur" and i + 1 < len(a):
                dur = float(a[i + 1])
        folder, files, fps = ensure_clip(tpl, spec, dur)
        print(f"OK {len(files)} frame @ {folder}  (fps={fps})")
        return 0
    print(f"perintah tidak dikenal: {sys.argv[1]}")
    return 1


if __name__ == "__main__":
    sys.exit(_cli())

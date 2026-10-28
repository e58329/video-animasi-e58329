# ============================================================
# scenes/templates/asset_visual.py — Visual dari vektor internet
# ------------------------------------------------------------
# Jembatan antara pipeline/assets.py (fetcher) dan template explainer.
# Dipanggil otomatis untuk visual yang TIDAK ada di registry VISUALS.
#
# Alur: resolve(name, override) -> assets/svg_auto/<slug>.svg
#       -> SVGMobject -> recolor/normalize -> animasi masuk ala channel
#
# Opt-in/opt-out per video via YAML:
#   assets: auto          (default, kalau key hilang dianggap auto)
#   assets: off           (semua visual unknown pakai kartu generic)
# Per-visual override (opsional):
#   asset_overrides:
#     rocket_launch: {provider: iconify, collection: fluent-emoji}
#     periscope:     {provider: wikimedia}
#     gravitasi:     {query: "gravity space", color: "#FFC107"}
# ============================================================
import json
from pathlib import Path

from manim import *

ROOT = Path(__file__).resolve().parent.parent.parent
ASSET_DIR = ROOT / "assets" / "svg_auto"

# gaya channel (sama dengan explainer.py)
PRIMARY = "#1E88E5"
ACCENT = "#FFC107"
BG = "#0F172A"
WHITE = "#FFFFFF"
FONT = "Montserrat"

_OVERRIDES = {}
_FAIL_CACHE = set()          # visual yang sudah terbukti gagal sesi ini


def set_asset_overrides(d):
    global _OVERRIDES
    _OVERRIDES = d or {}


def _assets_enabled():
    return _OVERRIDES.get("__enabled__", True)


def _load_index():
    try:
        with open(ASSET_DIR / "index.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


class AssetError(Exception):
    pass


def _zone(y=-0.7):
    """Zona visual standar template (sama dengan explainer)."""
    return np.array([0.0, y, 0.0])


def _label(txt, color=ACCENT, size=22):
    return Text(txt, font=FONT, font_size=size, color=color)


def _pretty(key):
    return key.replace("_", " ").title()


def _import_svg(path):
    svg = SVGMobject(str(path))
    if svg.width < 0.05 or svg.height < 0.05:
        raise AssetError("bounding box degenerate")
    return svg


def _recolor(svg, multicolor, color):
    if multicolor:
        return svg
    svg.set_fill(color=color, opacity=1.0)
    svg.set_stroke(width=0)
    return svg


def vis_asset(s, dur, key="default"):
    """Pengganti vis_generic untuk visual tanpa fungsi gambar.
    Melempar AssetError kalau aset tidak bisa didapat -> caller
    (explainer) jatuh balik ke vis_generic."""
    spec = dict(_OVERRIDES.get(key) or {})
    spec.setdefault("query", key.replace("_", " "))

    try:
        from pipeline.assets import resolve, AssetError as FetchError
    except Exception as e:
        raise AssetError(f"modul pipeline.assets tidak bisa diimport: {e}")

    try:
        entry = resolve(key, spec)
    except FetchError as e:
        _FAIL_CACHE.add(key)
        raise AssetError(f"fetch gagal: {e}")

    fpath = ROOT / entry["file"]
    if not fpath.exists():
        raise AssetError(f"file cache hilang: {fpath}")

    try:
        svg = _import_svg(fpath)
    except AssetError:
        raise
    except Exception as e:
        _FAIL_CACHE.add(key)
        raise AssetError(f"SVGMobject gagal parse: {e}")

    svg = _recolor(svg, entry.get("multicolor", False),
                   spec.get("color", WHITE))

    # normalisasi ke zona visual: tinggi maks 2.6, lebar maks 5.4
    if svg.width > 5.4:
        svg.scale_to_fit_width(5.4)
    if svg.height > 2.6:
        svg.scale_to_fit_height(2.6)
    if svg.width < 0.05 or svg.height < 0.05:
        raise AssetError("ukuran 0 setelah scaling")
    svg.move_to(_zone(-0.55) + UP * 0.25)

    # kartu latar lembut biar menyatu dengan gaya channel
    card = RoundedRectangle(corner_radius=0.18, width=6.4, height=3.4,
                            color=PRIMARY, stroke_width=3,
                            fill_color=PRIMARY, fill_opacity=0.10)
    card.move_to(svg.get_center())

    # label kecil di bawah kartu (sumber + lisensi biar transparan)
    lbl = _label(_pretty(key), color=ACCENT, size=24)
    lbl.next_to(card, DOWN, buff=0.22)
    if lbl.width > 8.0:
        lbl.set(width=8.0)

    grp = VGroup(card, svg, lbl)

    s.play(Create(card), FadeIn(svg, scale=1.15), Write(lbl), run_time=1.5)
    if dur and dur > 2.0:
        # float halus biar hidup, deterministik
        s.play(svg.animate.shift(UP * 0.12), run_time=min(dur - 1.6, 1.0),
               rate_func=there_and_back)
    return grp

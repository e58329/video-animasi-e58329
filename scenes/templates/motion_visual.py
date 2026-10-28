# ============================================================
# scenes/templates/motion_visual.py — Motion graphics di scene Manim
# ------------------------------------------------------------
# Jembatan antara pipeline/motion/clips.py (pymotion generator) dan
# template explainer. Visual dengan awalan "motion:" di YAML:
#
#   visual: "motion:route_map"     -> peta jalur bergerak
#   visual: "motion:stat_counter"  -> angka naik + progress bar
#   visual: "motion:kinetic_hook"  -> kata-kata besar muncul berurutan
#   visual: "motion:bar_compare"   -> perbandingan batang
#
# Param per-template (opsional) via YAML:
#   motion_overrides:
#     stat_counter:
#       value_to: 3800
#       fmt: "{:,.0f}"
#       suffix: " m"
#       label: "Kedalaman Maksimum"
#
# Clip dirender sekali (cache motion/cache/<template>-<hash>/), lalu
# frame PNG transparan di-swap tiap frame lewat updater ImageMobject.
# Gagal di tahap mana pun -> MotionError -> explainer fallback generic.
# ============================================================
import json
from pathlib import Path

from manim import *

# Catatan: pakai Group (bukan VGroup) karena frame motion = ImageMobject
# (bukan VMobject) — VGroup nolak campuran.

ROOT = Path(__file__).resolve().parent.parent.parent

# gaya channel (sama dengan explainer.py / asset_visual.py)
PRIMARY = "#1E88E5"
ACCENT = "#FFC107"
BG = "#0F172A"
WHITE = "#FFFFFF"
FONT = "Montserrat"

_MOT_OVERRIDES = {}
_FAIL_CACHE = set()          # template yang sudah terbukti gagal sesi ini


def set_motion_overrides(d):
    global _MOT_OVERRIDES
    _MOT_OVERRIDES = d or {}


class MotionError(Exception):
    pass


def _pretty(key):
    return key.replace("_", " ").title()


def vis_motion(s, dur, key="motion:default"):
    """Kartu motion graphics: frame pymotion di-swap via updater.

    Melempar MotionError kalau gagal -> caller (explainer) jatuh ke
    vis_generic, sama polanya dengan vis_asset.
    """
    template = key.split(":", 1)[1] if ":" in key else key
    if template in _FAIL_CACHE:
        raise MotionError(f"'{template}' sudah gagal sebelumnya (sesi ini)")

    spec = dict(_MOT_OVERRIDES.get(template) or {})
    try:
        from pipeline.motion.clips import ensure_clip, MotionError as ME
    except Exception as e:
        _FAIL_CACHE.add(template)
        raise MotionError(f"modul pipeline.motion.clips gagal diimport: {e}")

    try:
        # sisakan 0.7s buat fade-out biar clip berhenti sebelum fade dimulai
        folder, files, fps = ensure_clip(template, spec, max(dur - 0.7, 0.6))
    except ME:
        raise
    except Exception as e:
        _FAIL_CACHE.add(template)
        raise MotionError(f"ensure_clip gagal: {e}")

    # frame pertama -> ImageMobject dasar
    try:
        base = ImageMobject(str(files[0]))
    except Exception as e:
        _FAIL_CACHE.add(template)
        raise MotionError(f"ImageMobject gagal: {e}")

    # normalisasi ke zona visual kartu (lebar maks 4.9, tinggi maks 2.5)
    if base.width > 4.9:
        base.scale_to_fit_width(4.9)
    if base.height > 2.5:
        base.scale_to_fit_height(2.5)
    center = np.array([0.0, -0.55, 0.0]) + UP * 0.25
    base.move_to(center)
    vw = base.width

    # kartu latar + label — gaya identik vis_asset
    card = RoundedRectangle(corner_radius=0.18, width=6.4, height=3.4,
                            color=PRIMARY, stroke_width=3,
                            fill_color=PRIMARY, fill_opacity=0.10)
    card.move_to(base.get_center())
    lbl = Text(_pretty(template), font=FONT, font_size=24, color=ACCENT)
    lbl.next_to(card, DOWN, buff=0.22)
    if lbl.width > 8.0:
        lbl.set(width=8.0)

    # updater swap-frame: akumulasi dt, clamp di frame terakhir (freeze)
    state = {"t": 0.0, "i": -1, "n": len(files)}

    def _tick(m, dt):
        st = state
        st["t"] += dt
        idx = min(int(st["t"] * fps), st["n"] - 1)
        if idx != st["i"]:
            st["i"] = idx
            img = ImageMobject(str(files[idx]))
            img.scale_to_fit_width(vw).move_to(center)
            m.become(img)

    base.add_updater(_tick)

    grp = Group(card, base, lbl)
    s.play(Create(card), FadeIn(base, scale=1.08), Write(lbl), run_time=1.5)
    return grp

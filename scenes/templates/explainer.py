# ============================================================
# scenes/templates/explainer.py — v2 "Cinematic Sync"
# - Timing video proporsional terhadap durasi audio (audio_duration
#   di-inject studio.py) → video selalu sedikit LEBIH PANJANG dari
#   audio, jadi merge `-shortest` tidak pernah memotong narasi.
# - Poin format lama (string) & baru (dict dengan "visual") sama
#  -sama didukung.
# - Tanpa LaTeX. Font Montserrat (fallback otomatis kalau belum
#   ter-install di sistem).
# ============================================================
from manim import *
import numpy as np
from scenes.base_scene import BaseScene

# ---------- BRAND ----------
PRIMARY = "#1E88E5"
ACCENT  = "#FFC107"
BG      = "#0F172A"
WATER   = "#42A5F5"
DANGER  = "#EF5350"
GREEN   = "#66BB6A"
GREY    = "#90A4AE"
WHITE   = "#FFFFFF"
FONT    = "Montserrat"

# ---------- TIMING ----------
PACE_FALLBACK = 0.46   # detik per kata (konservatif)
FIXED_HEAD    = 5.4    # intro + kartu judul
FIXED_TAIL    = 5.0    # outro
FADE_T        = 0.7

def _T(txt, size=28, color=WHITE, bold=False):
    return Text(txt, font=FONT, font_size=size, color=color,
                weight=("BOLD" if bold else "NORMAL"))

def _wrap(txt, max_chars=56, max_lines=2):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return lines

def _bullet(txt, size=24, max_chars=56, max_lines=2):
    lines = _wrap(txt, max_chars, max_lines)
    g = VGroup(*[_T(l, size=size, color=WHITE) for l in lines]).arrange(DOWN, buff=0.16)
    if g.width > 11.6:
        g.set_width(11.6)
    return g

def _label(txt, color=ACCENT, size=22, bold=True):
    return _T(txt, size=size, color=color, bold=bold)

# ---------- BUILDER DASAR ----------
def _stickman(scale=1.0, color=WHITE, pose="stand"):
    head = Circle(radius=0.26, color=color, stroke_width=5)
    body = Line(ORIGIN, DOWN * 0.8, color=color, stroke_width=5)
    a_l = Line(ORIGIN, DL * 0.5, color=color, stroke_width=5)
    a_r = Line(ORIGIN, DR * 0.5, color=color, stroke_width=5)
    l_l = Line(body.get_end(), body.get_end() + DL * 0.55, color=color, stroke_width=5)
    l_r = Line(body.get_end(), body.get_end() + DR * 0.55, color=color, stroke_width=5)
    head.next_to(body.get_start(), UP, buff=0.05)
    g = VGroup(head, body, a_l, a_r, l_l, l_r)
    if pose == "point":
        a_r.set_points_as_corners([ORIGIN, RIGHT * 0.7])
    elif pose == "up":
        a_l.set_points_as_corners([ORIGIN, UL * 0.65])
        a_r.set_points_as_corners([ORIGIN, UR * 0.65])
    g.scale(scale)
    return g

def _submarine(scale=1.0, color=PRIMARY, alpha=1.0):
    hull = Ellipse(width=4.6, height=1.4, color=color,
                   fill_color=color, fill_opacity=alpha, stroke_width=3)
    sail = RoundedRectangle(corner_radius=0.1, width=1.15, height=0.7,
                            color=color, fill_color=color, fill_opacity=alpha)
    sail.move_to(hull.get_center() + UP * 0.88 + LEFT * 0.3)
    peri_v = Line(sail.get_top(), sail.get_top() + UP * 0.45, color=ACCENT, stroke_width=5)
    peri_h = Line(peri_v.get_end(), peri_v.get_end() + RIGHT * 0.38, color=ACCENT, stroke_width=5)
    wins = VGroup(*[Dot(radius=0.08, color=WHITE).move_to(
        hull.get_center() + UP * 0.16 + RIGHT * dx) for dx in (-1.1, -0.55, 0.0)])
    pf = Polygon([-0.3, 0, 0], [0.3, 0, 0], [0, -0.28, 0],
                 color=ACCENT, fill_color=ACCENT, fill_opacity=1)
    pf.move_to(hull.get_center() + RIGHT * 1.45 + UP * 0.32)
    pb = pf.copy().move_to(hull.get_center() + LEFT * 1.45 + UP * 0.32)
    prop = VGroup(
        RoundedRectangle(corner_radius=0.04, width=0.1, height=0.62, color=ACCENT,
                         fill_color=ACCENT, fill_opacity=1),
        RoundedRectangle(corner_radius=0.04, width=0.62, height=0.1, color=ACCENT,
                         fill_color=ACCENT, fill_opacity=1))
    prop.move_to(hull.get_center() + LEFT * 2.4)
    allp = VGroup(hull, sail, VGroup(peri_v, peri_h), wins, pf, pb, prop)
    allp.scale(scale)
    return {"all": allp, "hull": hull, "sail": sail, "peri": VGroup(peri_v, peri_h),
            "prop": prop, "planes": VGroup(pf, pb), "windows": wins}

def _sea(y=-1.4, op=0.16):
    rect = Rectangle(width=22, height=9, color=WATER,
                     fill_color=WATER, fill_opacity=op, stroke_width=0)
    rect.move_to([0, y - 4.5, 0])
    return rect

def _bubble(pos, r=0.07, color=WHITE):
    return Circle(radius=r, color=color, stroke_width=2,
                  fill_color=color, fill_opacity=0.25).move_to(pos)

def _gauge(pos=ORIGIN, radius=1.0):
    ring = Circle(radius=radius, color=WHITE, stroke_width=4)
    ticks = VGroup(*[Line(
        (radius - 0.13) * np.array([np.cos(a), np.sin(a), 0]),
        (radius - 0.03) * np.array([np.cos(a), np.sin(a), 0]),
        color=GREY, stroke_width=3)
        for a in [PI * 0.75 + i * PI * 1.5 / 8 for i in range(9)]])
    needle = Line(ORIGIN, RIGHT * (radius - 0.22), color=DANGER, stroke_width=5)
    needle.rotate(PI * 0.75, about_point=ORIGIN).shift(ring.get_center())
    hub = Dot(radius=0.06, color=WHITE).move_to(ring.get_center())
    ttl = _T("TEKANAN", size=18, color=ACCENT, bold=True).next_to(ring, DOWN, buff=0.16)
    grp = VGroup(ring, ticks, needle, hub, ttl).move_to(pos)
    return {"grp": grp, "needle": needle, "ring": ring}

def _arrow_updown(start, length, color, txt=None, up=True):
    d = UP if up else DOWN
    arr = Arrow(start, start + d * length, buff=0.04, color=color,
                stroke_width=6, max_tip_length_to_length_ratio=0.3)
    g = VGroup(arr)
    if txt:
        g.add(_T(txt, size=24, color=color, bold=True).next_to(arr.get_end(), d, buff=0.08))
    return g

# ---------- VISUAL: FUNGSI-FUNGSI ----------
# Semua fungsi visual: def vis_xxx(s, dur) -> VGroup
# Posisi standar zona visual: pusat y = -0.85

VIS_Y = -0.85

def _zone(yoff=0.0, xoff=0.0):
    return np.array([xoff, VIS_Y + yoff, 0])

def vis_history_ancient(s, dur):
    water = _sea(y=1.1, op=0.25)
    bell = Arc(radius=1.15, start_angle=0, angle=PI, color=WATER,
               stroke_width=6).move_to(_zone(0.35))
    rope = Line(bell.get_top(), bell.get_top() + UP * 1.0, color=GREY, stroke_width=4)
    man = _stickman(0.75).move_to(bell.get_bottom() + UP * 0.75)
    lbl = _label("Lonceng Kaca Kuno").next_to(bell, DOWN, buff=0.25)
    grp = VGroup(water, bell, rope, man, lbl)
    s.play(Create(water), FadeIn(bell), FadeIn(man), Write(rope), Write(lbl), run_time=1.6)
    return grp

def vis_history_wood(s, dur):
    hull = Polygon([-1.7, 0, 0], [1.7, 0, 0], [1.2, -0.9, 0], [-1.2, -0.9, 0],
                   color="#8D6E63", fill_color="#8D6E63", fill_opacity=0.85,
                   stroke_width=3).move_to(_zone(0.3))
    dome = Arc(radius=1.0, start_angle=0, angle=PI, color="#8D6E63",
               stroke_width=6, fill_color="#8D6E63", fill_opacity=0.85).move_to(hull.get_top())
    win = Circle(radius=0.14, color=ACCENT, stroke_width=3).move_to(dome.get_center() + UP * 0.25)
    oar = Line(DOWN * 0.2, DOWN * 0.9, color=GREY, stroke_width=5).move_to(
        hull.get_center() + RIGHT * 0.6 + DOWN * 0.1)
    lbl = _label("Drebbel, 1620 — Kayu & Kulit").next_to(hull, DOWN, buff=0.3)
    grp = VGroup(hull, dome, win, oar, lbl)
    s.play(DrawBorderThenFill(hull), FadeIn(dome), FadeIn(win), Create(oar), Write(lbl), run_time=1.8)
    return grp

def vis_history_turtle(s, dur):
    egg = Ellipse(width=1.5, height=1.9, color=GREY, fill_color=GREY,
                  fill_opacity=0.8, stroke_width=3).move_to(_zone(0.1))
    screw = Line(egg.get_top() + UP * 0.1, egg.get_top() + UP * 0.7, color=ACCENT, stroke_width=5)
    screw_lbl = _T("sekrup", size=18, color=GREY).next_to(screw, RIGHT, buff=0.12)
    hole = Circle(radius=0.12, color=ACCENT, stroke_width=3).move_to(egg.get_center())
    lbl = _label("Turtle, 1776 — 1 Awak").next_to(egg, DOWN, buff=0.35)
    grp = VGroup(egg, screw, screw_lbl, hole, lbl)
    s.play(DrawBorderThenFill(egg), Create(screw), Write(screw_lbl), FadeIn(hole), Write(lbl), run_time=1.8)
    s.play(Rotate(screw, angle=PI * 2), run_time=0.9)
    return grp

def vis_history_war(s, dur):
    sea = _sea(y=1.3, op=0.3)
    sub = _submarine(0.85)
    sub["all"].move_to(_zone(0.2))
    flag = Polygon([0, 0, 0], [0.55, 0.1, 0], [0, 0.2, 0], color=DANGER,
                   fill_color=DANGER, fill_opacity=1).next_to(sub["sail"], UP, buff=0.1)
    lbl = _label("U-boat — Pemburu Tak Terlihat").next_to(sub["all"], DOWN, buff=0.35)
    grp = VGroup(sea, sub["all"], flag, lbl)
    s.play(FadeIn(sea), FadeIn(sub["all"], shift=RIGHT * 1.2), FadeIn(flag), Write(lbl), run_time=1.8)
    return grp

def vis_history_wolfpack(s, dur):
    subs = VGroup()
    for i, (x, y, sc) in enumerate([(-3.2, 0.6, 0.6), (0.4, -0.3, 0.6), (3.2, 0.7, 0.6)]):
        su = _submarine(sc)
        su["all"].move_to(_zone(0.1) + RIGHT * x + UP * y)
        subs.add(su["all"])
    lbl = _label("Wolfpack — Berburu Berkelompok").next_to(subs, DOWN, buff=0.4)
    grp = VGroup(subs, lbl)
    s.play(LaggedStart(*[FadeIn(m, shift=RIGHT) for m in subs], lag_ratio=0.25), Write(lbl), run_time=2.2)
    return grp

def vis_history_nuclear(s, dur):
    sub = _submarine(0.85)
    sub["all"].move_to(_zone(-0.3))
    atom = VGroup(Circle(radius=0.32, color=GREEN, stroke_width=4),
                  Ellipse(width=0.95, height=0.38, color=GREEN, stroke_width=3),
                  Ellipse(width=0.95, height=0.38, color=GREEN, stroke_width=3).rotate(60 * DEGREES),
                  Ellipse(width=0.95, height=0.38, color=GREEN, stroke_width=3).rotate(120 * DEGREES))
    atom.move_to(_zone(1.35))
    lbl = _label("USS Nautilus, 1954 — Reaktor Nuklir", color=GREEN).move_to(_zone(1.35) + UP * 0.55)
    grp = VGroup(sub["all"], atom, lbl)
    s.play(FadeIn(sub["all"], shift=RIGHT * 0.8), FadeIn(atom, scale=1.4), Write(lbl), run_time=1.9)
    s.play(Rotate(atom, angle=PI * 2), run_time=0.8)
    return grp

def _tank_blk(pos, w=3.4, h=2.1, frac=0.62):
    tank = Rectangle(width=w, height=h, color=GREY, stroke_width=4).move_to(pos)
    water = Rectangle(width=w - 0.14, height=h * frac - 0.07, color=WATER,
                      fill_color=WATER, fill_opacity=0.4, stroke_width=0)
    water.move_to(tank.get_bottom() + UP * (h * frac / 2))
    return VGroup(tank, water), tank

def vis_archimedes_question(s, dur):
    grp_t, tank = _tank_blk(_zone(-0.2))
    blk = Square(side_length=0.62, color=ACCENT, fill_color=ACCENT,
                 fill_opacity=1, stroke_width=2).move_to(tank.get_top() + UP * 0.55)
    q = _T("?", size=72, color=ACCENT, bold=True).next_to(blk, UP, buff=0.2)
    grp = VGroup(grp_t, blk, q)
    s.play(Create(grp_t), FadeIn(blk), run_time=1.2)
    s.play(blk.animate.move_to(tank.get_center()), FadeIn(q, scale=1.6), run_time=1.0)
    return grp

def vis_archimedes_law(s, dur):
    grp_t, tank = _tank_blk(_zone(-0.2))
    blk = Square(side_length=0.62, color=ACCENT, fill_color=ACCENT,
                 fill_opacity=1, stroke_width=2).move_to(tank.get_center())
    fb = _arrow_updown(tank.get_center() + RIGHT * 1.15, 1.1, GREEN, "F naik", up=True)
    wgt = _arrow_updown(tank.get_center() - RIGHT * 1.15, 1.1, DANGER, "W berat", up=False)
    lbl = _label("Gaya dorong = berat air yang dipindahkan", color=WHITE, size=22, bold=False)
    lbl.next_to(tank, DOWN, buff=0.25)
    grp = VGroup(grp_t, blk, fb, wgt, lbl)
    s.play(Create(grp_t), FadeIn(blk), run_time=1.1)
    s.play(GrowArrow(fb[0]), GrowArrow(wgt[0]), FadeIn(fb[1]), FadeIn(wgt[1]), Write(lbl), run_time=1.4)
    return grp

def vis_archimedes_float(s, dur):
    g1, t1 = _tank_blk(_zone(-0.05) + LEFT * 2.6, w=2.5, h=1.8)
    blk1 = Square(side_length=0.5, color=ACCENT, fill_color=ACCENT,
                  fill_opacity=1).move_to(t1.get_top() + UP * 0.24)
    l1 = _label("APUNG", color=GREEN).next_to(t1, DOWN, buff=0.2)
    g2, t2 = _tank_blk(_zone(-0.05) + RIGHT * 2.6, w=2.5, h=1.8)
    blk2 = blk1.copy().move_to(t2.get_bottom() + UP * 0.35)
    l2 = _label("TENGGELAM", color=DANGER).next_to(t2, DOWN, buff=0.2)
    grp = VGroup(g1, blk1, l1, g2, blk2, l2)
    s.play(FadeIn(g1), FadeIn(blk1), Write(l1), run_time=1.0)
    s.play(FadeIn(g2), FadeIn(blk2), Write(l2), run_time=1.0)
    s.play(blk1.animate.shift(UP * 0.12), run_time=0.6)
    return grp

def _cutaway_sub(pos, alpha=0.14, tanks=False):
    parts = _submarine(1.5, alpha=alpha)
    parts["all"].move_to(pos)
    inner = Ellipse(width=3.6, height=0.95, color=WHITE, stroke_width=3)
    inner.move_to(parts["hull"].get_center())
    return parts, inner

def vis_anatomy_hull(s, dur):
    parts, inner = _cutaway_sub(_zone(0.0))
    lbl_out = _label("Lambung luar", color=PRIMARY, size=20).next_to(parts["hull"], UP, buff=0.55)
    lbl_out.move_to(_zone(1.35))
    lbl_in = _label("Pressure hull (dalam)", color=ACCENT, size=20).next_to(inner, DOWN, buff=0.3)
    grp = VGroup(parts["all"], inner, lbl_out, lbl_in)
    s.play(Create(parts["all"]), run_time=1.1)
    s.play(Create(inner), Write(lbl_in), FadeIn(lbl_out), run_time=1.3)
    return grp

def vis_anatomy_ballast(s, dur):
    parts, inner = _cutaway_sub(_zone(0.0))
    tk_l = RoundedRectangle(corner_radius=0.09, width=1.0, height=0.5,
                            color=ACCENT, stroke_width=3).move_to(parts["hull"].get_center() + LEFT * 1.1 + DOWN * 0.32)
    tk_r = tk_l.copy().move_to(parts["hull"].get_center() + RIGHT * 1.1 + DOWN * 0.32)
    lbl = _label("Ballast tanks", color=ACCENT).next_to(parts["hull"], DOWN, buff=0.3)
    grp = VGroup(parts["all"], inner, tk_l, tk_r, lbl)
    s.play(Create(parts["all"]), Create(inner), run_time=1.1)
    s.play(FadeIn(tk_l, scale=1.5), FadeIn(tk_r, scale=1.5), Write(lbl), run_time=1.2)
    s.play(Indicate(VGroup(tk_l, tk_r), color=ACCENT), run_time=0.8)
    return grp

def vis_anatomy_rooms(s, dur):
    parts, inner = _cutaway_sub(_zone(0.1))
    seps = VGroup(*[Line(inner.get_top() + DOWN * 0.05 + UP * 0.05,
                         inner.get_bottom() + UP * 0.05, color=GREY, stroke_width=3).move_to(
        inner.get_center() + RIGHT * dx) for dx in (-1.2, 0.0, 1.2)])
    men = VGroup(*[_stickman(0.42).move_to(inner.get_center() + RIGHT * dx + UP * 0.02)
                   for dx in (-1.85, -0.6, 0.6, 1.85)])
    lbl = _label("Mesin • Torpedo • Dapur • Kamar Tidur", size=20, color=WHITE, bold=False)
    lbl.next_to(inner, DOWN, buff=0.3)
    grp = VGroup(parts["all"], inner, seps, men, lbl)
    s.play(Create(parts["all"]), Create(inner), run_time=1.0)
    s.play(Create(seps), LaggedStart(*[FadeIn(m, scale=0.7) for m in men], lag_ratio=0.15),
           Write(lbl), run_time=1.5)
    return grp

def _ballast_system(pos, fill=0.0):
    """Kapal potongan + 2 tangki + tracker level air."""
    parts, inner = _cutaway_sub(pos)
    tk_l = RoundedRectangle(corner_radius=0.09, width=1.05, height=0.52,
                            color=GREY, stroke_width=3).move_to(parts["hull"].get_center() + LEFT * 1.12 + DOWN * 0.33)
    tk_r = tk_l.copy().move_to(parts["hull"].get_center() + RIGHT * 1.12 + DOWN * 0.33)
    tracker = ValueTracker(fill)
    def _w(tk):
        w, hmax = tk.width - 0.12, tk.height - 0.12
        return always_redraw(lambda: Rectangle(
            width=w, height=max(tracker.get_value() * hmax, 0.002),
            color=WATER, fill_color=WATER, fill_opacity=0.8, stroke_width=0
        ).move_to(tk.get_bottom() + UP * (tracker.get_value() * hmax / 2 + 0.002)))
    grp = VGroup(parts["all"], inner, tk_l, tk_r, _w(tk_l), _w(tk_r))
    return grp, tracker, VGroup(tk_l, tk_r)

def vis_ballast_tank(s, dur):
    sea = _sea(y=1.55, op=0.25)
    sysg, tr, tks = _ballast_system(_zone(0.15))
    lbl = _label("Tangki penuh UDARA → kapal mengapung", color=ACCENT, size=22, bold=False)
    lbl.next_to(sysg, DOWN, buff=0.28)
    grp = VGroup(sea, sysg, lbl)
    s.play(FadeIn(sea), Create(sysg), Write(lbl), run_time=1.6)
    return grp

def vis_ballast_water_in(s, dur):
    sysg, tr, tks = _ballast_system(_zone(0.1))
    valve_l = Rectangle(width=0.16, height=0.16, color=DANGER, stroke_width=2).move_to(
        tks[0].get_bottom() + DOWN * 0.1)
    out_a = Arrow(tks[0].get_top() + UP * 0.15, tks[0].get_top() + UP * 0.95,
                  color=ACCENT, stroke_width=5)
    out_l = _T("udara keluar", size=18, color=ACCENT).next_to(out_a.get_end(), UP, buff=0.08)
    in_a = Arrow(tks[1].get_bottom() + DOWN * 0.9, tks[1].get_bottom() + DOWN * 0.14,
                 color=WATER, stroke_width=5)
    in_l = _T("air laut masuk", size=18, color=WATER).next_to(in_a.get_start(), DOWN, buff=0.08)
    grp = VGroup(sysg, valve_l, out_a, out_l, in_a, in_l)
    s.play(Create(sysg), run_time=1.1)
    s.play(FadeIn(valve_l), GrowArrow(out_a), FadeIn(out_l),
           GrowArrow(in_a), FadeIn(in_l), run_time=1.0)
    s.play(tr.animate.set_value(1.0), run_time=1.6)
    return grp

def vis_ballast_sinking(s, dur):
    sub = _submarine(1.1)
    sub["all"].move_to(_zone(0.9)).rotate(-12 * DEGREES)
    darr = Arrow(sub["all"].get_center() + DOWN * 0.8, sub["all"].get_center() + DOWN * 2.6,
                 color=DANGER, stroke_width=6)
    dl = _label("TENGGELAM", color=DANGER).next_to(darr.get_end(), DOWN, buff=0.12)
    bub = VGroup(*[_bubble(sub["all"].get_center() + UP * 0.9 + RIGHT * dx, r=0.06 + 0.02 * (i % 2))
                   for i, dx in enumerate((-0.7, 0.0, 0.7))])
    lbl = _label("Berat > gaya dorong", color=WHITE, size=20, bold=False).next_to(dl, DOWN, buff=0.15)
    grp = VGroup(sub["all"], darr, dl, bub, lbl)
    s.play(FadeIn(sub["all"]), GrowArrow(darr), FadeIn(dl), Write(lbl), run_time=1.4)
    s.play(LaggedStart(*[b.animate.shift(UP * 0.8 + RIGHT * 0.2) for b in bub], lag_ratio=0.2),
           run_time=0.9)
    return grp

def vis_ballast_air_in(s, dur):
    sysg, tr, tks = _ballast_system(_zone(0.1), fill=1.0)
    in_a1 = Arrow(tks[0].get_top() + UP * 1.0, tks[0].get_top() + UP * 0.18,
                  color=WHITE, stroke_width=5)
    in_a2 = in_a1.copy().move_to(tks[1].get_top() + UP * 0.59)
    inl = _T("udara bertekanan tinggi", size=18, color=WHITE).next_to(in_a1.get_end(), UP, buff=0.1)
    outl = _T("air terdorong keluar", size=18, color=WATER).next_to(sysg, DOWN, buff=0.26)
    grp = VGroup(sysg, in_a1, in_a2, inl, outl)
    s.play(Create(sysg), run_time=1.0)
    s.play(GrowArrow(in_a1), GrowArrow(in_a2), FadeIn(inl), Write(outl), run_time=1.1)
    s.play(tr.animate.set_value(0.05), run_time=1.5)
    return grp

def vis_ballast_rise(s, dur):
    sea = _sea(y=1.7, op=0.25)
    sub = _submarine(1.0)
    sub["all"].move_to(_zone(-1.1))
    bub = VGroup(*[_bubble(sub["all"].get_center() + DL * 0.9, r=0.07),
                   _bubble(sub["all"].get_center() + DR * 1.1, r=0.05)])
    lbl = _label("Gaya dorong > berat → kapal naik", color=GREEN, size=22, bold=False)
    lbl.move_to(_zone(1.05))
    grp = VGroup(sea, sub["all"], bub, lbl)
    s.play(FadeIn(sea), FadeIn(sub["all"]), FadeIn(bub), Write(lbl), run_time=1.2)
    s.play(sub["all"].animate.move_to(_zone(1.15)),
           LaggedStart(*[b.animate.shift(UP * 2.2) for b in bub], lag_ratio=0.3), run_time=1.8)
    return grp

def vis_trim_tank(s, dur):
    flat = _submarine(0.95)
    flat["all"].move_to(_zone(0.85) + LEFT * 0.4)
    tilt = _submarine(0.95)
    tilt["all"].move_to(_zone(-0.9) + LEFT * 0.4).rotate(-14 * DEGREES)
    fa = Arrow(ORIGIN, RIGHT * 0.9, color=GREEN, stroke_width=5).next_to(tilt["all"].get_right(), RIGHT, buff=0.15)
    fa2 = Arrow(ORIGIN, LEFT * 0.9, color=GREEN, stroke_width=5).next_to(tilt["all"].get_left(), LEFT, buff=0.15)
    lbl = _label("Tangki trim: pindahkan air → atur kemiringan", color=ACCENT, size=21, bold=False)
    lbl.move_to(_zone(-1.75))
    grp = VGroup(flat["all"], tilt["all"], fa, fa2, lbl)
    s.play(FadeIn(flat["all"]), Write(lbl), run_time=1.2)
    s.play(FadeIn(tilt["all"], shift=DOWN * 0.4), GrowArrow(fa), GrowArrow(fa2), run_time=1.2)
    return grp

def vis_dive_planes(s, dur):
    sub = _submarine(1.05)
    sub["all"].move_to(_zone(0.2))
    hi = VGroup(*sub["planes"]).copy().set_color(YELLOW).scale(1.25)
    ra = Arc(radius=0.5, start_angle=-PI / 2, angle=PI, color=ACCENT,
             stroke_width=4).move_to(sub["planes"][0].get_center() + UP * 0.45)
    lbl = _label("Hydroplanes — sayap pengatur kedalaman", color=ACCENT, size=21, bold=False)
    lbl.next_to(sub["all"], DOWN, buff=0.35)
    grp = VGroup(sub["all"], hi, ra, lbl)
    s.play(Create(sub["all"]), Write(lbl), run_time=1.3)
    s.play(FadeIn(hi, scale=1.2), Create(ra), sub["planes"][0].animate.rotate(18 * DEGREES),
           sub["planes"][1].animate.rotate(-18 * DEGREES), run_time=1.2)
    return grp

def vis_depth_control(s, dur):
    sub = _submarine(0.9)
    sub["all"].move_to(_zone(0.0))
    a_up = Arrow(sub["all"].get_center(), sub["all"].get_center() + UP * 1.3, color=GREEN, stroke_width=5)
    a_dn = Arrow(sub["all"].get_center(), sub["all"].get_center() + DOWN * 1.3, color=DANGER, stroke_width=5)
    a_lf = Arrow(sub["all"].get_center(), sub["all"].get_center() + LEFT * 1.6, color=ACCENT, stroke_width=5)
    a_rt = Arrow(sub["all"].get_center(), sub["all"].get_center() + RIGHT * 1.6, color=ACCENT, stroke_width=5)
    lu = _T("naik", size=18, color=GREEN).next_to(a_up.get_end(), UP, buff=0.06)
    ld = _T("turun", size=18, color=DANGER).next_to(a_dn.get_end(), DOWN, buff=0.06)
    grp = VGroup(sub["all"], a_up, a_dn, a_lf, a_rt, lu, ld)
    s.play(FadeIn(sub["all"]), run_time=0.8)
    s.play(GrowArrow(a_up), GrowArrow(a_dn), GrowArrow(a_lf), GrowArrow(a_rt),
           FadeIn(lu), FadeIn(ld), run_time=1.3)
    s.play(sub["all"].animate.shift(UP * 0.5), run_time=0.7)
    return grp

def vis_dive_controlled(s, dur):
    path = ParametricFunction(
        lambda t: np.array([-5.5 + t * 11.0, 1.7 - 2.6 * (t ** 2), 0]),
        t_range=[0, 1, 0.02], color=GREY, stroke_width=3)
    sub = _submarine(0.75)
    sub["all"].move_to(path.get_start())
    lbl = _label("Menukik terkendali", color=ACCENT, size=21, bold=False)
    lbl.next_to(path.get_end(), DOWN, buff=0.3)
    grp = VGroup(path, sub["all"], lbl)
    s.play(Create(path), Write(lbl), run_time=1.2)
    s.play(MoveAlongPath(sub["all"], path, rate_func=linear), run_time=1.6)
    return grp

def vis_pressure_depth(s, dur):
    g = _gauge(_zone(-0.3) + LEFT * 3.1, radius=0.95)
    marks = VGroup()
    for i, (d, col) in enumerate([("10 m — 2 atm", ACCENT), ("100 m — 11 atm", "#FFA726"),
                                  ("500 m — 51 atm", DANGER)]):
        bar = Rectangle(width=0.4 * (i + 2), height=0.3, color=col,
                        fill_color=col, fill_opacity=0.9, stroke_width=0)
        bar.move_to(_zone(1.0 - i * 0.95) + RIGHT * 1.6)
        lb = _T(d, size=20, color=col, bold=True).next_to(bar, RIGHT, buff=0.15)
        marks.add(VGroup(bar, lb))
    grp = VGroup(g["grp"], marks)
    s.play(FadeIn(g["grp"]), run_time=0.8)
    s.play(LaggedStart(*[FadeIn(m, shift=RIGHT) for m in marks], lag_ratio=0.3), run_time=1.5)
    s.play(Rotate(g["needle"], angle=1.5, about_point=g["ring"].get_center()), run_time=1.0)
    return grp

def vis_pressure_hull(s, dur):
    ring_out = Ellipse(width=4.6, height=2.4, color=PRIMARY, stroke_width=6).move_to(_zone(0.0))
    ring_in = ring_out.copy().scale(0.82).set_stroke(color=WHITE, width=3)
    cw, chh = 4.6 / 2, 2.4 / 2
    arrows = VGroup(*[Arrow(
        ring_out.get_center() + np.array([np.cos(a) * cw, np.sin(a) * chh, 0]) * 1.28,
        ring_out.get_center() + np.array([np.cos(a) * cw, np.sin(a) * chh, 0]) * 1.04,
        color=WATER, stroke_width=4, buff=0.02)
        for a in np.linspace(0, 2 * PI, 10, endpoint=False)])
    lbl = _label("Tekanan terdistribusi merata", color=ACCENT, size=21, bold=False)
    lbl.move_to(_zone(-1.7))
    grp = VGroup(ring_out, ring_in, arrows, lbl)
    s.play(Create(ring_out), Create(ring_in), Write(lbl), run_time=1.3)
    s.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1), run_time=1.2)
    return grp

def vis_crush_depth(s, dur):
    hull = Ellipse(width=4.2, height=2.0, color=PRIMARY, stroke_width=6,
                   fill_color=PRIMARY, fill_opacity=0.15).move_to(_zone(0.1))
    warn = _label("CRUSH DEPTH!", color=DANGER, size=30).move_to(_zone(1.5))
    cracks = VGroup(*[Line(ORIGIN, DOWN * 0.5 + RIGHT * 0.12, color=DANGER, stroke_width=3).move_to(
        hull.get_bottom() + UP * 0.3 + RIGHT * dx) for dx in (-1.0, 0.0, 1.0)])
    lbl = _label("Denting logam… lalu runtuh", color=GREY, size=20, bold=False)
    lbl.move_to(_zone(-1.6))
    grp = VGroup(hull, warn, cracks, lbl)
    s.play(Create(hull), FadeIn(warn, scale=1.6), Write(lbl), run_time=1.4)
    s.play(Create(cracks), hull.animate.scale([1.0, 0.85, 1.0]), run_time=1.1)
    return grp

def vis_diesel_engine(s, dur):
    eng = RoundedRectangle(corner_radius=0.12, width=1.7, height=1.2, color=GREY,
                           stroke_width=4).move_to(_zone(0.2) + LEFT * 2.9)
    eng_l = _T("DIESEL", size=18, color=WHITE, bold=True).move_to(eng)
    bat = RoundedRectangle(corner_radius=0.1, width=1.5, height=0.9, color=GREEN,
                           stroke_width=4).move_to(_zone(0.2) + RIGHT * 2.9)
    bat_l = _T("BATERAI", size=16, color=GREEN, bold=True).move_to(bat)
    bolt = _T("CHARGE", size=14, color=ACCENT, bold=True).next_to(bat, UP, buff=0.1)
    ex_a = Arrow(eng.get_top(), eng.get_top() + UP * 1.0, color=GREY, stroke_width=4)
    ex_l = _T("knalpot + snorkel", size=17, color=GREY).next_to(ex_a.get_end(), UP, buff=0.06)
    ca = Arrow(eng.get_right(), bat.get_left(), color=GREEN, stroke_width=5)
    grp = VGroup(eng, eng_l, bat, bat_l, bolt, ex_a, ex_l, ca)
    s.play(FadeIn(eng), FadeIn(eng_l), FadeIn(bat), FadeIn(bat_l), run_time=1.0)
    s.play(GrowArrow(ex_a), FadeIn(ex_l), GrowArrow(ca), FadeIn(bolt), run_time=1.2)
    return grp

def vis_nuclear_engine(s, dur):
    rct = Circle(radius=0.55, color=GREEN, stroke_width=5).move_to(_zone(0.2) + LEFT * 3.3)
    rct_l = _T("REAKTOR", size=15, color=GREEN, bold=True).next_to(rct, DOWN, buff=0.12)
    trb = RoundedRectangle(corner_radius=0.1, width=1.1, height=0.8, color=ACCENT,
                           stroke_width=4).move_to(_zone(0.2))
    trb_l = _T("TURBIN", size=15, color=ACCENT, bold=True).next_to(trb, DOWN, buff=0.12)
    sub = _submarine(0.55)
    sub["all"].move_to(_zone(0.2) + RIGHT * 3.1)
    a1 = Arrow(rct.get_right(), trb.get_left(), color=WHITE, stroke_width=4)
    a2 = Arrow(trb.get_right(), sub["all"].get_left() + LEFT * 0.1, color=WHITE, stroke_width=4)
    steam = VGroup(*[_bubble(rct.get_top() + UP * 0.3 + RIGHT * dx * 0.5, r=0.08, color=WHITE)
                     for dx in (-1, 0, 1)])
    grp = VGroup(rct, rct_l, trb, trb_l, sub["all"], a1, a2, steam)
    s.play(FadeIn(rct), FadeIn(rct_l), FadeIn(trb), FadeIn(trb_l), FadeIn(sub["all"]), run_time=1.1)
    s.play(GrowArrow(a1), GrowArrow(a2), run_time=0.8)
    s.play(LaggedStart(*[b.animate.shift(UP * 0.9) for b in steam], lag_ratio=0.2),
           Rotate(sub["prop"], angle=2 * PI), run_time=1.0)
    return grp

def vis_silent_running(s, dur):
    sub = _submarine(1.0)
    sub["all"].move_to(_zone(0.1))
    waves = VGroup(*[Arc(radius=r, start_angle=-PI / 3, angle=2 * PI / 3, color=GREY,
                         stroke_width=3).move_to(sub["all"].get_right() + RIGHT * 0.3)
                     for r in (0.35, 0.6, 0.85)])
    cross = Line(waves[2].get_corner(UL), waves[2].get_corner(DR), color=DANGER, stroke_width=6)
    lbl = _label("MODE SENYAP", color=GREEN, size=26).move_to(_zone(1.45))
    sub_l = _label("Mesin lambat • Getaran diredam", color=WHITE, size=19, bold=False)
    sub_l.move_to(_zone(-1.55))
    grp = VGroup(sub["all"], waves, cross, lbl, sub_l)
    s.play(FadeIn(sub["all"]), Write(lbl), FadeIn(sub_l), run_time=1.2)
    s.play(Create(waves), run_time=0.8)
    s.play(Create(cross), waves.animate.set_opacity(0.25), run_time=0.9)
    return grp

def vis_periscope(s, dur):
    frame = RoundedRectangle(corner_radius=0.1, width=3.6, height=2.1, color=GREY,
                             stroke_width=4).move_to(_zone(0.0) + LEFT * 0.6)
    cv = Line(frame.get_top() + DOWN * 0.12, frame.get_bottom() + UP * 0.12, color=GREY, stroke_width=2)
    ch = Line(frame.get_left() + RIGHT * 0.12, frame.get_right() + LEFT * 0.12, color=GREY, stroke_width=2)
    ship = _submarine(0.42)
    ship["all"].move_to(frame.get_center() + RIGHT * 0.5)
    alert = _label("KAPAL MUSUH", color=DANGER, size=18).move_to(frame.get_top() + DOWN * 0.3)
    pipe = VGroup(Line(_zone(2.0) + RIGHT * 3.0, _zone(0.0) + RIGHT * 3.0, color=ACCENT, stroke_width=6),
                  Line(_zone(2.0) + RIGHT * 3.0, _zone(2.0) + RIGHT * 3.6, color=ACCENT, stroke_width=6))
    grp = VGroup(frame, cv, ch, ship["all"], alert, pipe)
    s.play(Create(frame), Create(cv), Create(ch), Create(pipe), run_time=1.2)
    s.play(FadeIn(ship["all"], shift=RIGHT * 0.5), FadeIn(alert), run_time=0.9)
    return grp

def vis_sonar_active(s, dur):
    core = Dot(radius=0.14, color=ACCENT).move_to(_zone(-0.1) + LEFT * 1.2)
    rings = VGroup(*[Circle(radius=0.5 + i * 0.55, color=GREEN, stroke_width=4)
                     .move_to(core) for i in range(3)])
    tgt = _submarine(0.35)
    tgt["all"].move_to(_zone(0.4) + RIGHT * 2.9)
    ping = _T("PING!", size=26, color=GREEN, bold=True).next_to(core, UP, buff=0.3)
    lbl = _label("Sonar aktif — kirim & terima gema", color=WHITE, size=20, bold=False)
    lbl.move_to(_zone(-1.7))
    grp = VGroup(core, rings, tgt["all"], ping, lbl)
    s.play(FadeIn(core), Write(ping), FadeIn(tgt["all"]), FadeIn(lbl), run_time=1.1)
    s.play(LaggedStart(*[Succession(FadeIn(r, scale=1.2), FadeOut(r)) for r in rings],
                       lag_ratio=0.35), run_time=1.6)
    return grp

def vis_sonar_passive(s, dur):
    base = Line(LEFT * 2.6, RIGHT * 2.6, color=GREY, stroke_width=3).move_to(_zone(-0.2))
    w1 = ParametricFunction(lambda t: np.array([t, 0.35 * np.sin(t * 6), 0]),
                            t_range=[-2.4, 2.4, 0.05], color=GREEN, stroke_width=4).move_to(_zone(0.35))
    w2 = w1.copy().rotate(180 * DEGREES).move_to(_zone(-0.85))
    blip = _T("dengarkan…", size=20, color=GREEN).next_to(base, RIGHT, buff=0.25)
    lbl = _label("Sonar pasif — diam & mendengar", color=WHITE, size=20, bold=False)
    lbl.move_to(_zone(-1.7))
    grp = VGroup(base, w1, w2, blip, lbl)
    s.play(Create(base), Create(w1), Create(w2), FadeIn(blip), FadeIn(lbl), run_time=1.4)
    s.play(w1.animate.shift(DOWN * 0.3), w2.animate.shift(UP * 0.3), run_time=0.8)
    return grp

def vis_life_oxygen(s, dur):
    o2 = RoundedRectangle(corner_radius=0.12, width=0.7, height=1.5, color=GREEN,
                          stroke_width=4).move_to(_zone(0.0) + LEFT * 3.0)
    o2_l = _T("O₂", size=22, color=GREEN, bold=True).move_to(o2)
    scr = Rectangle(width=1.6, height=1.2, color=ACCENT, stroke_width=4).move_to(_zone(0.0))
    scr_l = _T("SCRUBBER", size=14, color=ACCENT, bold=True).move_to(scr)
    a1 = Arrow(o2.get_right(), scr.get_left() + UP * 0.25, color=GREEN, stroke_width=4)
    a2 = Arrow(scr.get_left() + DOWN * 0.25, o2.get_right() + DOWN * 0.15, color=WATER, stroke_width=4)
    co2 = _T("CO₂ keluar", size=17, color=WATER).next_to(a2.get_end(), DOWN, buff=0.08)
    man = _stickman(0.55).move_to(_zone(0.0) + RIGHT * 2.6)
    ca = Arrow(scr.get_right(), man.get_left(), color=GREEN, stroke_width=4)
    grp = VGroup(o2, o2_l, scr, scr_l, a1, a2, co2, man, ca)
    s.play(FadeIn(o2), FadeIn(o2_l), FadeIn(scr), FadeIn(scr_l), FadeIn(man), run_time=1.1)
    s.play(GrowArrow(a1), GrowArrow(a2), FadeIn(co2), GrowArrow(ca), run_time=1.2)
    return grp

def vis_life_supply(s, dur):
    pot = Arc(radius=0.7, start_angle=0, angle=PI, color=GREY, stroke_width=5,
              fill_color=GREY, fill_opacity=0.4).move_to(_zone(0.2) + LEFT * 2.4)
    steam = VGroup(*[_bubble(pot.get_top() + UP * 0.2 + RIGHT * dx, r=0.07) for dx in (-0.2, 0.2)])
    man = _stickman(0.7, pose="up").move_to(_zone(0.0) + RIGHT * 1.8)
    bunk = VGroup(*[Rectangle(width=1.4, height=0.28, color=GREY, stroke_width=3)
                    for _ in range(2)])
    bunk.arrange(DOWN, buff=0.3).move_to(_zone(0.2) + RIGHT * 0.0)
    lbl = _label("Dapur 24 jam • Air tawar dari laut", color=ACCENT, size=20, bold=False)
    lbl.move_to(_zone(-1.6))
    grp = VGroup(pot, steam, man, bunk, lbl)
    s.play(FadeIn(pot), FadeIn(bunk), FadeIn(man), FadeIn(lbl), run_time=1.2)
    s.play(LaggedStart(*[b.animate.shift(UP * 0.7) for b in steam], lag_ratio=0.3), run_time=0.9)
    return grp

def vis_life_days(s, dur):
    cal = Rectangle(width=2.6, height=1.8, color=GREY, stroke_width=4).move_to(_zone(0.0) + LEFT * 2.2)
    top = Rectangle(width=2.6, height=0.4, color=DANGER, fill_color=DANGER,
                    fill_opacity=1, stroke_width=0).move_to(cal.get_top())
    num = _T("100+", size=44, color=WHITE, bold=True).move_to(cal.get_center() + DOWN * 0.15)
    days = _T("HARI", size=18, color=GREY).next_to(num, DOWN, buff=0.1)
    sub = _submarine(0.6)
    sub["all"].move_to(_zone(0.0) + RIGHT * 2.4)
    grp = VGroup(cal, top, num, days, sub["all"])
    s.play(Create(cal), FadeIn(top), FadeIn(num), FadeIn(days), FadeIn(sub["all"]), run_time=1.4)
    s.play(Rotate(sub["prop"], angle=2 * PI), num.animate.scale(1.15), run_time=0.9)
    return grp

def vis_rescue_dsv(s, dur):
    stranded = _submarine(1.0)
    stranded["all"].move_to(_zone(-1.0)).rotate(6 * DEGREES)
    dsv = RoundedRectangle(corner_radius=0.2, width=2.0, height=1.0, color=ACCENT,
                           stroke_width=5, fill_color=ACCENT, fill_opacity=0.25)
    dsv.move_to(stranded["all"].get_top() + UP * 0.85)
    dsv_l = _T("DSV PENYELAMAT", size=15, color=ACCENT, bold=True).next_to(dsv, UP, buff=0.1)
    hatch = Line(stranded["sail"].get_top(), dsv.get_bottom(), color=GREEN, stroke_width=4)
    lbl = _label("Menempel → buka pintu → evakuasi", color=WHITE, size=20, bold=False)
    lbl.move_to(_zone(-1.85))
    grp = VGroup(stranded["all"], dsv, dsv_l, hatch, lbl)
    s.play(FadeIn(stranded["all"]), Write(lbl), run_time=1.1)
    s.play(FadeIn(dsv, shift=DOWN * 0.6), FadeIn(dsv_l), Create(hatch), run_time=1.2)
    return grp

def vis_escape_suit(s, dur):
    man = _stickman(0.9, color=ACCENT, pose="up").move_to(_zone(-1.2))
    tower = _submarine(1.1)
    tower["all"].move_to(_zone(-1.9))
    bub = VGroup(*[_bubble(man.get_center() + UP * 1.1 + RIGHT * dx, r=0.06) for dx in (-0.3, 0.3)])
    up_a = Arrow(man.get_top() + UP * 1.2, man.get_top() + UP * 2.2, color=GREEN, stroke_width=5)
    lbl = _label("Menara pelarian → apung pelan-pelan", color=WHITE, size=20, bold=False)
    lbl.move_to(_zone(1.35))
    grp = VGroup(tower["all"], man, bub, up_a, lbl)
    s.play(FadeIn(tower["all"]), FadeIn(man), Write(lbl), run_time=1.2)
    s.play(LaggedStart(*[b.animate.shift(UP * 1.2) for b in bub], lag_ratio=0.25),
           man.animate.shift(UP * 1.4), GrowArrow(up_a), run_time=1.3)
    return grp

def vis_deep_mystery(s, dur):
    grid = VGroup(*[Line(LEFT * 4 + UP * y, RIGHT * 4 + UP * y, color=GREY,
                         stroke_width=1).set_opacity(0.35) for y in np.linspace(-1.8, 1.0, 6)])
    grid.add(*[Line(LEFT * 4 + RIGHT * x + UP * 1.0, LEFT * 4 + RIGHT * x + DOWN * 1.8,
                    color=GREY, stroke_width=1).set_opacity(0.35) for x in np.linspace(-4, 4, 9)])
    dots = VGroup(*[Dot(radius=0.05, color=ACCENT).move_to(
        _zone(0.0) + RIGHT * dx + UP * dy) for dx, dy in
        [(-2.5, 0.5), (-1.0, -0.8), (0.6, 0.3), (2.2, -0.5), (3.2, 0.7)]])
    lbl = _label("82% dasar samudra belum terpetakan", color=ACCENT, size=21, bold=False)
    lbl.move_to(_zone(-1.85))
    grp = VGroup(grid, dots, lbl)
    s.play(Create(grid), Write(lbl), run_time=1.3)
    s.play(LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.2), run_time=1.1)
    return grp

def vis_type_missile(s, dur):
    sub = _submarine(1.0)
    sub["all"].move_to(_zone(-0.6))
    msl = RoundedRectangle(corner_radius=0.1, width=0.34, height=1.6, color=DANGER,
                           stroke_width=3, fill_color=DANGER, fill_opacity=0.9)
    tip = Triangle(radius=0.2, color=DANGER, fill_color=DANGER, fill_opacity=1)
    msl_grp = VGroup(msl, tip.arrange(UP, buff=0)).move_to(sub["sail"].get_top() + UP * 1.4)
    lbl = _label("Pembawa rudal balistik — tameng negara", color=ACCENT, size=21, bold=False)
    lbl.move_to(_zone(1.35))
    grp = VGroup(sub["all"], msl_grp, lbl)
    s.play(FadeIn(sub["all"]), Write(lbl), run_time=1.1)
    s.play(msl_grp.animate.shift(UP * 0.9), run_time=1.2)
    return grp

def vis_type_attack(s, dur):
    sub = _submarine(0.85)
    sub["all"].move_to(_zone(-0.4) + LEFT * 1.6)
    tgt = Circle(radius=0.9, color=DANGER, stroke_width=4).move_to(_zone(-0.4) + RIGHT * 2.4)
    t1 = Line(tgt.get_left() + RIGHT * 0.12, tgt.get_right() + LEFT * 0.12, color=DANGER, stroke_width=2)
    t2 = Line(tgt.get_top() + DOWN * 0.12, tgt.get_bottom() + UP * 0.12, color=DANGER, stroke_width=2)
    lbl = _label("Kapal selam penyerang — pemburu senyap", color=ACCENT, size=21, bold=False)
    lbl.move_to(_zone(1.35))
    grp = VGroup(sub["all"], tgt, t1, t2, lbl)
    s.play(FadeIn(sub["all"], shift=RIGHT * 0.6), Create(tgt), Create(t1), Create(t2),
           Write(lbl), run_time=1.5)
    return grp

def vis_type_stealth(s, dur):
    s1 = _submarine(0.8)
    s1["all"].move_to(_zone(0.5) + LEFT * 1.4)
    s2 = _submarine(0.8)
    s2["all"].move_to(_zone(-1.1) + RIGHT * 1.4).rotate(PI)
    q = _T("?", size=40, color=ACCENT, bold=True).move_to(_zone(-0.3))
    lbl = _label("Berpapasan… tanpa saling menyadari", color=WHITE, size=21, bold=False)
    lbl.move_to(_zone(1.35))
    grp = VGroup(s1["all"], s2["all"], q, lbl)
    s.play(FadeIn(s1["all"], shift=RIGHT * 0.8), FadeIn(s2["all"], shift=LEFT * 0.8),
           FadeIn(q, scale=1.5), Write(lbl), run_time=1.6)
    return grp

def vis_generic(s, dur, key="default"):
    title = key.replace("_", " ").title()
    card = RoundedRectangle(corner_radius=0.18, width=5.2, height=2.4, color=PRIMARY,
                            stroke_width=4, fill_color=PRIMARY, fill_opacity=0.12)
    card.move_to(_zone(0.0))
    ttl = _label(title, color=ACCENT, size=24).move_to(card.get_center() + UP * 0.35)
    sub = _submarine(0.4)
    sub["all"].move_to(card.get_center() + DOWN * 0.55)
    grp = VGroup(card, ttl, sub["all"])
    s.play(Create(card), Write(ttl), FadeIn(sub["all"]), run_time=1.6)
    return grp

VISUALS = {
    "history_ancient": vis_history_ancient,
    "history_wood": vis_history_wood,
    "history_turtle": vis_history_turtle,
    "history_war": vis_history_war,
    "history_wolfpack": vis_history_wolfpack,
    "history_nuclear": vis_history_nuclear,
    "archimedes_question": vis_archimedes_question,
    "archimedes_law": vis_archimedes_law,
    "archimedes_float": vis_archimedes_float,
    "anatomy_hull": vis_anatomy_hull,
    "anatomy_ballast": vis_anatomy_ballast,
    "anatomy_rooms": vis_anatomy_rooms,
    "ballast_tank": vis_ballast_tank,
    "ballast_water_in": vis_ballast_water_in,
    "ballast_sinking": vis_ballast_sinking,
    "ballast_air_in": vis_ballast_air_in,
    "ballast_rise": vis_ballast_rise,
    "trim_tank": vis_trim_tank,
    "dive_planes": vis_dive_planes,
    "depth_control": vis_depth_control,
    "dive_controlled": vis_dive_controlled,
    "pressure_depth": vis_pressure_depth,
    "pressure_hull": vis_pressure_hull,
    "crush_depth": vis_crush_depth,
    "diesel_engine": vis_diesel_engine,
    "nuclear_engine": vis_nuclear_engine,
    "silent_running": vis_silent_running,
    "periscope": vis_periscope,
    "sonar_active": vis_sonar_active,
    "sonar_passive": vis_sonar_passive,
    "life_oxygen": vis_life_oxygen,
    "life_supply": vis_life_supply,
    "life_days": vis_life_days,
    "rescue_dsv": vis_rescue_dsv,
    "escape_suit": vis_escape_suit,
    "deep_mystery": vis_deep_mystery,
    "type_missile": vis_type_missile,
    "type_attack": vis_type_attack,
    "type_stealth": vis_type_stealth,
}

# Durasi play asli tiap visual (diukur via instrumentasi, deterministik)
VISUAL_SPENT = {
    "history_ancient": 1.6, "history_wood": 1.8, "history_turtle": 2.7,
    "history_war": 1.8, "history_wolfpack": 2.2, "history_nuclear": 2.7,
    "archimedes_question": 2.2, "archimedes_law": 2.5, "archimedes_float": 2.6,
    "anatomy_hull": 2.4, "anatomy_ballast": 3.1, "anatomy_rooms": 2.5,
    "ballast_tank": 1.6, "ballast_water_in": 3.7, "ballast_sinking": 2.3,
    "ballast_air_in": 3.6, "ballast_rise": 3.0, "trim_tank": 2.4,
    "dive_planes": 2.5, "depth_control": 2.8, "dive_controlled": 2.8,
    "pressure_depth": 3.3, "pressure_hull": 2.5, "crush_depth": 2.5,
    "diesel_engine": 2.2, "nuclear_engine": 2.9, "silent_running": 2.9,
    "periscope": 2.1, "sonar_active": 2.7, "sonar_passive": 2.2,
    "life_oxygen": 2.3, "life_supply": 2.1, "life_days": 2.3,
    "rescue_dsv": 2.3, "escape_suit": 2.5, "deep_mystery": 2.4,
    "type_missile": 2.3, "type_attack": 1.5, "type_stealth": 1.6,
}

def _spent(key):
    return VISUAL_SPENT.get(key, 1.6)  # vis_generic ±1.6s

# ---------- SCENE UTAMA ----------
class ExplainerScene(BaseScene):
    def construct(self):
        # --- background + jam internal (akumulasi waktu) ---
        bg = Rectangle(width=config.frame_width, height=config.frame_height,
                       fill_color=BG, fill_opacity=1, stroke_width=0)
        self.add(bg)
        self._clock = 0.0
        _orig_play = self.play

        def timed_play(*args, **kwargs):
            if "run_time" in kwargs:
                rt = kwargs.pop("run_time")
                self._clock += rt
                _orig_play(*args, run_time=rt, **kwargs)
            else:
                # tanpa run_time eksplisit (mis. Wait dari Scene.wait):
                # pakai durasi natural animasi, jangan dipaksa 1.0
                rt = getattr(args[0], "run_time", 1.0) if args else 1.0
                self._clock += rt
                _orig_play(*args, **kwargs)

        self.play = timed_play

        data = self.data
        brand = self.brand
        primary = brand.get("primary_color", PRIMARY)
        accent = brand.get("accent_color", ACCENT)

        wc = lambda t: max(len(str(t).split()), 1)

        # ---- normalisasi konten (dukung format string & dict) ----
        sections = []
        n_pts = 0
        for sec in data.get("sections", []):
            pts = []
            for p in sec.get("points", []):
                if isinstance(p, dict):
                    pts.append((p.get("text", ""), p.get("visual", "default")))
                else:
                    pts.append((str(p), "default"))
            sections.append((sec.get("heading", ""), pts))
            n_pts += len(pts)
        q_text = str(data.get("question", ""))
        c_text = str(data.get("conclusion", ""))
        n_sec = len(sections)

        # ---- hitung target durasi total video ----
        adur = 0.0
        try:
            adur = float(data.get("audio_duration") or 0)
        except (TypeError, ValueError):
            adur = 0.0
        words = wc(q_text) + wc(c_text)
        for h, pts in sections:
            words += wc(h)
            for t, _ in pts:
                words += wc(t)

        INTRO_T = 5.5   # intro channel + kartu judul
        OUTRO_T = 4.9   # outro + wait 0.3
        IN_Q, OUT_Q = 0.9, 0.7
        IN_P, OUT_P = 0.7, 0.7
        IN_H, OUT_H = 0.7, 0.7
        IN_C, OUT_C = 1.1, 0.8
        QVIS, CVIS = 0.9, 1.6

        known = (INTRO_T + OUTRO_T + IN_Q + QVIS + OUT_Q + IN_C + CVIS + OUT_C
                 + n_sec * (IN_H + OUT_H)
                 + n_pts * (IN_P + OUT_P)
                 + sum(_spent(v) for _, pts in sections for _, v in pts))

        if adur > 30:
            target = adur + 4.0                # video = audio + 0.6s (outro terlihat)
        else:
            target = max(known + words * 0.42, 60.0)
        leftover = target - known

        wq = wc(q_text) + 8
        wcc = wc(c_text) + 8
        W = wq + wcc
        for h, pts in sections:
            W += wc(h) + 4
            for t, _ in pts:
                W += wc(t) + 6
        wg_q = max(leftover * wq / W, 0.1)
        wg_c = max(leftover * wcc / W, 0.1)
        wg_h = [max(leftover * (wc(h) + 4) / W, 0.1) for h, _ in sections]
        wg_p = [[max(leftover * (wc(t) + 6) / W, 0.12) for t, _ in pts] for _, pts in sections]

        # ================= INTRO =================
        self.intro()  # dari BaseScene (nama channel) — ±1.5s

        ch_name = self.brand.get("channel_name", "")
        ch = _T(ch_name, size=24, color=accent, bold=True).to_edge(UP, buff=1.0)
        ttl_lines = _wrap(str(data.get("title", "")), 30, 2)
        ttl = VGroup(*[_T(l, size=46, color=WHITE, bold=True) for l in ttl_lines]
                     ).arrange(DOWN, buff=0.22).next_to(ch, DOWN, buff=0.45)
        box = SurroundingRectangle(ttl, color=primary, corner_radius=0.12, buff=0.3)
        box.set_fill(primary, opacity=0.15)
        swim = _submarine(0.8)
        swim["all"].move_to(LEFT * 7.5 + DOWN * 2.0)
        self.play(FadeIn(ch), run_time=0.6)
        self.play(DrawBorderThenFill(box), Write(ttl), run_time=1.4)
        self.add(swim["all"])
        self.play(swim["all"].animate.move_to(RIGHT * 7.5 + DOWN * 2.0), run_time=1.3)
        self.play(FadeOut(ch), FadeOut(ttl), FadeOut(box), FadeOut(swim["all"]), run_time=0.7)
        # total intro+judul ≈ 5.5s

        # ================= PERTANYAAN =================
        qb = _bullet(q_text, 24, 58, 3)
        qb.set_width(min(qb.width, 10.8))
        qb.to_edge(UP, buff=1.5)
        bigq = _T("?", size=64, color=accent, bold=True).move_to(_zone(0.1) + RIGHT * 3.6)
        sil = _submarine(0.7)
        sil["all"].move_to(_zone(-0.7) + LEFT * 2.2)
        self.play(FadeIn(qb, shift=DOWN), run_time=IN_Q)
        self.play(FadeIn(bigq, scale=1.6), FadeIn(sil["all"], shift=RIGHT * 0.5), run_time=QVIS)
        if wg_q > 0.05:
            self.wait(wg_q)
        self.play(FadeOut(qb), FadeOut(bigq), FadeOut(sil["all"]), run_time=OUT_Q)

        # ================= SECTIONS =================
        for si, (heading, pts) in enumerate(sections):
            hb = _bullet(heading, 34)
            hb.set_width(min(hb.width, 11.0))
            hb.to_edge(UP, buff=0.55)
            hbar = Rectangle(width=hb.width + 0.5, height=0.06, color=accent,
                             fill_color=accent, fill_opacity=1, stroke_width=0)
            hbar.next_to(hb, DOWN, buff=0.12)
            self.play(FadeIn(hb, shift=DOWN), FadeIn(hbar), run_time=IN_H)
            if wg_h[si] > 0.05:
                self.wait(wg_h[si])

            for pi, (ptext, pvis) in enumerate(pts):
                bullet = _bullet(ptext, 24)
                bullet.set_width(min(bullet.width, 11.6))
                bullet.next_to(hbar, DOWN, buff=0.4)
                self.play(FadeIn(bullet, shift=RIGHT), run_time=IN_P)

                t0 = self._clock
                fn = VISUALS.get(pvis)
                vis_grp = None
                try:
                    if fn is not None:
                        vis_grp = fn(self, _spent(pvis))
                    else:
                        vis_grp = vis_generic(self, 1.6, key=pvis)
                except Exception as e:
                    print(f"[explainer] visual '{pvis}' gagal: {e}")
                    vis_grp = None
                    for m in list(self.mobjects):
                        if m is not bg and m is not hb and m is not hbar and m is not bullet:
                            self.remove(m)

                # normalisasi: tunggu selisih biar total = target persis
                actual = self._clock - t0
                rest = wg_p[si][pi] + _spent(pvis) - actual
                if rest > 0.05:
                    self.wait(rest)

                fade_list = [bullet]
                if vis_grp is not None and len(vis_grp) > 0:
                    fade_list.append(vis_grp)
                try:
                    self.play(*[FadeOut(m) for m in fade_list], run_time=OUT_P)
                except Exception:
                    for m in self.mobjects:
                        if m is not bg and m is not hb and m is not hbar:
                            self.remove(m)

            self.play(FadeOut(hb), FadeOut(hbar), run_time=OUT_H)

        # ================= KESIMPULAN =================
        cbox = RoundedRectangle(corner_radius=0.22, width=13.0, height=4.3, color=accent,
                                stroke_width=3).move_to([0, 0.3, 0])
        cbox.set_fill(accent, opacity=0.07)
        clines = _wrap(c_text, 72, 7)
        ctxt = VGroup(*[_T(l, size=21, color=accent, bold=False) for l in clines]
                      ).arrange(DOWN, buff=0.15).move_to(cbox.get_center())
        self.play(FadeIn(cbox), run_time=IN_C)
        self.play(Write(ctxt), run_time=1.6)
        if wg_c - 1.6 > 0.05:
            self.wait(wg_c - 1.6)
        self.play(FadeOut(cbox), FadeOut(ctxt), run_time=OUT_C)

        # ================= OUTRO =================
        cta = _T("Subscribe untuk episode berikutnya", size=32, color=accent, bold=True)
        cta.to_edge(UP, buff=2.2)
        sub2 = _submarine(0.9)
        sub2["all"].move_to(DOWN * 1.6)
        self.play(FadeIn(cta, shift=UP), FadeIn(sub2["all"]), run_time=0.9)
        self.play(Rotate(sub2["prop"], angle=3 * PI),
                  sub2["all"].animate.shift(RIGHT * 1.2), run_time=1.4)
        self.wait(1.6)
        self.play(FadeOut(cta), FadeOut(sub2["all"]), run_time=0.8)

        self.wait(4.3)


def build_scene(data, config):
    return ExplainerScene(data=data, config=config)




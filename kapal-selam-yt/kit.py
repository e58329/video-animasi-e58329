"""Kit visual bersama: palet, helper teks, kapal selam, dan NarratedScene.

Aturan layout (1920x1080 = 14.22 x 8 unit Manim):
  - judul bab di atas (y ~ 3.3), area gambar y = -2.3 .. 2.6
  - zona y < -2.5 dikosongkan karena subtitle dibakar di bagian bawah
Semua teks memakai Text (tanpa LaTeX), jadi tidak perlu instalasi TeX.
"""
import json
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from manim import *  # noqa: F401,F403

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cfg  # noqa: E402
from script_id import CHAPTERS  # noqa: E402

config.background_color = "#0B1426"

# ---- palet ---------------------------------------------------------------
NAVY = "#0B1426"
DEEP = "#0F2A4A"
SEA = "#134B7C"
SKY = "#4FC3F7"
BLUE = "#1E88E5"
GOLD = "#FFC107"
CORAL = "#EF5350"
MINT = "#66BB6A"
INK = "#F5F7FA"
MIST = "#90A4AE"


def p(x, y):
    return np.array([float(x), float(y), 0.0])


def T(s, size=30, color=INK, **kw):
    return Text(s, font_size=size, color=color, font=cfg.FONT, **kw)


def fit(m, w):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def arr(a, b, color=INK, w=5):
    return Arrow(np.array(a, dtype=float), np.array(b, dtype=float), buff=0, color=color,
                 stroke_width=w, max_tip_length_to_length_ratio=0.35)


def box(label, w=2.1, h=0.8, color=SKY, size=22):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color,
                         stroke_width=3, fill_color=color, fill_opacity=0.15)
    t = fit(T(label, size), w - 0.2)
    t.move_to(r)
    return VGroup(r, t)


def ocean(top=1.2, bottom=-2.3, width=13.2, opacity=0.45):
    body = Rectangle(width=width, height=top - bottom, stroke_width=0,
                     fill_color=SEA, fill_opacity=opacity).move_to(p(0, (top + bottom) / 2))
    wave = FunctionGraph(lambda x: top + 0.07 * np.sin(2.2 * x),
                         x_range=[-width / 2, width / 2], color=SKY, stroke_width=4)
    return VGroup(body, wave)


def ocean_front(top=1.2, bottom=-2.3, width=13.2):
    r = Rectangle(width=width, height=top - bottom, stroke_width=0,
                  fill_color=SKY, fill_opacity=0.10).move_to(p(0, (top + bottom) / 2))
    r.set_z_index(5)
    return r


def person(scale=1.0, color=INK):
    head = Circle(radius=0.1, stroke_color=color, stroke_width=3, fill_opacity=0).move_to(p(0, 0.3))
    body = Line(p(0, 0.2), p(0, -0.15))
    arms = Line(p(-0.17, 0.1), p(0.17, 0.1))
    legs = VGroup(Line(p(0, -0.15), p(-0.12, -0.38)), Line(p(0, -0.15), p(0.12, -0.38)))
    g = VGroup(head, body, arms, legs).set_stroke(color, 3)
    return g.scale(scale)


def bell_icon(color=GOLD):
    dome = Sector(radius=0.42, angle=PI, start_angle=0, fill_color=color, fill_opacity=1, stroke_width=0)
    base = Rectangle(width=0.84, height=0.14, fill_color=color, fill_opacity=1,
                     stroke_width=0).move_to(p(0, -0.07))
    clap = Dot(p(0, -0.27), radius=0.08, color=color)
    return VGroup(dome, base, clap)


def satellite():
    body = Rectangle(width=0.45, height=0.35, fill_color=MIST, fill_opacity=1, stroke_width=0)
    lp = Rectangle(width=0.55, height=0.25, fill_color=SKY, fill_opacity=1,
                   stroke_width=0).next_to(body, LEFT, buff=0.04)
    rp = Rectangle(width=0.55, height=0.25, fill_color=SKY, fill_opacity=1,
                   stroke_width=0).next_to(body, RIGHT, buff=0.04)
    return VGroup(lp, body, rp)


# ---- ikon sejarah ----------------------------------------------------------
def icon_bell():
    dome = Arc(radius=0.55, start_angle=0, angle=PI, stroke_color=SKY, stroke_width=4)
    base = Line(p(-0.55, 0), p(0.55, 0), color=SKY, stroke_width=4)
    rope = Line(p(0, 0.55), p(0, 0.95), color=MIST, stroke_width=3)
    man = person(0.9).move_to(p(0, 0.05))
    return VGroup(dome, base, rope, man)


def icon_boat():
    hull = Polygon(p(-0.8, 0), p(0.8, 0), p(0.55, -0.32), p(-0.55, -0.32),
                   stroke_color="#C58B4C", stroke_width=4, fill_color="#7A5230", fill_opacity=0.9)
    oars = VGroup(Line(p(-0.3, 0), p(-0.55, -0.5)), Line(p(0.3, 0), p(0.05, -0.5))).set_stroke(MIST, 3)
    return VGroup(oars, hull)


def icon_turtle():
    egg = Ellipse(width=0.8, height=1.0, fill_color="#B8860B", fill_opacity=1,
                  stroke_color=GOLD, stroke_width=3)
    window = Circle(radius=0.12, fill_color=SKY, fill_opacity=1, stroke_width=0).move_to(p(0, 0.2))
    hatch = Line(p(-0.12, 0.52), p(0.12, 0.52), color=GOLD, stroke_width=4)
    return VGroup(egg, window, hatch)


def icon_alvin():
    body = Circle(radius=0.38, fill_color=INK, fill_opacity=1, stroke_width=0)
    port = Circle(radius=0.12, fill_color=SKY, fill_opacity=1, stroke_width=0).move_to(p(0.15, 0.05))
    stripe = Rectangle(width=0.8, height=0.16, fill_color=CORAL, fill_opacity=1,
                       stroke_width=0).move_to(p(-0.05, -0.42))
    arm = VGroup(Line(p(0.3, -0.2), p(0.7, -0.4)), Line(p(0.7, -0.4), p(0.85, -0.25))).set_stroke(MIST, 4)
    return VGroup(body, port, stripe, arm)


# ---- kapal selam -----------------------------------------------------------
class Sub(VGroup):
    """Kapal selam tampak samping, menghadap kanan.

    internals=True menambah lambung tekan, dua tangki ballast, dan air di dalamnya
    (animasikan dengan Sub.fill(level) dengan level 0..1).
    """

    def __init__(self, color=BLUE, internals=False, portholes=True, **kw):
        super().__init__(**kw)
        self.hull = Ellipse(width=5.0, height=1.3, fill_color=color, fill_opacity=1, stroke_width=0)
        self.sail = RoundedRectangle(corner_radius=0.12, width=0.95, height=0.55, fill_color=color,
                                     fill_opacity=1, stroke_width=0).move_to(p(0.55, 0.78))
        self.scope = VGroup(Line(p(0.45, 1.0), p(0.45, 1.4)),
                            Line(p(0.45, 1.4), p(0.72, 1.4))).set_stroke(GOLD, 4)
        self.rudder = Polygon(p(-2.2, 0.4), p(-2.75, 0.95), p(-2.5, 0.95), p(-1.95, 0.45),
                              fill_color=GOLD, fill_opacity=1, stroke_width=0)
        self.stern_plane = Polygon(p(-2.3, 0.0), p(-2.95, 0.14), p(-2.95, -0.14),
                                   fill_color=GOLD, fill_opacity=1, stroke_width=0)
        self.sail_plane = Rectangle(width=0.5, height=0.09, fill_color=GOLD, fill_opacity=1,
                                    stroke_width=0).move_to(p(0.55, 0.72))
        self.prop = Ellipse(width=0.14, height=0.75, fill_color=GOLD, fill_opacity=1,
                            stroke_width=0).move_to(p(-2.55, 0.0))
        self.add(self.stern_plane, self.rudder, self.prop, self.hull, self.sail,
                 self.scope, self.sail_plane)
        self.has_internals = internals
        if internals:
            self.inner = Ellipse(width=2.4, height=0.62, stroke_color=INK, stroke_width=3,
                                 fill_opacity=0)
            self.tanks = VGroup(*[
                Rectangle(width=0.7, height=0.36, stroke_color=GOLD, stroke_width=3,
                          fill_opacity=0).move_to(p(x, -0.1))
                for x in (-1.65, 1.65)
            ])
            self.water = self.water_at(0.0)
            self.add(self.inner, self.tanks, self.water)
        elif portholes:
            self.ports = VGroup(*[Dot(p(x, 0.12), radius=0.06, color=INK) for x in (-0.9, -0.3, 0.2)])
            self.add(self.ports)

    def water_at(self, level):
        """Geometri air di dalam tangki untuk level 0..1 (mengikuti posisi & skala saat ini)."""
        sc = self.tanks[0].width / 0.7
        parts = []
        for tank in self.tanks:
            h = max(0.36 * level * sc, 0.001)
            r = Rectangle(width=0.64 * sc, height=h, stroke_width=0, fill_color=SKY, fill_opacity=0.9)
            r.move_to(tank.get_bottom() + UP * (h / 2 + 0.03 * sc))
            parts.append(r)
        return VGroup(*parts)

    def fill(self, level):
        return Transform(self.water, self.water_at(level))


def top_sub(color=BLUE):
    """Kapal selam tampak atas (untuk demo kemudi)."""
    hull = Ellipse(width=2.8, height=0.7, fill_color=color, fill_opacity=1, stroke_width=0)
    sail = Ellipse(width=0.5, height=0.3, fill_color=color, fill_opacity=1,
                   stroke_color=INK, stroke_width=2).move_to(p(0.3, 0))
    rudder = Line(p(-1.4, 0), p(-1.9, 0), color=GOLD, stroke_width=8)
    fins = VGroup(Line(p(0.2, 0.35), p(0.0, 0.7)), Line(p(0.2, -0.35), p(0.0, -0.7))).set_stroke(GOLD, 6)
    g = VGroup(rudder, hull, sail, fins)
    g.rudder = rudder
    g.hull = hull
    return g


def flow_row(labels, y, color, w=2.1, gap=0.55):
    boxes = [box(l, w=w, h=0.8, color=color, size=20) for l in labels]
    total = len(boxes) * w + (len(boxes) - 1) * gap
    x0 = -total / 2 + w / 2
    for i, b in enumerate(boxes):
        b.move_to(p(x0 + i * (w + gap), y))
    arrows = [arr(boxes[i].get_right(), boxes[i + 1].get_left(), INK, 3) for i in range(len(boxes) - 1)]
    return boxes, arrows


def pulses(center, direction=RIGHT, radii=None, color=SKY, width=PI / 7):
    base = float(np.arctan2(direction[1], direction[0]))
    return [Arc(radius=r, start_angle=base - width / 2, angle=width, arc_center=center,
                stroke_color=color, stroke_width=5) for r in radii]


def pulse_anim(arcs):
    return LaggedStart(*[Succession(FadeIn(a, run_time=0.2), FadeOut(a, run_time=0.3)) for a in arcs],
                       lag_ratio=0.35)


# ---- naskah & manifest ------------------------------------------------------
def load_lines(chapter_id):
    ch = next(c for c in CHAPTERS if c["id"] == chapter_id)
    manifest = {}
    if cfg.MANIFEST.exists():
        manifest = json.loads(cfg.MANIFEST.read_text())
    out = []
    for i, ln in enumerate(ch["lines"]):
        m = manifest.get(f"{chapter_id}_{i:02d}")
        if m:
            out.append({"sub": ln["sub"], "dur": float(m["dur"]), "wav": m["wav"]})
        else:  # belum ada TTS: pratinjau tanpa suara dengan durasi perkiraan
            out.append({"sub": ln["sub"], "dur": max(2.0, len(ln["say"].split()) / 2.7), "wav": None})
    return out


class NarratedScene(Scene):
    """Scene yang animasinya disinkronkan ke narasi.

    Pakai:  with self.line():  <animasi untuk kalimat ke-i>
    Audio kalimat dimulai saat blok dimulai; setelah blok selesai, scene menunggu
    sampai audio + jeda selesai. Subtitle dicatat ke build/cues/<bab>.json.
    """

    chapter_id = ""

    def setup(self):
        super().setup()
        self.lines = load_lines(self.chapter_id)
        self._i = 0
        self.cues = []

    def now(self):
        r = getattr(self, "renderer", None)
        t = getattr(r, "time", None)
        if t is None:
            t = getattr(self, "time", 0.0)
        return float(t)

    @contextmanager
    def line(self):
        ln = self.lines[self._i]
        idx = self._i
        self._i += 1
        t0 = self.now()
        if ln["wav"]:
            self.add_sound(ln["wav"])
        cue = {"start": t0, "end": t0 + ln["dur"], "text": ln["sub"]}
        self.cues.append(cue)
        yield ln
        rest = t0 + ln["dur"] + cfg.LINE_GAP - self.now()
        if rest > 1.0 / cfg.FPS:
            self.wait(rest)
        elif rest < -0.05:
            print(f"[peringatan] {self.chapter_id} kalimat #{idx}: animasi {-rest:.1f} dtk lebih "
                  f"lama dari narasi. Persingkat run_time-nya.")

    def hdr(self, num, title):
        t = T(f"{num} · {title}" if num else title, 38)
        t.to_edge(UP, buff=0.4)
        ul = Line(t.get_corner(DL) + DOWN * 0.1, t.get_corner(DR) + DOWN * 0.1, color=GOLD, stroke_width=4)
        return VGroup(t, ul)

    def clear(self, t=0.6):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=t)

    def tear_down(self):
        super().tear_down()
        assert self._i == len(self.lines), (
            f"{self.chapter_id}: {self._i} dari {len(self.lines)} kalimat naskah terpakai. "
            f"Jumlah 'with self.line()' harus sama dengan jumlah kalimat di script_id.py")
        cfg.CUES_DIR.mkdir(parents=True, exist_ok=True)
        (cfg.CUES_DIR / f"{self.chapter_id}.json").write_text(
            json.dumps(self.cues, ensure_ascii=False, indent=1))

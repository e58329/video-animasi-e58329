"""Bagian 1: hook, prolog subscribe, sejarah, Hukum Archimedes."""
from kit import *


class Ch00Hook(NarratedScene):
    chapter_id = "ch00"

    def construct(self):
        sea = ocean(top=1.4, bottom=-2.3)
        front = ocean_front(top=1.4, bottom=-2.3)
        sub = Sub(portholes=False).scale(0.7).move_to(p(0, 1.45))
        depth = ValueTracker(0)
        meter = always_redraw(
            lambda: T(f"Kedalaman: {int(depth.get_value())} m", 32, GOLD).move_to(p(4.4, 2.7)))
        span = DoubleArrow(p(-2.0, 2.65), p(2.0, 2.65), buff=0, color=GOLD, stroke_width=4)
        span_lab = T("± 100 meter", 28, GOLD).move_to(p(0, 3.2))

        with self.line():  # tabung baja 100 m
            self.play(FadeIn(sea), FadeIn(front), run_time=0.8)
            self.play(FadeIn(sub, shift=UP * 0.3), run_time=1.0)
            self.play(Create(span), FadeIn(span_lab), run_time=1.0)

        with self.line():  # turun ratusan meter
            self.play(FadeOut(span), FadeOut(span_lab), FadeIn(meter), run_time=0.6)
            self.play(sub.animate.shift(DOWN * 2.6), depth.animate.set_value(300),
                      run_time=4.5, rate_func=smooth)

        dots = VGroup(*[Dot(sub.hull.get_center() + RIGHT * x * 0.7, radius=0.05, color=INK)
                        for x in np.linspace(-1.5, 1.5, 9)])
        with self.line():  # puluhan manusia di dalam
            self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.25), run_time=3.0)
            tag = T("puluhan awak", 28, INK).next_to(sub, DOWN, buff=0.3)
            self.play(FadeIn(tag), run_time=0.6)

        with self.line():  # naik tenang
            self.play(FadeOut(tag), run_time=0.4)
            self.play(sub.animate.shift(UP * 2.6), dots.animate.shift(UP * 2.6),
                      depth.animate.set_value(0), run_time=4.0, rate_func=smooth)

        q = T("Bagaimana mungkin?", 56, GOLD).move_to(p(0, 3.1))
        with self.line():  # pertanyaan
            self.play(Write(q), run_time=1.4)
            self.play(Indicate(sub, color=GOLD, scale_factor=1.05), run_time=1.2)

        title = T(cfg.TITLE, 50, INK, weight=BOLD).move_to(p(0, 3.1))
        underline = Line(title.get_corner(DL) + DOWN * 0.12, title.get_corner(DR) + DOWN * 0.12,
                         color=GOLD, stroke_width=5)
        with self.line():  # judul
            self.play(FadeOut(meter), ReplacementTransform(q, title), run_time=1.2)
            self.play(Create(underline), run_time=1.0)
        self.clear()


class Ch01Prolog(NarratedScene):
    chapter_id = "ch01"

    def construct(self):
        ask = T("Satu permintaan kecil", 48, GOLD).move_to(p(0, 2.2))
        btn_bg = RoundedRectangle(corner_radius=0.25, width=4.4, height=1.1, fill_color=CORAL,
                                  fill_opacity=1, stroke_width=0)
        btn_tx = T("SUBSCRIBE", 38, INK, weight=BOLD)
        btn = VGroup(btn_bg, btn_tx).move_to(p(-0.8, 0.2))
        bell = bell_icon().move_to(p(2.4, 0.2))
        cursor = Polygon(p(0, 0), p(0, -0.55), p(0.15, -0.42), p(0.28, -0.7), p(0.4, -0.64),
                         p(0.27, -0.38), p(0.45, -0.36), fill_color=INK, fill_opacity=1,
                         stroke_color=NAVY, stroke_width=2).move_to(p(4.2, -1.8))

        with self.line():
            self.play(Write(ask), run_time=1.4)

        with self.line():
            self.play(FadeIn(btn, shift=UP * 0.2), FadeIn(bell, shift=UP * 0.2), FadeIn(cursor), run_time=1.0)
            self.play(cursor.animate.move_to(btn.get_center() + DOWN * 0.15 + RIGHT * 0.5), run_time=1.0)
            self.play(btn_bg.animate.set_fill(MIST, opacity=1),
                      Transform(btn_tx, T("SUBSCRIBED", 38, NAVY, weight=BOLD).move_to(btn_tx)),
                      run_time=0.5)
            self.play(cursor.animate.move_to(bell.get_center() + DOWN * 0.15 + RIGHT * 0.15), run_time=0.9)
            self.play(Wiggle(bell, rotation_angle=0.12 * TAU, scale_value=1.2, n_wiggles=6), run_time=1.5)

        free = T("Gratis · hanya satu ketukan", 36, INK).move_to(p(0, -1.4))
        with self.line():
            self.play(FadeIn(free, shift=UP * 0.2), run_time=0.8)
            self.play(Indicate(btn, color=GOLD, scale_factor=1.05), run_time=1.2)

        series = T("SERI · " + cfg.SERIES.upper(), 24, GOLD).move_to(p(0, 1.7))
        title = T(cfg.TITLE, 56, INK, weight=BOLD).move_to(p(0, 0.8))
        mini = Sub().scale(0.55).move_to(p(0, -0.9))
        with self.line():
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
            self.play(FadeIn(series), Write(title), FadeIn(mini, shift=UP * 0.3), run_time=2.0)
        self.clear()


class Ch02History(NarratedScene):
    chapter_id = "ch02"

    def construct(self):
        xs = [-5.2, -2.6, 0.0, 2.6, 5.2]
        timeline = Line(p(-6.4, -0.2), p(6.4, -0.2), color=MIST, stroke_width=4)

        def mk(i, icon, year, label):
            x = xs[i]
            icon.move_to(p(x, 1.0))
            dot = Dot(p(x, -0.2), color=GOLD, radius=0.1)
            yr = fit(T(year, 24, GOLD), 2.3).move_to(p(x, -0.65))
            lb = fit(T(label, 22, INK), 2.4).move_to(p(x, -1.1))
            return VGroup(icon, dot, yr, lb)

        hdr = self.hdr(1, "Mimpi Menyelam")
        items = [
            mk(0, icon_bell(), "Legenda", "Lonceng selam"),
            mk(1, icon_boat(), "± 1620", "Kapal Drebbel"),
            mk(2, icon_turtle(), "1776", "Turtle"),
            mk(3, Sub(color=MIST, portholes=False).scale(0.34), "1914–1918", "U-boat"),
            mk(4, Sub(color=MINT, portholes=False).scale(0.34), "1954", "USS Nautilus"),
        ]

        with self.line():
            self.play(FadeIn(hdr, shift=DOWN * 0.2), Create(timeline), run_time=1.5)
        with self.line():
            self.play(FadeIn(items[0], shift=UP * 0.3), run_time=1.0)
        with self.line():
            self.play(FadeIn(items[1], shift=UP * 0.3), run_time=1.0)
        with self.line():
            self.play(FadeIn(items[2], shift=UP * 0.3), run_time=1.0)
        note = T("1 orang · tenaga otot", 22, MIST).move_to(p(0, -1.55))
        with self.line():
            self.play(Indicate(items[2][0], color=GOLD), FadeIn(note), run_time=1.5)
        with self.line():
            self.play(FadeIn(items[3], shift=UP * 0.3), run_time=1.0)
        with self.line():
            self.play(FadeIn(items[4], shift=UP * 0.3), run_time=1.0)
        months = T("Berbulan-bulan di bawah air", 34, GOLD).move_to(p(0, -1.95))
        with self.line():
            self.play(FadeOut(note), FadeIn(months, shift=UP * 0.2), Indicate(items[4][0], color=GOLD),
                      run_time=1.6)
        self.clear()


class Ch03Archimedes(NarratedScene):
    chapter_id = "ch03"

    def construct(self):
        hdr = self.hdr(2, "Hukum Archimedes")

        water = Rectangle(width=6, height=1.3, stroke_width=0, fill_color=SEA,
                          fill_opacity=0.6).move_to(p(0, -0.6))
        hull = Polygon(p(-1.6, 0.0), p(1.6, 0.0), p(1.1, -0.55), p(-1.2, -0.55),
                       fill_color=MIST, fill_opacity=1, stroke_width=0)
        cabin = Rectangle(width=0.9, height=0.5, fill_color=INK, fill_opacity=1,
                          stroke_width=0).move_to(p(0.2, 0.28))
        chimney = Rectangle(width=0.2, height=0.35, fill_color=CORAL, fill_opacity=1,
                            stroke_width=0).move_to(p(0.2, 0.68))
        ship = VGroup(hull, cabin, chimney).move_to(p(0, 0.15))
        q = T("?", 90, GOLD).move_to(p(2.8, 1.1))

        with self.line():
            self.play(FadeIn(hdr), FadeIn(water), FadeIn(ship, shift=DOWN * 0.2), run_time=1.2)
            self.play(Write(q), run_time=0.8)

        law = T("Hukum Archimedes", 56, GOLD, weight=BOLD).move_to(p(0, 0.6))
        with self.line():
            self.play(FadeOut(VGroup(water, ship, q)), run_time=0.6)
            self.play(Write(law), run_time=1.2)

        stmt = box("Gaya apung = berat air yang dipindahkan", w=9.4, h=1.1, color=GOLD, size=34)
        stmt.move_to(p(0, -0.2))
        with self.line():
            self.play(law.animate.move_to(p(0, 1.4)).scale(0.7), run_time=0.8)
            self.play(FadeIn(stmt, shift=UP * 0.2), run_time=1.0)

        def tank_unit(cx, block_y, w_len, f_len):
            frame = Rectangle(width=3.0, height=3.2, stroke_color=MIST, stroke_width=3).move_to(p(cx, 0.15))
            wat = Rectangle(width=2.94, height=2.4, stroke_width=0, fill_color=SEA, fill_opacity=0.6)
            wat.move_to(frame.get_bottom() + UP * 1.23)
            blk = Square(side_length=0.5, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(p(cx, block_y))
            up = arr(p(cx, block_y + 0.25), p(cx, block_y + 0.25 + f_len), MINT)
            dn = arr(p(cx, block_y - 0.25), p(cx, block_y - 0.25 - w_len), CORAL)
            fl = T("F", 26, MINT).next_to(up, RIGHT, buff=0.1)
            wl = T("W", 26, CORAL).next_to(dn, RIGHT, buff=0.1)
            return VGroup(frame, wat), VGroup(blk, up, dn, fl, wl)

        tA, uA = tank_unit(-4.4, -0.55, 0.45, 0.2)   # tenggelam
        tB, uB = tank_unit(0.0, -0.10, 0.35, 0.35)   # melayang
        tC, uC = tank_unit(4.4, 0.40, 0.2, 0.45)     # naik
        with self.line():
            self.play(FadeOut(stmt), FadeOut(law), run_time=0.6)
            self.play(FadeIn(VGroup(tA, tB, tC)), run_time=0.8)
            self.play(FadeIn(VGroup(uA, uB, uC)), run_time=1.0)

        labels = [T("Tenggelam\nW > F", 24, CORAL).move_to(p(-4.4, -1.95)),
                  T("Melayang\nW = F", 24, GOLD).move_to(p(0, -1.95)),
                  T("Naik\nF > W", 24, MINT).move_to(p(4.4, -1.95))]
        with self.line():
            self.play(uA.animate.shift(DOWN * 0.3), uC.animate.shift(UP * 0.25),
                      LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.5), run_time=3.5)

        ring = SurroundingRectangle(tB, color=GOLD, buff=0.1)
        with self.line():
            self.play(Create(ring),
                      Transform(labels[1], T("Daya apung netral\nW = F", 24, GOLD).move_to(labels[1])),
                      run_time=1.5)

        rows = [("Baja", 4.2, MIST, "≈ 7.850 kg/m³"),
                ("Air laut", 0.55, SKY, "≈ 1.025 kg/m³"),
                ("Kapal selam\n(rata-rata, diatur)", 0.55, GOLD, "≈ air laut")]
        bars = VGroup()
        for i, (name, w, col, val) in enumerate(rows):
            y = 1.0 - i * 1.05
            bar = Rectangle(width=w, height=0.5, fill_color=col, fill_opacity=0.85, stroke_width=0)
            bar.move_to(p(-1.0 + w / 2, y))
            nm = T(name, 24, INK).next_to(p(-1.15, y), LEFT, buff=0.0)
            vl = T(val, 24, col).next_to(bar, RIGHT, buff=0.25)
            bars.add(VGroup(nm, bar, vl))
        with self.line():
            self.play(FadeOut(VGroup(tA, tB, tC, uA, uB, uC, labels[0], labels[1], labels[2], ring)),
                      run_time=0.7)
            self.play(LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.5), run_time=3.5)

        how = T("Caranya: tangki ballast", 38, GOLD, weight=BOLD).move_to(p(0, -2.0))
        with self.line():
            self.play(Indicate(bars[2], color=GOLD), FadeIn(how, shift=UP * 0.2), run_time=1.6)
        self.clear()

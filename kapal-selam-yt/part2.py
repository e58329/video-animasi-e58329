"""Bagian 2: tangki ballast, kemudi & hidroplane, tekanan."""
from kit import *


class Ch04Ballast(NarratedScene):
    chapter_id = "ch04"

    def construct(self):
        hdr = self.hdr(3, "Tangki Ballast")
        sea = ocean(top=1.2, bottom=-2.3)
        front = ocean_front(top=1.2, bottom=-2.3)
        sub = Sub(internals=True).scale(0.85).move_to(p(0, 1.3))
        tl, tr = sub.tanks[0], sub.tanks[1]

        lab = T("Tangki ballast", 28, GOLD).move_to(p(-1.4, -0.5))
        pointer = arr(p(-1.4, -0.2), tl.get_bottom() + DOWN * 0.05, GOLD, 4)
        with self.line():  # 0
            self.play(FadeIn(hdr), FadeIn(sea), FadeIn(front), run_time=0.8)
            self.play(FadeIn(sub, shift=UP * 0.2), run_time=1.0)
            self.play(FadeIn(lab), GrowArrow(pointer), Indicate(sub.tanks, color=GOLD), run_time=2.0)

        air = VGroup(T("udara", 16, INK).move_to(tl), T("udara", 16, INK).move_to(tr))
        note = T("Berisi udara → ringan → mengapung", 28, GOLD).move_to(p(0, -1.4))
        with self.line():  # 1
            self.play(FadeOut(lab), FadeOut(pointer), run_time=0.4)
            self.play(FadeIn(air), FadeIn(note, shift=UP * 0.2), run_time=1.2)

        valves = VGroup(*[Dot(t.get_top(), radius=0.09, color=CORAL) for t in (tl, tr)])
        vlab = T("katup", 24, CORAL).move_to(p(-1.4, 2.35))
        vptr = arr(p(-1.4, 2.1), tl.get_top() + UP * 0.1, CORAL, 3)
        with self.line():  # 2
            self.play(FadeOut(note), FadeIn(valves), FadeIn(vlab), GrowArrow(vptr), run_time=1.2)
            self.play(Indicate(valves, color=CORAL), run_time=1.0)

        air_out = VGroup(*[arr(t.get_top() + UP * 0.4, t.get_top() + UP * 1.0, INK, 4) for t in (tl, tr)])
        out_lab = T("udara keluar", 24, INK).move_to(p(-1.4, 2.7))
        water_in = VGroup(*[arr(t.get_bottom() + DOWN * 0.9, t.get_bottom() + DOWN * 0.2, SKY, 4)
                            for t in (tl, tr)])
        in_lab = T("air laut masuk", 24, SKY).move_to(p(0, -0.15))
        with self.line():  # 3
            self.play(FadeOut(vlab), FadeOut(vptr), FadeOut(air), run_time=0.4)
            self.play(LaggedStart(*[GrowArrow(a) for a in air_out], lag_ratio=0.3),
                      LaggedStart(*[GrowArrow(a) for a in water_in], lag_ratio=0.3),
                      FadeIn(out_lab), FadeIn(in_lab), sub.fill(1.0), run_time=3.5)

        with self.line():  # 4
            self.play(FadeOut(air_out), FadeOut(water_in), FadeOut(out_lab), FadeOut(in_lab), run_time=0.5)
            self.play(sub.animate.shift(DOWN * 2.1), valves.animate.shift(DOWN * 2.1),
                      run_time=3.0, rate_func=smooth)

        status = T("Daya apung netral: melayang", 30, GOLD).move_to(p(0, 2.1))
        with self.line():  # 5
            self.play(Indicate(valves, color=CORAL), FadeIn(status, shift=UP * 0.2), run_time=1.5)
            self.play(Indicate(sub.hull, color=GOLD, scale_factor=1.03), run_time=1.5)

        c = sub.hull.get_center()
        trim = VGroup(*[Rectangle(width=0.4, height=0.2, stroke_color=MINT, stroke_width=3,
                                  fill_opacity=0).move_to(c + RIGHT * x * 0.85 + DOWN * 0.05)
                        for x in (-0.5, 0.5)])
        tw_l = Rectangle(width=0.34, height=0.16, stroke_width=0, fill_color=SKY,
                         fill_opacity=0.9).move_to(trim[0].get_bottom() + UP * 0.11)
        tw_r = Rectangle(width=0.34, height=0.01, stroke_width=0, fill_color=SKY,
                         fill_opacity=0.9).move_to(trim[1].get_bottom() + UP * 0.035)
        tw_l_new = Rectangle(width=0.34, height=0.01, stroke_width=0, fill_color=SKY,
                             fill_opacity=0.9).move_to(trim[0].get_bottom() + UP * 0.035)
        tw_r_new = Rectangle(width=0.34, height=0.16, stroke_width=0, fill_color=SKY,
                             fill_opacity=0.9).move_to(trim[1].get_bottom() + UP * 0.11)
        trim_lab = T("tangki trim", 24, MINT).next_to(sub, DOWN, buff=0.25)
        with self.line():  # 6
            self.play(Transform(status, T("Tangki trim: penyeimbang halus", 30, MINT).move_to(status)),
                      FadeIn(trim), FadeIn(tw_l), FadeIn(tw_r), FadeIn(trim_lab), run_time=1.5)
            self.play(Transform(tw_l, tw_l_new), Transform(tw_r, tw_r_new), run_time=2.5)

        bottles = VGroup(*[RoundedRectangle(corner_radius=0.12, width=0.38, height=1.0, fill_color=GOLD,
                                            fill_opacity=0.9, stroke_width=0) for _ in range(3)])
        bottles.arrange(RIGHT, buff=0.12).move_to(p(-5.4, -0.8))
        blab = T("udara bertekanan", 24, GOLD).next_to(bottles, DOWN, buff=0.2)
        to_tank = arr(bottles.get_right() + RIGHT * 0.1, sub.hull.get_left() + LEFT * 0.55, GOLD, 4)
        with self.line():  # 7
            self.play(FadeOut(VGroup(trim, tw_l, tw_r, trim_lab)), FadeOut(status), run_time=0.5)
            self.play(FadeIn(bottles), FadeIn(blab), GrowArrow(to_tank), run_time=1.5)

        push = VGroup(*[arr(t.get_bottom(), t.get_bottom() + DOWN * 0.6, SKY, 4) for t in (tl, tr)])
        with self.line():  # 8
            self.play(sub.fill(0.0), LaggedStart(*[GrowArrow(a) for a in push], lag_ratio=0.3), run_time=2.5)
            self.play(FadeOut(push), FadeOut(bottles), FadeOut(blab), FadeOut(to_tank), run_time=0.5)
            self.play(sub.animate.shift(UP * 2.1), valves.animate.shift(UP * 2.1),
                      run_time=3.0, rate_func=smooth)

        last = T("Setiap kilogram harus dihitung dengan teliti", 32, GOLD).move_to(p(0, -1.6))
        with self.line():  # 9
            self.play(FadeIn(last, shift=UP * 0.2), run_time=1.2)
        self.clear()


class Ch05Planes(NarratedScene):
    chapter_id = "ch05"

    def construct(self):
        hdr = self.hdr(4, "Kemudi dan Hidroplane")
        top = top_sub().move_to(p(-3.4, 0.4))
        side = Sub(portholes=False).scale(0.55).move_to(p(3.6, 0.4))
        t_top = T("Tampak atas", 24, MIST).move_to(p(-3.4, 1.9))
        t_side = T("Tampak samping", 24, MIST).move_to(p(3.6, 1.9))

        with self.line():  # 0
            self.play(FadeIn(hdr), run_time=0.6)
            self.play(FadeIn(top), FadeIn(side), FadeIn(t_top), FadeIn(t_side), run_time=1.5)

        pivot = top.rudder.get_right()
        rl = T("Kemudi vertikal", 24, GOLD).move_to(p(-3.4, -1.0))
        with self.line():  # 1
            self.play(FadeIn(rl), top.rudder.animate.rotate(28 * DEGREES, about_point=pivot), run_time=1.5)
            self.play(Rotate(top, angle=18 * DEGREES), run_time=2.0)

        box_s = SurroundingRectangle(side.stern_plane, color=GOLD, buff=0.08)
        box_b = SurroundingRectangle(side.sail_plane, color=GOLD, buff=0.08)
        hp = T("Hidroplane", 26, GOLD).move_to(p(3.6, 1.5))
        with self.line():  # 2
            self.play(Create(box_s), Create(box_b), FadeIn(hp), run_time=1.5)

        hb = side.hull.get_bottom()
        flow = VGroup(*[arr(hb + RIGHT * 1.3 + DOWN * (0.2 + 0.2 * i), hb + LEFT * 0.2 + DOWN * (0.2 + 0.2 * i),
                            SKY, 3) for i in range(3)])
        flow_lab = T("aliran air", 22, SKY).move_to(p(3.6, -1.0))
        tip = side.stern_plane.get_left()
        with self.line():  # 3
            self.play(FadeOut(box_s), FadeOut(box_b), LaggedStart(*[GrowArrow(a) for a in flow], lag_ratio=0.3),
                      FadeIn(flow_lab), run_time=1.5)
            self.play(side.stern_plane.animate.rotate(-20 * DEGREES, about_point=side.stern_plane.get_right()),
                      run_time=1.2)
            force = arr(tip + UP * 0.1, tip + DOWN * 0.55, CORAL, 4)
            self.play(GrowArrow(force), run_time=0.8)

        with self.line():  # 4
            self.play(FadeOut(flow), FadeOut(flow_lab), FadeOut(force), run_time=0.4)
            self.play(Rotate(side, angle=12 * DEGREES), run_time=1.3)
            self.play(Rotate(side, angle=-24 * DEGREES), run_time=1.6)

        card = T("Diam atau pelan → ballast dan trim yang bekerja", 30, GOLD)
        fit(card, 12.5).move_to(p(0, -1.9))
        with self.line():  # 5
            self.play(FadeIn(card, shift=UP * 0.2), run_time=1.5)
        self.clear()


class Ch06Pressure(NarratedScene):
    chapter_id = "ch06"

    def construct(self):
        def yd(d):
            return 2.1 - d * 0.0125

        hdr = self.hdr(5, "Melawan Tekanan")
        col = Rectangle(width=1.2, height=3.75, stroke_color=SKY, stroke_width=3, fill_color=SEA,
                        fill_opacity=0.5).move_to(p(-4.8, 0.225))
        depth_labs = VGroup(*[T(f"{d} m", 24, INK).move_to(p(-6.25, yd(d))) for d in (0, 100, 200, 300)])
        ticks = VGroup(*[Line(p(-5.4, yd(d)), p(-5.2, yd(d)), color=INK, stroke_width=3)
                         for d in (0, 100, 200, 300)])
        atm_labs = VGroup(*[T(f"{1 + d // 10} atm", 24, GOLD).move_to(p(-3.0, yd(d)))
                            for d in (0, 100, 200, 300)])

        big_t = T("TEKANAN", 64, GOLD, weight=BOLD).move_to(p(2.4, 0.5))
        with self.line():  # 0
            self.play(FadeIn(hdr), FadeIn(col), run_time=1.0)
            self.play(Write(big_t), run_time=1.2)

        rule = T("+1 atm tiap 10 m", 36, GOLD).move_to(p(2.4, 1.2))
        with self.line():  # 1
            self.play(FadeOut(big_t), FadeIn(depth_labs), FadeIn(ticks), run_time=1.0)
            self.play(FadeIn(rule, shift=UP * 0.2), run_time=1.0)

        mark = Dot(p(-4.8, yd(300)), color=CORAL, radius=0.12)
        big = T("≈ 31 atm", 64, GOLD, weight=BOLD).move_to(p(2.4, 0.2))
        big_sub = T("di kedalaman 300 m", 30, INK).next_to(big, DOWN, buff=0.25)
        with self.line():  # 2
            self.play(LaggedStart(*[FadeIn(a) for a in atm_labs], lag_ratio=0.4), run_time=2.0)
            self.play(FadeOut(rule), FadeIn(mark), FadeIn(big), FadeIn(big_sub), run_time=1.2)

        sq = Square(side_length=0.8, stroke_color=GOLD, stroke_width=4, fill_color=GOLD, fill_opacity=0.2)
        sq.move_to(p(2.4, 0.9))
        sq_arrows = VGroup(
            arr(p(2.4, 2.0), p(2.4, 1.4), SKY, 4), arr(p(2.4, -0.2), p(2.4, 0.4), SKY, 4),
            arr(p(1.3, 0.9), p(1.9, 0.9), SKY, 4), arr(p(3.5, 0.9), p(2.9, 0.9), SKY, 4))
        kg = T("≈ 30 kg\ntiap 1 cm²", 34, INK).move_to(p(2.4, -1.2))
        with self.line():  # 3
            self.play(FadeOut(big), FadeOut(big_sub), run_time=0.5)
            self.play(FadeIn(sq), LaggedStart(*[GrowArrow(a) for a in sq_arrows], lag_ratio=0.2), run_time=1.5)
            self.play(FadeIn(kg, shift=UP * 0.2), run_time=1.0)

        hull = Circle(radius=1.0, stroke_color=INK, stroke_width=12, fill_color=DEEP,
                      fill_opacity=0.9).move_to(p(3.8, 0.0))
        hull_lab = T("Pressure hull", 30, GOLD).move_to(p(3.8, 2.15))
        hull_mat = T("baja bermutu tinggi\natau titanium", 24, INK).move_to(p(3.8, -2.1))
        with self.line():  # 4
            self.play(FadeOut(sq), FadeOut(sq_arrows), FadeOut(kg), run_time=0.5)
            self.play(Create(hull), FadeIn(hull_lab), FadeIn(hull_mat), run_time=2.0)

        ring = VGroup(*[
            arr(p(3.8, 0) + 1.65 * np.array([np.cos(a), np.sin(a), 0]),
                p(3.8, 0) + 1.1 * np.array([np.cos(a), np.sin(a), 0]), SKY, 4)
            for a in np.linspace(0, TAU, 12, endpoint=False)])
        sq2 = Square(side_length=1.6, stroke_color=INK, stroke_width=10, fill_color=DEEP,
                     fill_opacity=0.9).move_to(p(0.4, 0.0))
        sq2_arrows = VGroup()
        for d in (UP, DOWN, LEFT, RIGHT):
            perp = np.array([d[1], d[0], 0.0])
            for off in (-0.4, 0.4):
                sq2_arrows.add(arr(sq2.get_center() + d * 1.5 + perp * off,
                                   sq2.get_center() + d * 0.95 + perp * off, SKY, 3))
        corners = VGroup(*[Dot(sq2.get_corner(c), radius=0.1, color=CORAL) for c in (UL, UR, DL, DR)])
        weak = T("titik lemah", 22, CORAL).move_to(p(0.4, -1.65))
        with self.line():  # 5
            self.play(LaggedStart(*[GrowArrow(a) for a in ring], lag_ratio=0.08), run_time=2.0)
            self.play(FadeIn(sq2), FadeIn(sq2_arrows), FadeIn(corners), FadeIn(weak), run_time=1.5)

        uji_y, hancur_y = yd(150), yd(240)
        m_uji = VGroup(Line(p(-5.4, uji_y), p(-4.2, uji_y), color=GOLD, stroke_width=4),
                       T("uji", 24, GOLD).move_to(p(-3.5, uji_y)))
        m_han = VGroup(Line(p(-5.4, hancur_y), p(-4.2, hancur_y), color=CORAL, stroke_width=4),
                       T("hancur", 24, CORAL).move_to(p(-3.4, hancur_y)))
        secret = T("angka sebenarnya\ndirahasiakan", 26, MIST).move_to(p(0.4, 0.2))
        with self.line():  # 6
            self.play(FadeOut(atm_labs), FadeOut(mark), FadeOut(VGroup(sq2, sq2_arrows, corners, weak)),
                      run_time=0.6)
            self.play(FadeIn(m_uji), FadeIn(m_han), FadeIn(secret), run_time=1.5)

        dots = VGroup(*[Dot(p(3.8, 0) + np.array([np.cos(a), np.sin(a), 0.0]), radius=0.1, color=GOLD)
                        for a in (0.4, 1.9, 3.4, 4.6, 5.7)])
        with self.line():  # 7
            self.play(FadeOut(ring), FadeOut(secret), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.2), run_time=1.5)
            self.play(Transform(hull_mat, T("tiap sambungan & katup\ndiuji ketat", 24, INK).move_to(hull_mat)),
                      Indicate(dots, color=GOLD), run_time=1.5)
        self.clear()

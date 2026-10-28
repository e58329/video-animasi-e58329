"""Bagian 3: tenaga penggerak, pendukung kehidupan, navigasi & sonar."""
from kit import *


class Ch07Power(NarratedScene):
    chapter_id = "ch07"

    def construct(self):
        hdr = self.hdr(6, "Tenaga Penggerak")
        q = T("?", 110, GOLD).move_to(p(0, 0.3))
        with self.line():  # 0
            self.play(FadeIn(hdr), Write(q), run_time=1.5)

        lab1 = T("DIESEL-LISTRIK (konvensional)", 22, GOLD).move_to(p(0, 2.4))
        b1, a1 = flow_row(["Diesel", "Generator", "Baterai", "Motor listrik", "Baling-baling"], 1.8, SKY)
        with self.line():  # 1
            self.play(FadeOut(q), FadeIn(lab1), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(x) for pair in zip(b1, a1 + [None]) for x in pair if x is not None],
                                  lag_ratio=0.25), run_time=3.0)

        note1 = T("di permukaan / snorkel: diesel mengisi baterai", 26, MIST).move_to(p(0, 1.05))
        with self.line():  # 2
            self.play(FadeIn(note1), LaggedStart(*[Indicate(b, color=GOLD) for b in b1[:3]], lag_ratio=0.4),
                      run_time=3.0)

        with self.line():  # 3
            self.play(Transform(note1, T("menyelam: baterai → motor listrik → baling-baling (senyap)", 26, MIST)
                                .move_to(note1)),
                      b1[0].animate.set_opacity(0.3), b1[1].animate.set_opacity(0.3), run_time=1.5)
            self.play(LaggedStart(*[Indicate(b, color=GOLD) for b in b1[2:]], lag_ratio=0.4), run_time=2.0)

        with self.line():  # 4
            self.play(Transform(note1, T("baterai terbatas: beberapa hari, lalu harus diisi lagi", 26, CORAL)
                                .move_to(note1)),
                      Indicate(b1[2], color=CORAL), run_time=2.0)

        aip = box("AIP: sel bahan bakar", w=4.0, h=0.7, color=MINT, size=22).move_to(p(0, 0.3))
        with self.line():  # 5
            self.play(Transform(note1, T("AIP: tidak butuh udara dari luar", 26, MINT).move_to(note1)),
                      FadeIn(aip, shift=UP * 0.2), run_time=1.5)

        lab2 = T("TENAGA NUKLIR", 22, GOLD).move_to(p(0, -0.4))
        b2, a2 = flow_row(["Reaktor", "Uap", "Turbin", "Baling-baling"], -1.1, MINT, gap=0.9)
        with self.line():  # 6
            self.play(FadeOut(aip), FadeOut(note1), FadeIn(lab2), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(x) for pair in zip(b2, a2 + [None]) for x in pair if x is not None],
                                  lag_ratio=0.3), run_time=3.5)
            self.play(LaggedStart(*[Indicate(b, color=GOLD) for b in b2], lag_ratio=0.4), run_time=2.0)

        note2 = T("reaktor modern: puluhan tahun · batas kapal: makanan awak", 26, MIST).move_to(p(0, -2.0))
        with self.line():  # 7
            self.play(FadeIn(note2, shift=UP * 0.2), Indicate(b2[0], color=GOLD), run_time=2.0)

        prop = VGroup(*[Ellipse(width=0.9, height=0.26, fill_color=MIST, fill_opacity=1,
                                stroke_width=0).shift(RIGHT * 0.45).rotate(a, about_point=ORIGIN)
                        for a in np.linspace(0, TAU, 5, endpoint=False)])
        prop.scale(0.6).move_to(p(4.5, 0.05))
        with self.line():  # 8
            self.play(Transform(note2, T("baling-baling melengkung & miring → lebih senyap", 26, MIST)
                                .move_to(note2)), FadeIn(prop), run_time=1.0)
            self.play(Rotate(prop, angle=TAU, run_time=3.0, rate_func=linear))
        self.clear()


class Ch08Life(NarratedScene):
    chapter_id = "ch08"

    def construct(self):
        hdr = self.hdr(7, "Bertahan Hidup di Kedalaman")
        people = VGroup(*[person(1.1) for _ in range(6)]).arrange(RIGHT, buff=0.5).move_to(p(0, 0.3))
        with self.line():  # 0
            self.play(FadeIn(hdr), LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in people], lag_ratio=0.2),
                      run_time=2.5)

        # panel 1: oksigen
        t1 = T("Oksigen", 28, GOLD).move_to(p(-4.6, 2.35))
        h2o = box("H2O", w=1.9, h=0.7, color=SKY).move_to(p(-4.6, 1.5))
        elec = box("Elektrolisis", w=1.9, h=0.7, color=GOLD).move_to(p(-4.6, 0.35))
        a_e = arr(h2o.get_bottom(), elec.get_top(), INK, 3)
        bolt = T("listrik", 20, GOLD).next_to(a_e, RIGHT, buff=0.1)
        o2 = box("O2", w=1.2, h=0.7, color=MINT).move_to(p(-5.4, -0.8))
        h2 = box("H2", w=1.2, h=0.7, color=MIST).move_to(p(-3.8, -0.8))
        a_o = arr(elec.get_bottom() + LEFT * 0.4, o2.get_top(), INK, 3)
        a_h = arr(elec.get_bottom() + RIGHT * 0.4, h2.get_top(), INK, 3)
        c_o = T("dialirkan\nke kapal", 18, MIST).move_to(p(-5.4, -1.65))
        c_h = T("dibuang\nke laut", 18, MIST).move_to(p(-3.8, -1.65))
        with self.line():  # 1
            self.play(FadeOut(people), run_time=0.5)
            self.play(FadeIn(t1), FadeIn(h2o), run_time=0.8)
            self.play(GrowArrow(a_e), FadeIn(elec), FadeIn(bolt), run_time=1.5)
        with self.line():  # 2
            self.play(GrowArrow(a_o), GrowArrow(a_h), FadeIn(o2), FadeIn(h2), run_time=1.2)
            self.play(FadeIn(c_o), FadeIn(c_h), run_time=1.0)

        # panel 2: CO2
        t2 = T("Karbon dioksida", 28, GOLD).move_to(p(0, 2.35))
        co2 = box("CO2", w=1.9, h=0.7, color=CORAL).move_to(p(0, 1.5))
        scr = box("Scrubber", w=1.9, h=0.7, color=GOLD).move_to(p(0, 0.35))
        clean = box("Udara bersih", w=1.9, h=0.7, color=MINT).move_to(p(0, -0.8))
        a_c1 = arr(co2.get_bottom(), scr.get_top(), INK, 3)
        a_c2 = arr(scr.get_bottom(), clean.get_top(), INK, 3)
        with self.line():  # 3
            self.play(FadeIn(t2), FadeIn(co2), run_time=0.8)
            self.play(GrowArrow(a_c1), FadeIn(scr), run_time=1.2)
            self.play(GrowArrow(a_c2), FadeIn(clean), run_time=1.2)

        # panel 3: air tawar
        t3 = T("Air tawar", 28, GOLD).move_to(p(4.6, 2.35))
        sea = box("Air laut", w=1.9, h=0.7, color=SKY).move_to(p(4.6, 1.5))
        dist = box("Penyulingan", w=1.9, h=0.7, color=GOLD).move_to(p(4.6, 0.35))
        fresh = box("Air tawar", w=1.9, h=0.7, color=MINT).move_to(p(4.6, -0.8))
        a_w1 = arr(sea.get_bottom(), dist.get_top(), INK, 3)
        a_w2 = arr(dist.get_bottom(), fresh.get_top(), INK, 3)
        with self.line():  # 4
            self.play(FadeIn(t3), FadeIn(sea), run_time=0.8)
            self.play(GrowArrow(a_w1), FadeIn(dist), run_time=1.2)
            self.play(GrowArrow(a_w2), FadeIn(fresh), run_time=1.2)

        # giliran jaga
        clock = Circle(radius=0.9, stroke_color=INK, stroke_width=5).move_to(p(-4.3, 0.4))
        hand = Line(clock.get_center(), clock.get_center() + UP * 0.7, color=GOLD, stroke_width=6)
        bars = VGroup(*[
            VGroup(Rectangle(width=2.6, height=0.7, fill_color=c, fill_opacity=0.8, stroke_width=0),
                   T(f"Jaga {n}", 24, NAVY, weight=BOLD))
            for n, c in (("A", SKY), ("B", GOLD), ("C", MINT))])
        for b in bars:
            b[1].move_to(b[0])
        bars.arrange(RIGHT, buff=0.07).move_to(p(1.9, 0.4))
        bars_cap = T("24 jam, bergiliran", 24, MIST).move_to(p(1.9, -0.5))
        with self.line():  # 5
            self.play(*[FadeOut(m) for m in self.mobjects if m is not hdr], run_time=0.7)
            self.add(hdr)
            self.play(FadeIn(clock), FadeIn(hand), FadeIn(bars), FadeIn(bars_cap), run_time=1.0)
            self.play(Rotate(hand, angle=-TAU, about_point=clock.get_center(), run_time=3.5, rate_func=linear))

        cond = VGroup(T("Ruang sempit", 32, INK), T("Lampu buatan", 32, INK), T("Kerja bergilir", 32, INK))
        cond.arrange(RIGHT, buff=0.9).move_to(p(0, -1.5))
        with self.line():  # 6
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cond], lag_ratio=0.5), run_time=3.0)

        sel = T("Seleksi dan latihan ketat", 44, GOLD, weight=BOLD).move_to(p(0, -1.5))
        with self.line():  # 7
            self.play(FadeOut(cond), FadeIn(sel, shift=UP * 0.2), run_time=1.5)
        self.clear()


class Ch09Nav(NarratedScene):
    chapter_id = "ch09"

    def construct(self):
        hdr = self.hdr(8, "Navigasi dan Sonar")
        sea = Rectangle(width=14.2, height=4.2, stroke_width=0, fill_color=SEA, fill_opacity=0.4)
        sea.move_to(p(0, -0.2))
        wave = FunctionGraph(lambda x: 1.9 + 0.06 * np.sin(2.2 * x), x_range=[-7, 7], color=SKY, stroke_width=4)
        sub = Sub().scale(0.5).move_to(p(-4.2, -0.2))
        sat = satellite().move_to(p(4.8, 2.65))
        blocked = DashedLine(sat.get_bottom(), p(4.8, 1.95), color=GOLD)
        xmark = VGroup(Line(p(-0.2, -0.2), p(0.2, 0.2)), Line(p(-0.2, 0.2), p(0.2, -0.2))).set_stroke(CORAL, 6)
        xmark.move_to(p(4.8, 1.95))
        dark = T("cahaya hilang dalam\nbeberapa ratus meter", 22, MIST).move_to(p(4.2, -1.3))

        with self.line():  # 0
            self.play(FadeIn(hdr), FadeIn(sea), FadeIn(wave), FadeIn(sub), run_time=1.2)
            self.play(FadeIn(sat), Create(blocked), FadeIn(xmark), run_time=1.2)
            self.play(FadeIn(dark), run_time=1.0)

        q = T("?", 90, GOLD).move_to(p(-4.2, 1.2))
        with self.line():  # 1
            self.play(Write(q), run_time=1.0)

        path = VMobject().set_points_smoothly([p(-4.2, -0.2), p(-2, -1.0), p(0, -0.3), p(2, -1.1), p(3.6, -0.4)])
        trail = DashedVMobject(path, num_dashes=40).set_color(GOLD)
        gyro = VGroup(Circle(radius=0.42, stroke_color=INK, stroke_width=4),
                      Line(p(-0.42, 0), p(0.42, 0)), Line(p(0, -0.42), p(0, 0.42))).set_stroke(INK, 4)
        gyro.move_to(p(4.8, 0.6))
        gyro_lab = T("giroskop", 22, MIST).next_to(gyro, DOWN, buff=0.15)
        ins = T("Navigasi inersia = giroskop + sensor percepatan", 28, GOLD).move_to(p(0, 1.3))
        with self.line():  # 2
            self.play(FadeOut(q), FadeIn(ins), FadeIn(gyro), FadeIn(gyro_lab), run_time=1.0)
            self.play(MoveAlongPath(sub, path), Create(trail), Rotate(gyro, angle=TAU, run_time=5.0),
                      run_time=5.0, rate_func=linear)

        fix = DashedLine(sat.get_bottom(), p(3.6, 1.7), color=MINT)
        fix_lab = T("koreksi posisi", 24, MINT).move_to(p(2.3, 2.3))
        with self.line():  # 3
            self.play(FadeOut(blocked), FadeOut(xmark), FadeOut(ins), FadeOut(gyro), FadeOut(gyro_lab),
                      FadeOut(trail), run_time=0.6)
            self.play(sub.animate.move_to(p(3.6, 1.45)), run_time=1.8)
            self.play(Create(fix), FadeIn(fix_lab), run_time=1.2)

        rock = Polygon(p(3.2, -1.0), p(3.6, -0.2), p(4.2, 0.1), p(4.9, -0.3), p(5.1, -1.0),
                       fill_color=MIST, fill_opacity=1, stroke_width=0)
        sonar_t = T("SONAR = Sound Navigation And Ranging", 32, GOLD).move_to(p(0, 1.5))
        with self.line():  # 4
            self.play(FadeOut(sat), FadeOut(fix), FadeOut(fix_lab), FadeOut(dark), run_time=0.6)
            self.play(sub.animate.move_to(p(-4.5, -0.3)), FadeIn(rock), FadeIn(sonar_t), run_time=1.8)

        out_arcs = pulses(sub.get_center(), RIGHT, np.linspace(1.0, 7.5, 8), SKY)
        echo_arcs = pulses(p(3.2, -0.5), LEFT, np.linspace(1.0, 7.5, 8), MINT)
        delay = T("selang waktu gema → jarak benda", 26, MIST).move_to(p(0, 0.9))
        with self.line():  # 5
            self.play(FadeIn(delay), pulse_anim(out_arcs), run_time=2.6)
            self.play(pulse_anim(echo_arcs), run_time=2.6)

        center = sub.get_center()
        rings = [Circle(radius=0.4, stroke_color=CORAL, stroke_width=5).move_to(center) for _ in range(3)]
        act = T("sonar aktif: posisi ketahuan", 28, CORAL).move_to(p(-2.8, -1.9))
        rock_arcs = pulses(p(3.2, -0.5), LEFT, np.linspace(1.0, 7.5, 8), MINT)
        with self.line():  # 6
            self.play(FadeOut(delay), FadeIn(act), run_time=0.6)
            self.add(*rings)
            self.play(LaggedStart(*[FadeOut(c, scale=7) for c in rings], lag_ratio=0.3), run_time=2.2)
            self.play(Transform(act, T("sonar pasif: hanya mendengarkan", 28, MINT).move_to(act)),
                      pulse_anim(rock_arcs), run_time=2.8)

        silent = T("Dinas senyap (Silent Service)", 44, GOLD, weight=BOLD).move_to(p(0, 1.5))
        with self.line():  # 7
            self.play(FadeOut(sonar_t), FadeOut(act), FadeIn(silent, shift=UP * 0.2), run_time=1.2)
            self.play(Indicate(sub, color=GOLD, scale_factor=1.08), run_time=1.5)
        self.clear()

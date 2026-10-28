"""Bagian 4: jenis kapal selam, darurat, penutup, thumbnail."""
from kit import *


class Ch10Types(NarratedScene):
    chapter_id = "ch10"

    def construct(self):
        hdr = self.hdr(9, "Jenis-Jenis Kapal Selam")

        def card(cx, title, body, icon):
            frame = RoundedRectangle(corner_radius=0.2, width=3.9, height=3.3, stroke_color=MIST,
                                     stroke_width=3, fill_color=DEEP, fill_opacity=0.5).move_to(p(cx, 0.45))
            icon.move_to(p(cx, 1.2))
            ti = fit(T(title, 28, GOLD, weight=BOLD), 3.6).move_to(p(cx, 0.15))
            bo = fit(T(body, 22, INK), 3.6).move_to(p(cx, -0.55))
            return frame, VGroup(icon, ti, bo)

        f1, c1 = card(-4.4, "Kapal selam serang", "Memburu kapal lain\ndan mengintai",
                      Sub(color=BLUE, portholes=False).scale(0.38))
        f2, c2 = card(0.0, "Rudal balistik", "Patroli senyap\nsebagai penangkal",
                      Sub(color=CORAL, portholes=False).scale(0.38))
        f3, c3 = card(4.4, "Penelitian", "Dasar laut, kapal karam,\nmakhluk laut dalam", icon_alvin())

        with self.line():  # 0
            self.play(FadeIn(hdr), run_time=0.6)
            self.play(LaggedStart(FadeIn(f1), FadeIn(f2), FadeIn(f3), lag_ratio=0.3), run_time=1.5)
        with self.line():  # 1
            self.play(FadeIn(c1, shift=UP * 0.2), run_time=1.2)
        with self.line():  # 2
            self.play(FadeIn(c2, shift=UP * 0.2), run_time=1.2)
        with self.line():  # 3
            self.play(FadeIn(c3, shift=UP * 0.2), run_time=1.2)
        ex = T("Contoh: Alvin · menjelajah reruntuhan Titanic", 28, GOLD).move_to(p(0, -1.9))
        with self.line():  # 4
            self.play(Indicate(f3, color=GOLD, scale_factor=1.04), FadeIn(ex, shift=UP * 0.2), run_time=1.6)
        size = T("Dari 2 awak hingga lebih dari 100 meter", 28, INK).move_to(p(0, -1.9))
        with self.line():  # 5
            self.play(Transform(ex, size), run_time=1.2)
        self.clear()


class Ch11Emergency(NarratedScene):
    chapter_id = "ch11"

    def construct(self):
        hdr = self.hdr(10, "Keadaan Darurat")
        sea = ocean(top=1.6, bottom=-2.3)
        front = ocean_front(top=1.6, bottom=-2.3)
        seabed = Polygon(p(-6.6, -2.3), p(-6.6, -1.75), p(-4, -1.9), p(-1, -1.7), p(2, -1.85),
                         p(5, -1.72), p(6.6, -1.9), p(6.6, -2.3),
                         fill_color="#3E2F23", fill_opacity=1, stroke_width=0)
        sub = Sub(internals=True).scale(0.8).move_to(p(0, -0.9))
        sub.water.become(sub.water_at(1.0))
        alarm = Dot(sub.sail.get_center(), radius=0.12, color=CORAL)
        bang = T("!", 90, CORAL, weight=BOLD).move_to(p(-3.5, 0.7))

        with self.line():  # 0
            self.play(FadeIn(hdr), FadeIn(sea), FadeIn(front), FadeIn(seabed), FadeIn(sub), run_time=1.0)
            self.play(FadeIn(alarm), Write(bang), run_time=0.5)
            self.play(Indicate(alarm, color=CORAL, scale_factor=2.0), run_time=0.6)

        air_lab = T("udara bertekanan ditiup ke semua tangki", 26, GOLD).move_to(p(0, 2.2))
        tl, tr = sub.tanks[0], sub.tanks[1]
        blow = VGroup(*[arr(t.get_top() + UP * 0.9, t.get_top() + UP * 0.15, GOLD, 4) for t in (tl, tr)])
        with self.line():  # 1
            self.play(FadeOut(alarm), FadeOut(bang), FadeIn(air_lab), LaggedStart(
                *[GrowArrow(a) for a in blow], lag_ratio=0.3), run_time=1.5)
            self.play(sub.fill(0.0), run_time=2.0)
            self.play(FadeOut(blow), sub.animate.shift(UP * 1.2), run_time=2.5, rate_func=smooth)

        weights = VGroup(*[Rectangle(width=0.55, height=0.2, fill_color=MIST, fill_opacity=1, stroke_width=0)
                           .move_to(sub.hull.get_bottom() + RIGHT * dx + UP * 0.05) for dx in (-0.6, 0.6)])
        w_lab = T("pemberat darurat dilepas", 26, MIST).move_to(p(0, 2.2))
        with self.line():  # 2
            self.play(Transform(air_lab, w_lab), FadeIn(weights), run_time=1.0)
            self.play(weights.animate.shift(DOWN * 1.2).set_opacity(0.0), sub.animate.shift(UP * 0.6),
                      run_time=2.5)

        stuck = Sub(portholes=True).scale(0.8).move_to(p(0, -0.9))
        stuck_lab = T("kapal tidak bisa naik", 28, CORAL).move_to(p(0, 2.2))
        with self.line():  # 3
            self.play(FadeOut(sub), FadeOut(weights), Transform(air_lab, stuck_lab), FadeIn(stuck), run_time=1.2)
            hatch_pt = stuck.sail.get_top()
            crew = person(0.8).move_to(hatch_pt + UP * 0.1)
            bubbles = VGroup(*[Circle(radius=0.05 + 0.02 * (i % 3), stroke_color=SKY, stroke_width=2)
                               .move_to(hatch_pt + UP * (0.3 + 0.15 * i) + RIGHT * (0.15 if i % 2 else -0.15))
                               for i in range(4)])
            self.play(FadeIn(crew), run_time=0.6)
            self.play(crew.animate.shift(UP * 2.2), LaggedStart(*[FadeIn(b) for b in bubbles], lag_ratio=0.3),
                      run_time=4.0, rate_func=linear)
            slow = T("naik perlahan", 24, SKY).move_to(p(2.2, 1.0))
            self.play(FadeIn(slow), run_time=0.6)

        rescue = Sub(color=GOLD, portholes=False).scale(0.28).move_to(p(5.5, 0.4))
        r_lab = T("kendaraan penyelamat", 26, GOLD).move_to(p(0, 2.2))
        with self.line():  # 4
            self.play(FadeOut(crew), FadeOut(bubbles), FadeOut(slow), Transform(air_lab, r_lab),
                      FadeIn(rescue), run_time=1.0)
            self.play(rescue.animate.move_to(stuck.sail.get_top() + UP * 0.35 + RIGHT * 0.2), run_time=3.0)
            link = DashedLine(rescue.get_bottom(), stuck.sail.get_top(), color=GOLD)
            self.play(Create(link), run_time=0.8)

        drill = T("Latihan berulang kali\n= awak tahu persis langkahnya", 36, GOLD, weight=BOLD)
        drill.move_to(p(0, 0.2))
        with self.line():  # 5
            self.play(*[FadeOut(m) for m in self.mobjects if m is not hdr], run_time=0.7)
            self.play(Write(drill), run_time=2.0)
        self.clear()


class Ch12Outro(NarratedScene):
    chapter_id = "ch12"

    def construct(self):
        hdr = self.hdr(None, "Rangkuman")

        def rcard(cx, cy, title, body, color):
            fr = RoundedRectangle(corner_radius=0.18, width=3.2, height=1.6, stroke_color=color,
                                  stroke_width=3, fill_color=color, fill_opacity=0.12).move_to(p(cx, cy))
            ti = fit(T(title, 24, color, weight=BOLD), 2.9).move_to(p(cx, cy + 0.35))
            bo = fit(T(body, 18, INK), 2.9).move_to(p(cx, cy - 0.25))
            return VGroup(fr, ti, bo)

        cards = [
            rcard(-5.1, 1.0, "Hukum Archimedes", "apung · melayang\ntenggelam", GOLD),
            rcard(-1.7, 1.0, "Tangki ballast", "mengatur berat\nnaik & turun", SKY),
            rcard(1.7, 1.0, "Hidroplane", "mengatur arah\nsaat bergerak", MINT),
            rcard(5.1, 1.0, "Lambung tekan", "menahan tekanan\nlaut dalam", CORAL),
            rcard(-3.4, -0.9, "Tenaga", "baterai atau\nreaktor nuklir", GOLD),
            rcard(0.0, -0.9, "Sonar", "mata dan telinga\ndi bawah air", SKY),
            rcard(3.4, -0.9, "Penunjang hidup", "oksigen, air tawar,\nawak terlatih", MINT),
        ]
        with self.line():  # 0
            self.play(FadeIn(hdr, shift=DOWN * 0.2), run_time=1.0)
        with self.line():  # 1
            self.play(FadeIn(cards[0], shift=UP * 0.2), run_time=1.0)
        with self.line():  # 2
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards[1:4]], lag_ratio=0.5), run_time=3.5)
        with self.line():  # 3
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards[4:]], lag_ratio=0.5), run_time=3.5)

        sea = ocean(top=0.2, bottom=-2.3)
        sub = Sub().scale(0.8).move_to(p(0, -0.8))
        wrap = T("Fisika sederhana · rekayasa luar biasa", 40, GOLD, weight=BOLD).move_to(p(0, 1.6))
        with self.line():  # 4
            self.play(*[FadeOut(c) for c in cards], run_time=0.6)
            self.play(FadeIn(sea), FadeIn(sub, shift=UP * 0.3), FadeIn(wrap), run_time=1.5)
            self.play(sub.animate.shift(DOWN * 0.5), run_time=3.0)

        cta = VGroup(box("LIKE", w=3.0, h=1.0, color=SKY, size=32),
                     box("SUBSCRIBE", w=3.6, h=1.0, color=CORAL, size=32),
                     box("KOMENTAR", w=3.4, h=1.0, color=MINT, size=32)).arrange(RIGHT, buff=0.5)
        cta.move_to(p(0, 0.6))
        ask = T("Benda apa yang ingin kamu ketahui cara kerjanya?", 32, GOLD).move_to(p(0, -1.0))
        fit(ask, 12.5)
        with self.line():  # 5
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in cta], lag_ratio=0.4), run_time=2.0)
            self.play(FadeIn(ask, shift=UP * 0.2), run_time=1.2)

        bye = T("Sampai jumpa!", 64, INK, weight=BOLD).move_to(p(0, 0.9))
        series = T("SERI · " + cfg.SERIES.upper(), 26, GOLD).move_to(p(0, -0.1))
        with self.line():  # 6
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
            self.play(Write(bye), FadeIn(series), run_time=1.6)

        # end screen ~6 detik: tempat elemen video/subscribe YouTube
        slot_l = RoundedRectangle(corner_radius=0.15, width=4.2, height=2.4, stroke_color=MIST, stroke_width=3)
        slot_r = slot_l.copy()
        slot_l.move_to(p(-3.4, -1.0))
        slot_r.move_to(p(3.4, -1.0))
        self.play(bye.animate.shift(UP * 0.9), series.animate.shift(UP * 0.9),
                  FadeIn(slot_l), FadeIn(slot_r), run_time=1.0)
        self.wait(5)
        self.clear(1.0)


class Thumb(Scene):
    """Thumbnail 1920x1080:  python build.py thumb"""

    def construct(self):
        sea = ocean(top=-0.6, bottom=-4.0, width=16, opacity=0.6)
        sub = Sub(portholes=True).scale(1.35).move_to(p(2.2, -1.8))
        t1 = T("BAGAIMANA", 96, INK, weight=BOLD).move_to(p(-3.2, 2.5))
        t2 = T("KAPAL SELAM", 96, GOLD, weight=BOLD).move_to(p(-2.6, 1.2))
        t3 = T("BEKERJA?", 96, INK, weight=BOLD).move_to(p(-3.1, -0.1))
        tag = T("Fisika di balik raksasa bawah laut", 34, MIST).move_to(p(-2.4, -1.2))
        self.add(sea, sub, t1, t2, t3, tag)

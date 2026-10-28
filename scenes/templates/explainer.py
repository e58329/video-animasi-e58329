from manim import *
from scenes.base_scene import BaseScene

class ExplainerScene(BaseScene):
    def construct(self):
        background = Rectangle(
            width=config.frame_width, height=config.frame_height,
            fill_color="#0F172A", fill_opacity=1, stroke_width=0
        )
        self.add(background)

        self.intro()
        
        total_duration = self.data.get("audio_duration", 60.0)
        # Kita tidak memakai wait yang panjang di sini, karena animasi visualnya yang akan memakan waktu
        
        # 1. Judul
        title = Text(self.data["title"], font_size=44, weight=BOLD, color=WHITE)
        title.to_edge(UP, buff=1)
        title_box = SurroundingRectangle(title, color=BLUE, buff=0.2, corner_radius=0.1)
        title_box.set_fill(BLUE, opacity=0.2)
        self.play(DrawBorderThenFill(title_box), Write(title), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(title_box), FadeOut(title), run_time=1)

        # 2. Pertanyaan
        question = Text(self.data["question"], font_size=28, color=YELLOW)
        question.set_width(12).to_edge(UP, buff=2)
        self.play(FadeIn(question, shift=DOWN), run_time=1.5)
        self.wait(3)
        self.play(FadeOut(question), run_time=1)

        # 3. Proses Bab dan Visual
        for section in self.data.get("sections", []):
            heading = Text(section["heading"], font_size=36, color=BLUE, weight=BOLD)
            heading.to_edge(UP, buff=1)
            self.play(Write(heading), run_time=1)
            self.wait(1)

            for point in section.get("points", []):
                text = point["text"]
                visual_type = point.get("visual", "default")
                
                # Tampilkan Teks
                bullet = Text(text, font_size=24, color=WHITE)
                bullet.set_width(11).next_to(heading, DOWN, buff=1)
                self.play(FadeIn(bullet, shift=RIGHT), run_time=1)
                self.wait(1)

                # --- GAMBAR VISUAL BERDASARKAN KODE ---
                if visual_type == "history_ancient":
                    # Lonceng kaca
                    bell = Arc(radius=1, start_angle=0, angle=PI, color=BLUE, fill_opacity=0.3)
                    bell.next_to(bullet, DOWN, buff=0.5)
                    self.play(Create(bell), run_time=1.5)
                elif visual_type == "history_wood":
                    # Kapal kayu sederhana
                    hull = Polygon([-2,0,0], [2,0,0], [1.5,-1,0], [-1.5,-1,0], color=BROWN, fill_opacity=0.8)
                    hull.next_to(bullet, DOWN, buff=0.5)
                    self.play(DrawBorderThenFill(hull), run_time=1.5)
                elif visual_type == "history_modern":
                    # Kapal selam modern
                    sub = Ellipse(width=3, height=1, color=GRAY, fill_opacity=0.8)
                    tower = Rectangle(width=0.6, height=0.4, color=GRAY, fill_opacity=0.8).next_to(sub, UP, buff=0)
                    sub_group = VGroup(sub, tower).next_to(bullet, DOWN, buff=0.5)
                    self.play(DrawBorderThenFill(sub_group), run_time=1.5)
                elif visual_type == "archimedes_law" or visual_type == "archimedes_float":
                    # Air dan benda
                    water = Rectangle(width=4, height=1.5, color=BLUE, fill_opacity=0.4)
                    water.next_to(bullet, DOWN, buff=0.5)
                    block = Square(side_length=0.5, color=YELLOW, fill_opacity=1)
                    block.next_to(water, UP, buff=0)
                    self.play(FadeIn(water), DrawBorderThenFill(block), run_time=1.5)
                    # Animasi mengapung
                    self.play(block.animate.shift(UP * 0.3), run_time=1)
                elif visual_type == "ballast_tank" or visual_type == "water_in" or visual_type == "air_in":
                    # Tangki pemberat
                    tank = Rectangle(width=3, height=1, color=WHITE, fill_opacity=0.1)
                    tank.next_to(bullet, DOWN, buff=0.5)
                    self.play(Create(tank), run_time=1)
                    if visual_type == "water_in":
                        # Air masuk
                        water_fill = Rectangle(width=2.9, height=0.9, color=BLUE, fill_opacity=0.6).move_to(tank)
                        self.play(FadeIn(water_fill), run_time=1.5)
                    elif visual_type == "air_in":
                        # Udara masuk
                        air_fill = Rectangle(width=2.9, height=0.9, color=WHITE, fill_opacity=0.6).move_to(tank)
                        self.play(FadeIn(air_fill), run_time=1.5)
                elif visual_type == "sinking":
                    # Animasi tenggelam
                    arrow = Arrow(start=UP, end=DOWN, color=RED).next_to(bullet, DOWN, buff=0.5)
                    self.play(GrowArrow(arrow), run_time=1)
                
                # Tunggu sesuai durasi audio (estimasi)
                # Karena kita tidak pakai auto-subs untuk timing, kita beri waktu statis
                self.wait(3) 
                
                # Hapus visual dan teks sebelum lanjut ke poin berikutnya
                self.play(FadeOut(bullet), *[FadeOut(m) for m in self.mobjects if m != heading], run_time=1)

            self.play(FadeOut(heading), run_time=1)

        # 4. Kesimpulan
        conclusion_box = RoundedRectangle(corner_radius=0.2, width=12, height=2, color=YELLOW, fill_opacity=0.1)
        conclusion_box.to_edge(DOWN, buff=1)
        conclusion = Text(self.data["conclusion"], font_size=26, color=YELLOW, weight=BOLD)
        conclusion.move_to(conclusion_box.get_center()).set_width(11)
        self.play(FadeIn(conclusion_box), Write(conclusion), run_time=2)
        self.wait(4)
        self.play(FadeOut(conclusion_box), FadeOut(conclusion))
        self.outro()

def build_scene(data, config):
    return ExplainerScene(data=data, config=config)

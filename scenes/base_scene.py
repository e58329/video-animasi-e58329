from manim import *

class BaseScene(Scene):
    def __init__(self, data, config, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.config = config
        self.brand = config["branding"]

    def intro(self):
        title = Text(self.brand["channel_name"], font_size=48, color=self.brand["primary_color"])
        self.play(Write(title), run_time=1)
        self.play(FadeOut(title), run_time=0.5)

    def outro(self):
        cta = Text("Subscribe untuk episode berikutnya", font_size=32, color=self.brand["accent_color"])
        self.play(FadeIn(cta), run_time=0.8)
        self.play(FadeOut(cta), run_time=0.5)

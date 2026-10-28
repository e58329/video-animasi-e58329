import sys
import os
import yaml
import importlib
import shutil
from pathlib import Path
from manim import config as manim_config

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
ROOT = Path(__file__).resolve().parent.parent

def render(yaml_path):
    with open(ROOT / "config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    w, h = cfg["video"]["resolution"].split(",")
    manim_config.pixel_width = int(w)
    manim_config.pixel_height = int(h)
    manim_config.frame_rate = cfg["video"]["fps"]
    
    # Set nama output
    manim_config.output_file = "ExplainerScene"

    template_name = data.get("template", "explainer")
    module = importlib.import_module(f"scenes.templates.{template_name}")
    scene_class = module.build_scene(data, cfg)

    scene_class.render()
    
    # --- TRIK PENYELAMAT ---
    # Manim menyimpan video di folder media. Kita cari dan salin ke folder utama.
    # Path ini mengikuti settingan Manim secara default
    video_manim = "media/videos/1080p30/ExplainerScene.mp4"
    
    if os.path.exists(video_manim):
        shutil.copy(video_manim, "ExplainerScene.mp4")
        print("✅ Video berhasil disalin ke folder utama.")
    else:
        print("⚠️ File video Manim tidak ditemukan di folder media.")

    print("Selesai!")

if __name__ == "__main__":
    render(sys.argv[1])

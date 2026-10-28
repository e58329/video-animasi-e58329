from pymotion import Composition, ColorClip, TextClip, Track

# 1. Setup Komposisi
comp = Composition(width=1080, height=1920, fps=30, duration=5)

# 2. Background Laut (Biru)
bg_track = Track(name="bg")
bg = ColorClip(color="#0B2E43")
bg.set_duration(5)
bg_track.add(bg)

# 3. Daratan (Hijau)
content_track = Track(name="content")
land = ColorClip(color="#6A9C78")
land.set_duration(5)
land.set_position(300.0, 0.0)
land.set_expression("rotation", lambda ctx: -30.0)
content_track.add(land)

# 4. Teks Judul
text_track = Track(name="text")
title = TextClip("Dari Medan menuju Nias", font="Arial", size=80.0, color="#FFFFFF")
title.set_duration(5)
title.set_position(-200.0, -600.0)
text_track.add(title)

# 5. Pesawat (Kotak Putih)
plane_track = Track(name="plane")
plane = ColorClip(color="#FFFFFF")
plane.set_duration(5)
plane.set_position(100.0, 600.0)
plane_track.add(plane)

# 6. Assemble
comp.add_track(bg_track)
comp.add_track(content_track)
comp.add_track(text_track)
comp.add_track(plane_track)

# 7. Render
comp.render("output_test_motion.mp4")
print("✅ Berhasil render: output_test_motion.mp4")

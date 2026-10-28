from pymotion import Composition, ColorClip, TextClip, Track

def buat_animasi_peta(output_path, judul_teks="Dari Medan menuju Nias", durasi=5):
    print(f"⏳ Membuat motion graphics: {judul_teks}...")
    
    comp = Composition(width=1080, height=1920, fps=30, duration=durasi)

    bg_track = Track(name="bg")
    bg = ColorClip(color="#0B2E43")
    bg.set_duration(durasi)
    bg_track.add(bg)

    content_track = Track(name="content")
    land = ColorClip(color="#6A9C78")
    land.set_duration(durasi)
    land.set_position(300.0, 0.0)
    land.set_expression("rotation", lambda ctx: -30.0)
    content_track.add(land)

    text_track = Track(name="text")
    title = TextClip(judul_teks, font="Arial", size=80.0, color="#FFFFFF")
    title.set_duration(durasi)
    title.set_position(-200.0, -600.0)
    text_track.add(title)

    plane_track = Track(name="plane")
    plane = ColorClip(color="#FFFFFF")
    plane.set_duration(durasi)
    plane.set_position(100.0, 600.0)
    plane_track.add(plane)

    comp.add_track(bg_track)
    comp.add_track(content_track)
    comp.add_track(text_track)
    comp.add_track(plane_track)

    comp.render(output_path)
    print(f"✅ Motion graphics tersimpan di: {output_path}")
    return output_path

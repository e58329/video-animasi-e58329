# fix_all.py — tambal explainer.py + studio.py (aman dijalankan berulang)
# Jalankan dari root repo: python3 fix_all.py
import ast


def patch(path, pairs):
    s = open(path, encoding="utf-8").read()
    ok, skip = 0, 0
    for old, new in pairs:
        if old in s:
            s = s.replace(old, new)
            ok += 1
        elif new in s:
            skip += 1  # sudah pernah dipatch
        else:
            print("  !! TIDAK KETEMU di %s: %s" % (path, old[:48]))
    open(path, "w", encoding="utf-8").write(s)
    ast.parse(s)
    print("%s: %d diubah, %d sudah oke" % (path, ok, skip))
    return ok + skip == len(pairs)


EXPL = [
    # 1. margin anti-potong: rounding frame manim diserap buffer 4 detik
    ("target = adur + 0.6", "target = adur + 4.0"),
    # 2. teks penutup muat penuh (7 baris), bukan dipotong jadi 4 baris + ...
    ("clines = _wrap(c_text, 62, 4)", "clines = _wrap(c_text, 72, 7)"),
    ("size=25, color=accent, bold=False", "size=21, color=accent, bold=False"),
    ("corner_radius=0.22, width=12.6, height=3.2",
     "corner_radius=0.22, width=13.0, height=4.3"),
    (".arrange(DOWN, buff=0.18).move_to(cbox.get_center())",
     ".arrange(DOWN, buff=0.15).move_to(cbox.get_center())"),
    # 3. ekor video: outro CTA tetap terlihat penuh walau ada buffer 4 detik
    ('self.play(FadeOut(cta), FadeOut(sub2["all"]), run_time=0.8)\n\n'
     '        self.wait(0.3)',
     'self.play(FadeOut(cta), FadeOut(sub2["all"]), run_time=0.8)\n\n'
     '        self.wait(4.3)'),
]

STUDIO = [
    # subtitle dari naskah via make_subs.py (bukan whisper yang bias typo)
    ("subprocess.run(cmd_autosubs, shell=True)",
     'subprocess.run(f"python pipeline/make_subs.py \\"{temp_yaml}\\" '
     '\\"{temp_combined}\\" \\"{out_name}\\"", shell=True)'),
]

if __name__ == "__main__":
    a = patch("scenes/templates/explainer.py", EXPL)
    b = patch("studio.py", STUDIO)
    print("SEMUA PATCH BERHASIL" if (a and b) else "ADA YANG GAGAL - screenshot ke gue")

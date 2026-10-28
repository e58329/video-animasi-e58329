# Perubahan repo ini (v2) vs repo asli

Repo ini = repo asli kalian + 4 perubahan yang sudah dipakai me-render
video final "Bagaimana Kapal Selam Bekerja" (9:33, 1080p30).

## Daftar perubahan

1. **scenes/templates/explainer.py** — diganti total (v2)
   - 39 visual khusus episode kapal selam (potongan kapal, ballast tank,
     sonar, periskop, gauge tekanan, dll) dengan gaya stickman brand
   - Engine timing presisi: durasi video mengikuti durasi audio + buffer 4 detik
     -> ekor VO tidak lagi terpotong
   - Teks penutup wrap 7 baris, font 21, box 13.0x4.3 (muat kalimat panjang)

2. **pipeline/make_subs.py** — file BARU
   - Subtitle DITETASKAN dari naskah lewat word-boundary edge-tts
     (bukan tebakan whisper) -> nol typo, tanda baca dipulihkan dari naskah
   - Cue dipecah di akhir kalimat, styling kuning #FFC107 bold Montserrat

3. **studio.py** — 1 baris diubah
   - Auto-subs whisper diganti panggil `pipeline/make_subs.py`

4. **content/cara_kerja_kapal_selam.yaml** — diperbarui
   - "lo" -> "kamu", typo diperbaiki ("gemanya", "penyakit penyelaman")

File lain (config.yaml, render.py, base_scene.py, assets, dll) TIDAK diubah.

## Cara pakai

Timpa repo lama dengan isi folder ini (atau salin 4 file di atas ke repo),
lalu render seperti biasa:

    pip install manim edge-tts        # jika belum ada
    python studio.py

Catatan: dependency eksternal `auto-subs` (whisper) TIDAK dipakai lagi,
jadi satu dependensi lebih sedikit. Output: final_cara_kerja_kapal_selam.mp4
(~9.5 menit).

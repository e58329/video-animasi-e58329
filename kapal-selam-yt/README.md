# Bagaimana Kapal Selam Bekerja — video explainer (Python + Manim)

Struktur video (~9-10 menit): hook → prolog subscribe → 10 bab isi → rangkuman, CTA, dan end screen.

## Alur cepat
```bash
python build.py info          # cek jumlah kata & estimasi durasi
python build.py tts           # suara per kalimat (cache) + manifest durasi
make preview ONLY=ch04        # render 480p satu bab untuk cek animasi
python build.py all           # tts + render 1080p + subtitle + gabung + loudnorm
python build.py thumb         # thumbnail
```
Hasil di `out/`: video `.mp4` (subtitle dibakar), `.srt`, `youtube.md` (judul, deskripsi, bab, tag), `thumbnail.png`.

## Memakai TTS milikmu
Default memakai edge-tts (`pip install edge-tts`, suara id-ID-ArdiNeural). Untuk TTS sendiri:
```bash
TTS_BACKEND=cmd TTS_CMD='python my_tts.py --in {text_file} --out {out}' python build.py tts
TTS_BACKEND=py  TTS_PY='my_tts:synth' python build.py tts      # synth(text, out_path)
```
Format audio keluaran bebas; ffmpeg mengonversinya. Ganti suara/kecepatan edge: `EDGE_VOICE`, `EDGE_RATE=-5%`.

## Subtitle
Subtitle dibuat dari naskah + durasi audio sebenarnya, jadi selalu sinkron. Untuk memakai auto-sub milikmu,
cukup ganti file `.srt` di `out/` lalu jalankan ulang bagian encode (`python build.py assemble`)
atau unggah `.srt` langsung ke YouTube. Di `script_id.py`, `say` = teks untuk TTS (boleh dieja fonetik),
`sub` = teks subtitle, jadi ejaan akal-akalan TTS tidak muncul di layar.

## Mengubah isi
- Naskah: `script_id.py`. Jumlah blok `with self.line():` di scene harus sama dengan jumlah kalimat bab itu
  (dicek otomatis di akhir render).
- Animasi: `part1.py` … `part4.py`; komponen bersama di `kit.py`.
- Render akan memberi peringatan `[peringatan] ... animasi lebih lama dari narasi` jika sebuah blok kepanjangan.
- Layout: konten di y -2.3..2.6, zona bawah dikosongkan untuk subtitle. Tanpa LaTeX, hanya `Text`.
- Font: `VIDEO_FONT="Montserrat"`; font subtitle: `SUB_FONT`, `SUB_SIZE`.
- Durasi kurang dari 8 menit? `EDGE_RATE=-8%` atau `LINE_GAP=0.8`.

## Kebutuhan
Python 3.9+, Manim Community (butuh cairo & pango), ffmpeg (disarankan dengan libass untuk bakar subtitle).

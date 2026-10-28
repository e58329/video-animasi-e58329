#!/usr/bin/env python3
"""Pipeline video: naskah -> TTS -> render Manim -> subtitle SRT -> gabung & encode.

  python build.py info                 # jumlah kata & estimasi durasi (tanpa TTS/render)
  python build.py tts                  # buat audio tiap kalimat + manifest durasi
  python build.py render [--preview] [--only ch04 ch05]
  python build.py assemble [--no-burn] # gabung bab, bakar subtitle, loudnorm, tulis youtube.md
  python build.py all                  # tts + render + assemble
  python build.py thumb                # thumbnail 1920x1080
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import textwrap
import time

import cfg
import tts_adapter
from script_id import CHAPTERS, total_words


def run(cmd, **kw):
    print("\n$ " + " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def probe_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True).strip()
    return float(out.splitlines()[0])


def fmt_clock(sec):
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def pick(only):
    chs = [c for c in CHAPTERS if not only or c["id"] in only]
    if only and len(chs) != len(only):
        sys.exit(f"Bab tidak dikenal. Pilihan: {', '.join(c['id'] for c in CHAPTERS)}")
    return chs


# ---------------------------------------------------------------- info
def cmd_info(_):
    words = total_words()
    n = sum(len(c["lines"]) for c in CHAPTERS)
    est = words / 2.7 + n * cfg.LINE_GAP + 12
    print(f"{n} kalimat, {words} kata -> perkiraan {fmt_clock(est)} (asumsi 2,7 kata/detik)")
    for c in CHAPTERS:
        print(f"  {c['id']}  {c['scene']:<16} {len(c['lines']):>2} kalimat  "
              f"{sum(len(l['say'].split()) for l in c['lines']):>4} kata")
    if est < cfg.MIN_SECONDS:
        print("PERINGATAN: perkiraan di bawah 8 menit, tambah naskah atau naikkan LINE_GAP.")


# ---------------------------------------------------------------- tts
def load_manifest():
    return json.loads(cfg.MANIFEST.read_text()) if cfg.MANIFEST.exists() else {}


def cmd_tts(_):
    cfg.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    total = 0.0
    for ch in CHAPTERS:
        ch_total = 0.0
        for i, ln in enumerate(ch["lines"]):
            key = f"{ch['id']}_{i:02d}"
            wav = cfg.AUDIO_DIR / f"{key}.wav"
            sig = hashlib.sha1(
                f"{cfg.TTS_BACKEND}|{cfg.EDGE_VOICE}|{cfg.EDGE_RATE}|{cfg.TTS_CMD}|{cfg.TTS_PY}|{ln['say']}"
                .encode()).hexdigest()
            m = manifest.get(key)
            if not (m and m.get("sig") == sig and wav.exists()):
                print(f"[tts] {key}: {ln['say'][:70]}")
                tts_adapter.synthesize(ln["say"], wav)
                manifest[key] = {"wav": str(wav), "dur": probe_duration(wav), "sig": sig}
            ch_total += manifest[key]["dur"] + cfg.LINE_GAP
        print(f"  {ch['id']} narasi {fmt_clock(ch_total)}")
        total += ch_total
    cfg.BUILD.mkdir(exist_ok=True)
    cfg.MANIFEST.write_text(json.dumps(manifest, indent=1))
    total += 12  # judul, transisi, end screen
    print(f"\nTotal perkiraan video: {fmt_clock(total)}")
    if total < cfg.MIN_SECONDS:
        print("PERINGATAN: di bawah 8 menit. Perlambat suara (EDGE_RATE=-8%), naikkan LINE_GAP, atau tambah naskah.")


# ---------------------------------------------------------------- render
def cmd_render(args):
    if not cfg.MANIFEST.exists():
        print("Catatan: belum ada manifest TTS, render akan tanpa suara (durasi perkiraan). "
              "Jalankan `python build.py tts` dulu untuk hasil final.")
    cfg.PARTS_DIR.mkdir(parents=True, exist_ok=True)
    flags = ["-ql"] if args.preview else ["-r", "1920,1080", "--fps", str(cfg.FPS)]
    for ch in pick(args.only):
        t0 = time.time()
        run([sys.executable, "-m", "manim", "render", *flags, "--media_dir", cfg.MEDIA_DIR,
             "-o", ch["id"], ch["file"], ch["scene"]], cwd=cfg.ROOT)
        found = [f for f in cfg.MEDIA_DIR.rglob(f"{ch['id']}.mp4") if "partial_movie_files" not in f.parts]
        if not found:
            sys.exit(f"Hasil render {ch['id']}.mp4 tidak ditemukan di {cfg.MEDIA_DIR}")
        newest = max(found, key=lambda f: f.stat().st_mtime)
        shutil.copy(newest, cfg.PARTS_DIR / f"{ch['id']}.mp4")
        print(f"[render] {ch['id']} selesai dalam {time.time() - t0:.0f} dtk")


# ---------------------------------------------------------------- subtitle
def srt_time(t):
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def split_text(text, max_chars=cfg.SUB_MAX_CHARS):
    pieces = []
    for part in re.split(r"(?<=[.!?,;:])\s+", text.strip()):
        pieces.extend(textwrap.wrap(part, max_chars) or [part])
    chunks, cur = [], ""
    for part in pieces:
        if cur and len(cur) + 1 + len(part) > max_chars:
            chunks.append(cur)
            cur = part
        else:
            cur = f"{cur} {part}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def chunk_cue(text, start, end):
    chunks = split_text(text)
    total = sum(len(c) for c in chunks) or 1
    out, t = [], start
    for c in chunks:
        d = (end - start) * len(c) / total
        out.append((t, t + d, textwrap.fill(c, cfg.SUB_LINE_WIDTH)))
        t += d
    return out


def has_filter(name):
    res = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return f" {name} " in res.stdout


# ---------------------------------------------------------------- assemble
def cmd_assemble(args):
    parts, entries, yt_chapters, offset = [], [], [], 0.0
    for ch in CHAPTERS:
        part = cfg.PARTS_DIR / f"{ch['id']}.mp4"
        cues_f = cfg.CUES_DIR / f"{ch['id']}.json"
        if not part.exists() or not cues_f.exists():
            sys.exit(f"Bab {ch['id']} belum dirender. Jalankan: python build.py render")
        dur = probe_duration(part)
        for c in json.loads(cues_f.read_text()):
            entries.extend(chunk_cue(c["text"], offset + c["start"], offset + min(c["end"], dur)))
        if ch["yt"]:
            yt_chapters.append((offset, ch["yt"]))
        parts.append(part)
        offset += dur

    cfg.OUT.mkdir(exist_ok=True)
    srt = cfg.OUT / f"{cfg.SLUG}.srt"
    srt.write_text("".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n"
                           for i, (a, b, txt) in enumerate(entries, 1)), encoding="utf-8")
    print(f"[srt] {len(entries)} baris -> {srt}")

    lst = cfg.BUILD / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    burn = (not args.no_burn) and has_filter("subtitles")
    if not args.no_burn and not burn:
        print("PERINGATAN: ffmpeg tanpa libass, subtitle tidak bisa dibakar. "
              "Unggah file .srt ke YouTube sebagai gantinya.")
    style = (f"FontName={cfg.SUB_FONT},FontSize={cfg.SUB_SIZE},PrimaryColour=&H00FFFFFF,"
             f"OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=14")
    final = cfg.OUT / f"{cfg.SLUG}.mp4"
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst]
    if burn:
        cmd += ["-vf", f"subtitles={srt.name}:force_style='{style}'"]
    cmd += ["-c:v", "libx264", "-preset", cfg.X264_PRESET, "-crf", cfg.X264_CRF, "-pix_fmt", "yuv420p", "-r", cfg.FPS,
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", final.name]
    run(cmd, cwd=cfg.OUT)

    chap = "\n".join(f"{fmt_clock(t)} {name}" for t, name in yt_chapters)
    (cfg.OUT / "youtube.md").write_text(f"""# {cfg.TITLE}

Durasi: {fmt_clock(offset)}

## Judul (pilih satu)
- {cfg.TITLE}? Fisika di Balik Raksasa Bawah Laut
- Kapal Selam: Cara Menyelam, Melayang, dan Naik Lagi (Dijelaskan dengan Animasi)

## Deskripsi
Bagaimana mungkin tabung baja ribuan ton bisa tenggelam, melayang, dan muncul kembali sesuka hati?
Di video ini kita bongkar fisika dan rekayasa di balik kapal selam: Hukum Archimedes, tangki ballast,
hidroplane, tekanan laut dalam, tenaga penggerak, sonar, sampai sistem penyelamatan.

Bab:
{chap}

Seri "{cfg.SERIES}": tulis di komentar, benda apa yang ingin kamu ketahui cara kerjanya berikutnya.

## Tag
kapal selam, cara kerja kapal selam, hukum archimedes, tangki ballast, sonar, animasi sains,
bagaimana dunia bekerja, explainer bahasa indonesia, teknologi militer, fisika

## Checklist sebelum unggah
- [ ] tonton seluruh video sekali (cek label tumpang tindih & sinkron suara)
- [ ] unggah thumbnail (python build.py thumb) dan file .srt sebagai subtitle cadangan
- [ ] tempel bab di deskripsi, atur end screen di 5-6 detik terakhir
""", encoding="utf-8")
    print(f"\nSelesai: {final}  ({fmt_clock(offset)})\nSubtitle: {srt}\nMetadata: {cfg.OUT / 'youtube.md'}")
    if offset < cfg.MIN_SECONDS:
        print("PERINGATAN: durasi di bawah 8 menit.")


# ---------------------------------------------------------------- thumb
def cmd_thumb(_):
    run([sys.executable, "-m", "manim", "render", "-s", "-r", "1920,1080", "--media_dir", cfg.MEDIA_DIR,
         "part4.py", "Thumb"], cwd=cfg.ROOT)
    imgs = list(cfg.MEDIA_DIR.rglob("Thumb*.png"))
    if not imgs:
        sys.exit("Thumbnail tidak ditemukan")
    cfg.OUT.mkdir(exist_ok=True)
    shutil.copy(max(imgs, key=lambda f: f.stat().st_mtime), cfg.OUT / "thumbnail.png")
    print(f"Thumbnail: {cfg.OUT / 'thumbnail.png'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("info")
    sp.add_parser("tts")
    r = sp.add_parser("render")
    r.add_argument("--only", nargs="*")
    r.add_argument("--preview", action="store_true", help="render 480p cepat untuk cek animasi")
    a = sp.add_parser("assemble")
    a.add_argument("--no-burn", action="store_true")
    al = sp.add_parser("all")
    al.add_argument("--no-burn", action="store_true")
    sp.add_parser("thumb")
    args = ap.parse_args()
    if args.cmd == "all":
        args.only, args.preview = None, False
        cmd_tts(args)
        cmd_render(args)
        cmd_assemble(args)
    else:
        {"info": cmd_info, "tts": cmd_tts, "render": cmd_render,
         "assemble": cmd_assemble, "thumb": cmd_thumb}[args.cmd](args)


if __name__ == "__main__":
    main()

"""Adapter TTS yang bisa diganti. Kontrak: synthesize(text, out_wav) menulis file audio.

Backend (TTS_BACKEND):
  edge   : edge-tts. Suara id-ID-ArdiNeural / id-ID-GadisNeural.
  cmd    : TTS milikmu lewat CLI.
           TTS_CMD='python my_tts.py --in {text_file} --out {out}'
           placeholder: {text_file} file teks UTF-8, {text} teks ter-quote, {out} file keluaran
  py     : TTS milikmu lewat fungsi Python.
           TTS_PY='my_tts:synth'  ->  synth(text: str, out_path: str) menulis audio ke out_path
  silent : audio hening berdurasi perkiraan (uji pipeline tanpa suara)
Apa pun format keluarannya, hasil akhir dikonversi ke WAV mono 44.1 kHz oleh ffmpeg.
"""
import asyncio
import importlib
import shlex
import subprocess
from pathlib import Path

import cfg


def _to_wav(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-ar", "44100", "-ac", "1", str(dst)], check=True)


def _edge(text, out):
    import edge_tts
    tmp = out.with_suffix(".tmp.mp3")

    async def go():
        await edge_tts.Communicate(text, cfg.EDGE_VOICE, rate=cfg.EDGE_RATE).save(str(tmp))

    asyncio.run(go())
    _to_wav(tmp, out)
    tmp.unlink(missing_ok=True)


def _cmd(text, out):
    if not cfg.TTS_CMD:
        raise SystemExit("TTS_BACKEND=cmd butuh TTS_CMD, contoh: "
                         "TTS_CMD='python my_tts.py --in {text_file} --out {out}'")
    raw = out.with_suffix(".raw")
    txt = out.with_suffix(".txt")
    txt.write_text(text, encoding="utf-8")
    cmd = cfg.TTS_CMD.format(text_file=shlex.quote(str(txt)), out=shlex.quote(str(raw)),
                             text=shlex.quote(text))
    subprocess.run(cmd, shell=True, check=True)
    if not raw.exists():
        raise SystemExit(f"TTS_CMD tidak menghasilkan file: {raw}")
    _to_wav(raw, out)
    raw.unlink(missing_ok=True)
    txt.unlink(missing_ok=True)


def _py(text, out):
    if ":" not in cfg.TTS_PY:
        raise SystemExit("TTS_BACKEND=py butuh TTS_PY='modul:fungsi'")
    mod, fn = cfg.TTS_PY.split(":", 1)
    raw = out.with_suffix(".raw")
    getattr(importlib.import_module(mod), fn)(text, str(raw))
    _to_wav(raw, out)
    raw.unlink(missing_ok=True)


def _silent(text, out):
    dur = max(2.0, len(text.split()) / 2.7)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=mono", "-t", f"{dur:.2f}", str(out)], check=True)


def synthesize(text, out_wav):
    out_wav = Path(out_wav)
    backends = {"edge": _edge, "cmd": _cmd, "py": _py, "silent": _silent}
    if cfg.TTS_BACKEND not in backends:
        raise SystemExit(f"TTS_BACKEND tidak dikenal: {cfg.TTS_BACKEND} (pilih: {', '.join(backends)})")
    backends[cfg.TTS_BACKEND](text, out_wav)

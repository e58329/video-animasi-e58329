"""Konfigurasi global proyek (semua bisa di-override lewat environment variable)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
AUDIO_DIR = BUILD / "audio"
CUES_DIR = BUILD / "cues"
PARTS_DIR = BUILD / "parts"
MEDIA_DIR = BUILD / "media"
MANIFEST = BUILD / "manifest.json"
OUT = ROOT / "out"

TITLE = "Bagaimana Kapal Selam Bekerja"
SERIES = "Bagaimana Dunia Bekerja"
SLUG = "bagaimana_kapal_selam_bekerja"

FPS = 30
MIN_SECONDS = 8 * 60                         # target minimal durasi video
LINE_GAP = float(os.getenv("LINE_GAP", "0.55"))   # jeda antar kalimat (detik)
FONT = os.getenv("VIDEO_FONT", "")           # contoh: VIDEO_FONT="Montserrat"

# --- TTS ---------------------------------------------------------------
# edge   : edge-tts (pip install edge-tts), butuh internet
# cmd    : perintah CLI milikmu sendiri, lewat TTS_CMD
# py     : fungsi Python milikmu sendiri, lewat TTS_PY="modul:fungsi"
# silent : audio hening (untuk uji pipeline tanpa suara)
TTS_BACKEND = os.getenv("TTS_BACKEND", "edge")
EDGE_VOICE = os.getenv("EDGE_VOICE", "id-ID-ArdiNeural")   # alternatif: id-ID-GadisNeural
EDGE_RATE = os.getenv("EDGE_RATE", "+0%")
TTS_CMD = os.getenv("TTS_CMD", "")
TTS_PY = os.getenv("TTS_PY", "")

# --- Subtitle (dibakar ke video lewat ffmpeg/libass) -----------------------
SUB_FONT = os.getenv("SUB_FONT", "DejaVu Sans")
SUB_SIZE = int(os.getenv("SUB_SIZE", "13"))
SUB_MAX_CHARS = 88
SUB_LINE_WIDTH = 46

# --- Encode akhir ------------------------------------------------------------
X264_PRESET = os.getenv("X264_PRESET", "medium")   # ultrafast/fast untuk pratinjau, slow untuk final
X264_CRF = os.getenv("X264_CRF", "18")

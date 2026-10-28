# pipeline/make_subs.py — subtitle BUKAN tebakan whisper, tapi langsung dari naskah
# Timing kata diambil dari edge-tts WordBoundary = nol typo, sinkron sempurna
# Pakai: python pipeline/make_subs.py <file.yaml> <video_in> <video_out>
import sys, os, re, asyncio, subprocess
import edge_tts
import yaml

VOICE = "id-ID-ArdiNeural"
PITCH = 0.85
STYLE = ("FontName=Montserrat,FontSize=18,Bold=1,PrimaryColour=&H0007C1FF&,"
         "OutlineColour=&H00000000&,BorderStyle=1,Outline=2,Shadow=1,"
         "Alignment=2,MarginV=42")
TICK = 10000.0  # offset edge-tts dalam satuan 100ns -> ms


def full_text(p):
    d = yaml.safe_load(open(p, encoding="utf-8"))
    t = str(d.get("question", "")) + " "
    for sec in d.get("sections", []):
        t += str(sec.get("heading", "")) + ". "
        for pt in sec.get("points", []):
            t += (pt.get("text", "") if isinstance(pt, dict) else str(pt)) + " "
    t += str(d.get("conclusion", ""))
    return t


async def tts_words(text):
    audio, words = [], []
    try:
        comm = edge_tts.Communicate(text, VOICE, boundary="WordBoundary")
    except TypeError:
        comm = edge_tts.Communicate(text, VOICE)  # versi lama: default WordBoundary
    async for ch in comm.stream():
        typ = ch.get("type") if isinstance(ch, dict) else getattr(ch, "type", "")
        if typ == "audio":
            audio.append(ch["data"] if isinstance(ch, dict) else ch.data)
        elif typ == "WordBoundary":
            g = (lambda k: ch[k] if isinstance(ch, dict) else getattr(ch, k))
            words.append({"o": g("offset"), "d": g("duration"), "t": g("text")})
    return b"".join(audio), words


def dur_of(f):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", f]).strip())


def fmt(ms):
    ms = max(int(ms), 0)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def attach_punct(text, words):
    """Balikin tanda baca dari naskah asli ke kata-kata edge-tts"""
    toks = text.split()
    i, out = 0, []
    for w in words:
        wt = norm(str(w["t"]))
        if not wt:
            out.append(str(w["t"]))
            continue
        hit, j = None, i
        while j < len(toks) and j - i < 6:
            if norm(toks[j]) == wt:
                hit, i = toks[j], j + 1
                break
            j += 1
        out.append(hit if hit is not None else str(w["t"]))
    return out


def build_srt(words, adur_ms, path, text):
    texts = attach_punct(text, words)
    cues, cur, st, pe = [], [], None, None
    for w, txt in zip(words, texts):
        o = w["o"] / TICK * 1.0  # pitch-shift (asetrate+atempo) tak ubah durasi
        d = w["d"] / TICK * 1.0
        if st is None:
            st = o
        cur.append(txt)
        pe = o + d
        line = " ".join(cur)
        term = txt[-1:] in ".,?!"
        if ((term and len(cur) >= 3) or len(cur) >= 7
                or len(line) >= 42 or (pe - st) >= 3200):
            cues.append([st, pe, line])
            cur, st = [], None
    if cur:
        cues.append([st, pe, " ".join(cur)])
    if not cues:
        raise SystemExit("TIDAK ADA word boundary dari edge-tts!")
    last = cues[-1][1]
    r = adur_ms / last if last > 0 else 1.0
    if abs(r - 1.0) > 0.10:  # cuma kalibrasi kalau skala tick-nya salah bener
        print("kalibrasi timing x%.4f" % r)
        for c in cues:
            c[0] *= r
            c[1] *= r
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(cues, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (i, fmt(a), fmt(b + 300), t))
    return len(cues)


def main():
    yml, vin, vout = sys.argv[1], sys.argv[2], sys.argv[3]
    text = full_text(yml)
    print("subs: ambil timing kata dari edge-tts...")
    raw, words = asyncio.run(tts_words(text))
    open("raw_subs.mp3", "wb").write(raw)
    subprocess.run(
        'ffmpeg -y -i raw_subs.mp3 -af "asetrate=24000*%s,aresample=24000,'
        'atempo=%s" -c:a libmp3lame audio_subs.mp3' % (PITCH, 1 / PITCH),
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    adur = dur_of("audio_subs.mp3")
    n = build_srt(words, adur * 1000.0, "subs_script.srt", text)
    print("subs: %d cue, audio %.1fs" % (n, adur))
    subprocess.run(
        ["ffmpeg", "-y", "-i", vin, "-i", "audio_subs.mp3",
         "-map", "0:v:0", "-map", "1:a:0",
         "-vf", "subtitles=subs_script.srt:force_style='" + STYLE + "'",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-shortest", "-movflags", "+faststart", vout])
    for f in ("raw_subs.mp3", "audio_subs.mp3", "subs_script.srt"):
        if os.path.exists(f):
            os.remove(f)
    print("SELESAI: %s (%.1fs)" % (vout, dur_of(vout)))


if __name__ == "__main__":
    main()

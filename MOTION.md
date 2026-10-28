# MOTION.md — Motion Graphics Lokal (pymotion)

Visual `motion:*` dirender **oleh repo sendiri** memakai pymotion — tanpa
internet, tanpa unduhan, **nol kewajiban atribusi**. Ini lapisan kedua di
urutan prioritas visual explainer:

1. **gambar manual** di registry `VISUALS` (explainer.py, 39 fungsi)
2. **`motion:<template>`** — motion graphics lokal (file ini)
3. **auto-fetch CC0** — vektor internet bebas-atribusi (pipeline/assets.py)
4. **kartu generic** — fallback kalau semua gagal (render tak pernah gagal)

## Cara pakai di YAML

```yaml
sections:
  - heading: "1. Hook"
    points:
      - text: "Kata besar muncul satu per satu."
        visual: "motion:kinetic_hook"
      - text: "Kedalaman maksimum kapal selam militer rata-rata."
        visual: "motion:stat_counter"

motion_overrides:            # opsional, spec per template
  stat_counter:
    label: "Kedalaman Maksimum"
    value_to: 3800
    fmt: "{:,.0f}"
    suffix: " m"
```

## Template tersedia

| template       | tampilan                                      | spec utama |
|----------------|-----------------------------------------------|------------|
| `kinetic_hook` | kata besar slide-in per baris (spring native) | `lines`, `colors`, `size` |
| `stat_counter` | angka count-up + progress bar (native)        | `value_to`, `fmt`, `suffix`, `label`, `caption`, `bar_w` |
| `route_map`    | peta: reveal rute titik demi titik + pulse tujuan | `points` (fraksi 0..1), `origin`, `dest`, `title`, `sub`, `dots` |
| `bar_compare`  | perbandingan batang blocky-fill               | `bars: [{label, value, color}]`, `unit`, `title`, `hi` |

Warna brand bisa dioverride per spec: `primary`, `accent`, `ink`, `mist`,
`deep`, `navy`, `green`. Font default = Montserrat bawaan repo
(`assets/fonts/Montserrat-Bold.ttf`, dipakai via path langsung).

## Detail teknis (penting)

- **Durasi clip otomatis** = play + gap tunggu poin (dikurangi 0.7s cadangan
  fade), jadi motion berhenti pas poin selesai.
- **Cache**: `motion/cache/<template>-<hash10>/f%04d.png`. Hash = sha1
  (template + spec + frames + fps). Ganti spec/override → render ulang
  otomatis, sama seperti cache aset.
- **Engine pymotion 3.7.0** (dipakai pas dengan kemampuannya):
  - semua durasi dalam **FRAME**, bukan detik;
  - ShapeClip/TextClip statis (render sekali, cache) → animasi = reveal
    opacity berjenjang di level composite;
  - yang dinamis native: `NumberCounter`, `ProgressBar`, `KineticText`.
- **Embed**: frame PNG transparan di-swap tiap frame lewat updater
  `ImageMobject` di dalam kartu brand (gaya identik kartu aset).
- Fallback aman: template gagal → `[motion] ... -> fallback generic`.

## CLI (tanpa render video)

```bash
python -m pipeline.motion.clips list
python -m pipeline.motion.clips render stat_counter --spec '{"value_to": 3800, "suffix": " m"}' --dur 5
```

## Kapan pakai yang mana

- butuh angka/perbandingan/peta/hook → `motion:*` (cepat, konsisten, gratis)
- butuh ikon/objek spesifik → auto-fetch CC0 (`visual: nama_bebas`)
- butuh karakter aksi stickman brand → gambar manual di registry

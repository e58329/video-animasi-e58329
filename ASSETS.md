# 🎨 Aset Vektor Otomatis (pipeline/assets.py)

Fitur ini bikin repo **mencari sendiri** vektor di internet kalau sebuah
`visual:` di content YAML tidak punya fungsi gambar manual di registry
`VISUALS` (scenes/templates/explainer.py). Alur lengkap:

```
YAML visual: "roket_meluncur"   (tidak ada di VISUALS)
        │
        ▼
scenes/templates/asset_visual.py  ── vis_asset()
        │
        ▼
pipeline/assets.py resolve()      ── cari → cek lisensi → download → validasi
        │                             (cache: assets/svg_auto/)
        ▼
SVGMobject import → animasi gaya channel (kartu + label)
        │
   gagal di tahap mana pun? → jatuh balik ke kartu generic (render TIDAK pernah gagal)
```

## Sumber (provider)

| Provider     | Isi                                  | Lisensi                       | Catatan |
|--------------|--------------------------------------|-------------------------------|---------|
| `iconify`    | ±200rb ikon open-source (default)    | Metadata SPDX per koleksi     | Paling stabil, tanpa API key |
| `wikimedia`  | SVG ilustrasi Wikimedia Commons      | CC0/CC-BY/CC-BY-SA (difilter) | Kadang kena rate-limit 429 di IP cloud |
| `github`     | file SVG repo mana pun (raw)         | Dibaca dari LICENSE repo      | Format spec: `owner/repo/path/file.svg` |

## Pemakaian

### 0. Nggak ngapa-ngapain (default)
Tulis saja visual baru di YAML. Saat render, pipeline otomatis mencari
ikon dari query nama visual (`periscope` → cari "periscope").

### 1. Matikan fitur (pakai kartu generic seperti dulu)
```yaml
assets: off          # default "auto"
```

### 2. Override per visual (opsional)
```yaml
asset_overrides:
  rocket_launch: {collection: "fluent-emoji"}          # paksa koleksi iconify
  periscope:     {provider: wikimedia}                 # ilustrasi dari Commons
  deep_sea:      {color: "#42A5F5"}                    # mono, warna kustom
  kapal:         {query: "submarine side view"}        # query kustom
  logo:          {github: "owner/repo/assets/logo.svg"}
```

### 3. CLI manual
```bash
python -m pipeline.assets search "rocket launch"        # lihat kandidat + lisensi
python -m pipeline.assets fetch rocket_launch           # download + validasi + cache
python -m pipeline.assets prefetch content/episode.yaml # scan semua visual di YAML
python -m pipeline.assets list                          # aset ter-cache
python -m pipeline.assets credits                       # buat ASSETS-ATTRIBUTION.md
```

## Lisensi & atribusi (PENTING)

- Hanya lisensi di allowlist yang diterima: CC0, Public domain,
  CC-BY, CC-BY-SA, MIT, Apache-2.0, BSD, ISC. Lisensi lain **ditolak**.
- Mayoritas lisensi ini **wajib atribusi**. Sebelum publish video:
  ```bash
  python -m pipeline.assets credits
  ```
  lalu tempel isi `ASSETS-ATTRIBUTION.md` ke deskripsi video.

## Aturan aman-manim (validator otomatis)

SVG ditolak (lanjut kandidat berikutnya) kalau:
- ada elemen `<text>` / `<image>` / `<script>` (manim tidak bisa render),
- lebih dari 400 node (terlalu kompleks → lambat & sering rusak),
- lebih dari 300KB,
- **semua** path-nya hanya andalkan gradient `<defs>` (manim tidak
  render gradient SVG) → otomatis cari ikon flat pengganti.

Cache: `assets/svg_auto/` (SVG + `index.json` + `credits.json`).
Cache otomatis di-refresh kalau override berubah (hash spesifikasi),
jadi ganti koleksi/warna di YAML langsung berefek tanpa hapus manual.

## Arsitektur singkat

- `pipeline/assets.py` — fetcher + validator + cache + CLI (tanpa
  dependensi baru selain `requests`).
- `scenes/templates/asset_visual.py` — `vis_asset()`: import SVGMobject,
  recolor, normalisasi ke zona visual, animasi masuk.
- `scenes/templates/explainer.py` — 3 jahitan kecil: import, baca
  `assets`/`asset_overrides` dari YAML, dan cabang `elif asset_on:`
  di dispatch visual.

# 🎨 Aset Vektor Otomatis (pipeline/assets.py)

> **POLICY LISENSI: ZERO-ATTRIBUTION (default).** Hanya CC0 / Public
> domain / Unlicense yang dipakai — video lo **bebas kewajiban kredit**,
> gak akan kelupaan atribusi. Lisensi butuh-kredit (CC-BY, MIT, dsb.)
> otomatis DITOLAK kecuali lo opt-in eksplisit (lihat bawah).

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
  rocket_launch: {collection: "system-uicons"}         # paksa koleksi iconify
  periscope:     {provider: wikimedia}                 # ilustrasi dari Commons
  deep_sea:      {color: "#42A5F5"}                    # mono, warna kustom
  kapal:         {query: "submarine side view"}        # query kustom
  logo:          {github: "owner/repo/assets/logo.svg"}
```

### 3. Opt-in lisensi butuh-atribusi (HANYA kalau lo sadar mau ngasih kredit)
```yaml
assets_attribution: true   # default: absen = REJECT CC-BY/MIT/dll
```
Atau via CLI: `python -m pipeline.assets fetch <nama> --allow-attribution`.
Kalau aktif, WAJIB jalankan `python -m pipeline.assets credits` dan
tempel hasilnya ke deskripsi video.

### 4. CLI manual
```bash
python -m pipeline.assets search "rocket launch"        # lihat kandidat + lisensi
python -m pipeline.assets fetch rocket_launch           # download + validasi + cache
python -m pipeline.assets prefetch content/episode.yaml # scan semua visual di YAML
python -m pipeline.assets list                          # aset ter-cache
python -m pipeline.assets credits                       # buat ASSETS-ATTRIBUTION.md
```

## Lisensi & atribusi (POLICY ZERO-ATTRIBUTION)

- **Default: hanya CC0 / Public domain / Unlicense yang lolos.**
  CC-BY, CC-BY-SA, MIT, Apache, BSD, ISC = otomatis ditolak → cari
  kandidat lain → kalau gak ada, jatuh ke kartu generic. Video 100%
  bebas kewajiban kredit.
- Koleksi iconify CC0 yang dikejar otomatis: `system-uicons` (Unlicense),
  `maki`, `temaki`, `osmic`, `pinhead`, `simple-icons`, `logos`, `cib`,
  `cif`, `cryptocurrency`. Wikimedia difilter CC0/PD juga.
- Konsekuensi jujur: cakupan lebih sempit dari ikon MIT/Apache
  (±4.6rb ikon umum CC0 vs 200rb). Topik umum (roket, jangkar, bendera,
  rumah sakit, logo brand) aman; topik niche bisa jatuh generic —
  solusinya: gambar manual, ubah query, atau opt-in atribusi.
- Kalau suatu saat opt-in (`assets_attribution: true`), sebelum publish:
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
Cache otomatis di-refresh kalau override/policy berubah (hash spesifikasi),
jadi ganti koleksi/warna di YAML langsung berefek tanpa hapus manual.

## Arsitektur singkat

- `pipeline/assets.py` — fetcher + validator + cache + CLI (tanpa
  dependensi baru selain `requests`). Policy lisensi di sini:
  `LICENSE_ZERO` (selalu boleh) vs `LICENSE_ATTR` (butuh opt-in).
- `scenes/templates/asset_visual.py` — `vis_asset()`: import SVGMobject,
  recolor, normalisasi ke zona visual, animasi masuk.
- `scenes/templates/explainer.py` — 3 jahitan kecil: import, baca
  `assets`/`asset_overrides` dari YAML, dan cabang `elif asset_on:`
  di dispatch visual.

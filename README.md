# KampusPlan

KampusPlan adalah aplikasi CLI sederhana untuk mencatat tugas kuliah, memantau tenggat, menandai pekerjaan yang selesai, dan mengekspor daftar tugas ke CSV. Data disimpan secara lokal dalam berkas JSON; aplikasi tidak memerlukan akun atau layanan daring.

## Fitur

- Menambah tugas dengan mata kuliah, tenggat, dan prioritas.
- Melihat daftar tugas, memfilter status, dan mengurutkan berdasarkan tenggat atau prioritas.
- Menampilkan ringkasan tugas terbuka, tenggat hari ini, tugas terlambat, dan tugas selesai.
- Menandai tugas selesai atau menghapus tugas.
- Mengekspor seluruh daftar tugas ke CSV.
- Menyimpan data dengan penulisan berkas atomik dan memberi pesan yang jelas bila data JSON rusak.

## Persyaratan

- Python 3.10 atau lebih baru.
- Tidak ada dependensi runtime pihak ketiga.

## Instalasi

Ekstrak folder proyek, lalu jalankan dari folder `kampusplan`.

```bash
python -m venv .venv
```

Aktifkan virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS atau Linux
source .venv/bin/activate
```

Pasang aplikasi dalam mode pengembangan:

```bash
python -m pip install -e .
```

## Cara menjalankan

Semua perintah menerima opsi `--data` sebelum subperintah untuk memilih lokasi data. Jika tidak disertakan, data disimpan di `~/.kampusplan/tasks.json`.

```bash
kampusplan --data tugas.json add "Pemrograman Web" "Demo REST API" --due 2026-11-02 --priority tinggi
kampusplan --data tugas.json list
kampusplan --data tugas.json summary
kampusplan --data tugas.json done ABC123
kampusplan --data tugas.json export-csv laporan/tugas.csv
```

Jika belum memasang aplikasi, perintah yang sama bisa dijalankan melalui modul:

```bash
python -m kampusplan --data tugas.json list --status terbuka --sort tenggat
```

Gunakan `python -m kampusplan --help` atau `python -m kampusplan list --help` untuk melihat bantuan.

### Contoh keluaran

```text
Tugas ditambahkan dengan ID 7A31C2: Pemrograman Web — Demo REST API

ID       TENGGAT      PRIORITAS  STATUS    MATA KULIAH — TUGAS
----------------------------------------------------------------------------------
7A31C2   2026-11-02   tinggi     terbuka   Pemrograman Web — Demo REST API

Ringkasan KampusPlan
Terbuka      : 1
Tenggat hari ini: 0
Terlambat    : 0
Selesai      : 0
```

ID pada contoh dibuat otomatis dan akan berbeda pada setiap tugas.

## Pengujian

Jalankan dari folder proyek:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Lisensi

MIT. Lihat berkas `LICENSE`.


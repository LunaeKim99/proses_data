# Proses Data Pendidikan

Proyek modular Python untuk memproses dataset pendidikan CSV dan menghasilkan analisis serta visualisasi data.

## Struktur Proyek

```
proses_data/
├── main.py                    # Entry point
├── dataset.csv                # Dataset input (tidak di-track)
├── requirements.txt           # Dependencies
├── modules/
│   ├── __init__.py           # Package init
│   ├── data_loader.py        # Memuat dan membersihkan data
│   ├── feature_engineer.py   # Feature engineering
│   ├── exporter.py           # Export file CSV
│   └── visualizer.py         # Generate chart PNG
└── output/                    # Hasil output (tidak di-track)
```

## Instalasi

```bash
pip install -r requirements.txt
```

## Penggunaan

1. Letakkan `dataset.csv` di direktori root proyek
2. Jalankan:
```bash
python main.py
```

## Output

### File CSV (`output/`)
- `feature_engineered.csv` - Data lengkap dengan fitur tambahan
- `ranking_provinsi.csv` - Ranking provinsi berdasarkan berbagai metrik

### Chart PNG (`output/`)
- `chart1_putus_sekolah.png` - Top 15 provinsi rasio putus sekolah
- `chart2_scatter_korelasi.png` - Scatter plot korelasi siswa-guru vs kelas rusak
- `chart3_kondisi_kelas.png` - Donut chart kondisi ruang kelas nasional

## Dataset

Dataset harus memiliki kolom:
`Provinsi, Sekolah, Siswa, Mengulang, Putus Sekolah, Kepala Sekolah dan Guru(<S1), Kepala Sekolah dan Guru(>S1), Tenaga Kependidikan(SM), Tenaga Kependidikan(>SM), Rombongan Belajar, Ruang kelas(baik), Ruang kelas(rusak ringan), Ruang kelas(rusak sedang), Ruang kelas(rusak berat)`

## Fitur Tambahan

- Rasio Putus Sekolah & Mengulang
- Persentase Kelas Rusak
- Rasio Siswa-Guru
- Persentase Guru S1 ke atas
- Ranking provinsi

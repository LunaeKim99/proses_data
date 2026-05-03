import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    df['Total_Rusak'] = df['Ruang kelas(rusak ringan)'] + df['Ruang kelas(rusak sedang)'] + df['Ruang kelas(rusak berat)']
    df['Total_Kelas'] = df['Ruang kelas(baik)'] + df['Total_Rusak']
    df['Total_Guru'] = df['Kepala Sekolah dan Guru(<S1)'] + df['Kepala Sekolah dan Guru(>S1)']
    
    df['Rasio_Putus_Sekolah'] = (df['Putus Sekolah'] / df['Siswa']) * 100
    df['Rasio_Mengulang'] = (df['Mengulang'] / df['Siswa']) * 100
    df['Persen_Kelas_Rusak'] = (df['Total_Rusak'] / df['Total_Kelas']) * 100
    df['Rasio_Siswa_Guru'] = df['Siswa'] / df['Total_Guru']
    df['Persen_Guru_S1_Plus'] = (df['Kepala Sekolah dan Guru(>S1)'] / df['Total_Guru']) * 100
    
    df = df.replace([np.inf, -np.inf], 0).fillna(0)
    
    df['Rasio_Putus_Sekolah'] = df['Rasio_Putus_Sekolah'].round(3)
    df['Rasio_Mengulang'] = df['Rasio_Mengulang'].round(3)
    df['Persen_Kelas_Rusak'] = df['Persen_Kelas_Rusak'].round(2)
    df['Rasio_Siswa_Guru'] = df['Rasio_Siswa_Guru'].round(2)
    df['Persen_Guru_S1_Plus'] = df['Persen_Guru_S1_Plus'].round(2)
    
    abbrev = {
        'D.K.I. Jakarta': 'DKI Jakarta', 'Jawa Barat': 'Jabar', 'Jawa Tengah': 'Jateng',
        'D.I. Yogyakarta': 'DIY', 'Jawa Timur': 'Jatim', 'Aceh': 'Aceh',
        'Sumatera Utara': 'Sumut', 'Sumatera Barat': 'Sumbar', 'Riau': 'Riau',
        'Jambi': 'Jambi', 'Sumatera Selatan': 'Sumsel', 'Lampung': 'Lampung',
        'Kalimantan Barat': 'Kalbar', 'Kalimantan Tengah': 'Kalteng',
        'Kalimantan Selatan': 'Kalsel', 'Kalimantan Timur': 'Kaltim',
        'Sulawesi Utara': 'Sulut', 'Sulawesi Tengah': 'Sulteng',
        'Sulawesi Selatan': 'Sulsel', 'Sulawesi Tenggara': 'Sultra',
        'Maluku': 'Maluku', 'Bali': 'Bali', 'Nusa Tenggara Barat': 'NTB',
        'Nusa Tenggara Timur': 'NTT', 'Papua': 'Papua', 'Bengkulu': 'Bengkulu',
        'Maluku Utara': 'Malut', 'Banten': 'Banten',
        'Kepulauan Bangka Belitung': 'Babel', 'Gorontalo': 'Gorontalo',
        'Kepulauan Riau': 'Kepri', 'Papua Barat': 'Papua Barat',
        'Sulawesi Barat': 'Sulbar', 'Kalimantan Utara': 'Kaltara',
        'Papua Tengah': 'Papua Tgh', 'Papua Selatan': 'Papua Sel',
        'Papua Pegunungan': 'Papua Peg', 'Papua Barat Daya': 'Papua BD'
    }
    
    df['ProvShort'] = df['Provinsi'].str.replace('Prov. ', '', regex=False).map(abbrev).fillna(df['Provinsi'])
    
    return df

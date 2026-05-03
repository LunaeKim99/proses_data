import pandas as pd

def export_csvs(df: pd.DataFrame, output_dir: str) -> None:
    feature_path = f"{output_dir}/feature_engineered.csv"
    df.to_csv(feature_path, index=False)
    print(f"✅ Saved: {feature_path}")
    
    ranking_cols = ['Provinsi', 'Siswa', 'Sekolah', 'Rasio_Putus_Sekolah', 'Rasio_Mengulang', 'Persen_Kelas_Rusak', 'Rasio_Siswa_Guru', 'Persen_Guru_S1_Plus']
    ranking_df = df[ranking_cols].copy()
    
    ranking_df['Rank_Siswa'] = ranking_df['Siswa'].rank(method='dense', ascending=False).astype(int)
    ranking_df['Rank_Putus_Sekolah'] = ranking_df['Rasio_Putus_Sekolah'].rank(method='dense', ascending=False).astype(int)
    ranking_df['Rank_Kelas_Rusak'] = ranking_df['Persen_Kelas_Rusak'].rank(method='dense', ascending=False).astype(int)
    
    ranking_df = ranking_df.sort_values('Rank_Siswa', ascending=True)
    
    ranking_path = f"{output_dir}/ranking_provinsi.csv"
    ranking_df.to_csv(ranking_path, index=False)
    print(f"✅ Saved: {ranking_path}")

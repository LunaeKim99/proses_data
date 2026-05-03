import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import os

pio.templates.default = "plotly_white"

try:
    import kaleido
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kaleido", "-q"])

def generate_charts(df: pd.DataFrame, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    
    chart1_df = df.nlargest(15, 'Rasio_Putus_Sekolah').sort_values('Rasio_Putus_Sekolah', ascending=True)
    fig1 = px.bar(chart1_df, x='Rasio_Putus_Sekolah', y='ProvShort', orientation='h',
                 title="Top 15 Provinsi: Rasio Putus Sekolah (%)")
    fig1.update_layout(xaxis_title="Rasio (%)", yaxis_title="Provinsi",
                      height=550, margin=dict(l=120, r=100, t=80, b=50))
    fig1.update_traces(texttemplate='%{x:.2f}%', textposition='outside')
    fig1.write_image(f"{output_dir}/chart1_putus_sekolah.png")
    print(f"✅ Saved: {output_dir}/chart1_putus_sekolah.png")
    
    threshold_x = np.percentile(df['Rasio_Siswa_Guru'], 80)
    threshold_y = np.percentile(df['Persen_Kelas_Rusak'], 80)
    df['text_label'] = df.apply(lambda r: r['ProvShort'] if r['Rasio_Siswa_Guru'] > threshold_x or r['Persen_Kelas_Rusak'] > threshold_y else "", axis=1)
    
    fig2 = px.scatter(df, x='Rasio_Siswa_Guru', y='Persen_Kelas_Rusak', size='Siswa',
                     color='Persen_Guru_S1_Plus', color_continuous_scale='RdYlGn',
                     text='text_label', title="Korelasi Rasio Siswa-Guru vs Kelas Rusak (%)")
    fig2.update_layout(xaxis_title="Siswa/Guru", yaxis_title="% Kelas Rusak",
                      height=550, margin=dict(l=60, r=80, t=80, b=60))
    fig2.update_traces(textposition='top center', textfont_size=11)
    fig2.write_image(f"{output_dir}/chart2_scatter_korelasi.png")
    print(f"✅ Saved: {output_dir}/chart2_scatter_korelasi.png")
    
    kondisi = {
        'Baik': df['Ruang kelas(baik)'].sum(),
        'Rusak Ringan': df['Ruang kelas(rusak ringan)'].sum(),
        'Rusak Sedang': df['Ruang kelas(rusak sedang)'].sum(),
        'Rusak Berat': df['Ruang kelas(rusak berat)'].sum()
    }
    
    fig3 = go.Figure(data=[go.Pie(labels=list(kondisi.keys()), values=list(kondisi.values()),
                                  hole=0.3, textinfo='label+percent', textfont=dict(size=14))])
    fig3.update_layout(title=dict(text="Kondisi Ruang Kelas Nasional", font=dict(size=20)),
                      height=500, margin=dict(t=80, b=80, l=40, r=40),
                      uniformtext_minsize=12, uniformtext_mode='hide',
                      legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5))
    fig3.write_image(f"{output_dir}/chart3_kondisi_kelas.png")
    print(f"✅ Saved: {output_dir}/chart3_kondisi_kelas.png")

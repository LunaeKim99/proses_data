import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import os
import sys
import subprocess
from datetime import datetime

from modules.data_loader import load_data
from modules.feature_engineer import engineer_features
from modules.visualizer import generate_charts
from modules.gui.components import log_message, create_flat_button, add_hover_effect
import pandas as pd

hover_colors = {
    "#27AE60": "#1E8449",
    "#2980B9": "#1F618D",
    "#E74C3C": "#C0392B",
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.dataset_path = tk.StringVar(value="dataset.csv" if os.path.exists("dataset.csv") else "")
        self.output_path = tk.StringVar(value="output")
        self.opt_csv_feature = tk.BooleanVar(value=True)
        self.opt_csv_ranking = tk.BooleanVar(value=True)
        self.opt_charts = tk.BooleanVar(value=True)
        self.is_running = False
        self._setup_window()
        self._build_header()
        self._build_main_area()
        self._build_status_bar()
        self._log_welcome()

    def _setup_window(self):
        self.title("📊 Analisis Data Pendidikan Indonesia")
        self.geometry("900x650")
        self.minsize(700, 500)
        self.configure(bg="#F5F5F5")
        self.default_font = ("Segoe UI", 10)
        self.header_font = ("Segoe UI", 12, "bold")

    def _build_header(self):
        header = tk.Frame(self, bg="#2C3E50", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        title = tk.Label(header, text="Analisis Data Pendidikan Indonesia",
                        font=("Segoe UI", 16, "bold"), bg="#2C3E50", fg="white")
        title.pack(pady=(15, 2))
        subtitle = tk.Label(header, text="Data Sekolah, Siswa, Guru, dan Infrastruktur per Provinsi",
                           font=("Segoe UI", 10), bg="#2C3E50", fg="#BDC3C7")
        subtitle.pack()

    def _build_main_area(self):
        main = tk.Frame(self, bg="#F5F5F5")
        main.pack(fill="both", expand=True, padx=10, pady=10)
        main.columnconfigure(0, minsize=280, maxsize=280)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)
        self._build_left_panel(tk.Frame(main, bg="#FFFFFF", relief="solid", bd=1))
        self._build_right_panel(tk.Frame(main, bg="#FFFFFF", relief="solid", bd=1))

    def _build_left_panel(self, panel):
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel.configure(bg="#FFFFFF")
        tk.Label(panel, text="📂 File Dataset", font=("Segoe UI", 10, "bold"),
                bg="#FFFFFF", fg="#2C3E50").pack(anchor="w", padx=15, pady=(15, 5))
        entry_file = ttk.Entry(panel, textvariable=self.dataset_path, state="readonly")
        entry_file.pack(fill="x", padx=15, pady=(0, 5))
        btn_file = ttk.Button(panel, text="Browse...", command=self._browse_file)
        btn_file.pack(fill="x", padx=15, pady=(0, 15))
        tk.Label(panel, text="📁 Folder Output", font=("Segoe UI", 10, "bold"),
                bg="#FFFFFF", fg="#2C3E50").pack(anchor="w", padx=15, pady=(0, 5))
        entry_out = ttk.Entry(panel, textvariable=self.output_path, state="readonly")
        entry_out.pack(fill="x", padx=15, pady=(0, 5))
        btn_out = ttk.Button(panel, text="Browse...", command=self._browse_output)
        btn_out.pack(fill="x", padx=15, pady=(0, 15))
        tk.Label(panel, text="⚙️ Pilihan Output", font=("Segoe UI", 10, "bold"),
                bg="#FFFFFF", fg="#2C3E50").pack(anchor="w", padx=15, pady=(0, 5))
        ttk.Checkbutton(panel, text="Buat CSV Feature Engineering", variable=self.opt_csv_feature).pack(anchor="w", padx=15)
        ttk.Checkbutton(panel, text="Buat CSV Ranking Provinsi", variable=self.opt_csv_ranking).pack(anchor="w", padx=15)
        ttk.Checkbutton(panel, text="Buat 3 Chart (PNG)", variable=self.opt_charts).pack(anchor="w", padx=15, pady=(0, 15))
        self.btn_run = create_flat_button(panel, "▶  Jalankan Proses", "#27AE60", self._start_process_thread)
        self.btn_run.pack(fill="x", padx=15, pady=(10, 5))
        add_hover_effect(self.btn_run, "#27AE60", hover_colors["#27AE60"])
        self.btn_open = create_flat_button(panel, "🗂  Buka Folder Output", "#2980B9", self._open_output_folder)
        self.btn_open.pack(fill="x", padx=15, pady=5)
        add_hover_effect(self.btn_open, "#2980B9", hover_colors["#2980B9"])
        self.btn_clear = create_flat_button(panel, "🧹  Bersihkan Log", "#E74C3C", self._clear_log)
        self.btn_clear.pack(fill="x", padx=15, pady=(5, 15))
        add_hover_effect(self.btn_clear, "#E74C3C", hover_colors["#E74C3C"])

    def _build_right_panel(self, panel):
        panel.grid(row=0, column=1, sticky="nsew")
        panel.configure(bg="#FFFFFF")
        tk.Label(panel, text="📋 Log Proses", font=("Segoe UI", 11, "bold"),
                bg="#FFFFFF", fg="#2C3E50").pack(anchor="w", padx=15, pady=10)
        self.log_widget = scrolledtext.ScrolledText(panel, font=("Consolas", 10),
                                                    bg="#1E1E1E", fg="#D4D4D4",
                                                    state="disabled", wrap="word")
        self.log_widget.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_widget.tag_configure("info", foreground="#4FC3F7")
        self.log_widget.tag_configure("success", foreground="#81C784")
        self.log_widget.tag_configure("warning", foreground="#FFD54F")
        self.log_widget.tag_configure("error", foreground="#E57373")
        self.log_widget.tag_configure("header", foreground="#CE93D8", font=("Consolas", 10, "bold"))

    def _build_status_bar(self):
        self.status_bar = tk.Frame(self, bg="#2C3E50", height=30)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_label = tk.Label(self.status_bar, text="Siap. Pilih file dataset dan klik Jalankan Proses.",
                                    font=("Segoe UI", 9), bg="#2C3E50", fg="white")
        self.status_label.pack(side="left", padx=15)
        self.progress = ttk.Progressbar(self.status_bar, mode="indeterminate", length=150)
        self.progress.pack(side="right", padx=15)

    def _log_welcome(self):
        log_message(self.log_widget, "Selamat datang di Analisis Data Pendidikan Indonesia", "header")
        log_message(self.log_widget, "Versi 1.0 | Powered by Python + Plotly + Tkinter", "info")
        log_message(self.log_widget, "─────────────────────────────────────────────", "info")
        log_message(self.log_widget, "Cara penggunaan:", "info")
        log_message(self.log_widget, "1. Pilih file dataset CSV", "info")
        log_message(self.log_widget, "2. Pilih folder output", "info")
        log_message(self.log_widget, "3. Centang output yang diinginkan", "info")
        log_message(self.log_widget, "4. Klik tombol 'Jalankan Proses'", "info")

    def _browse_file(self):
        path = filedialog.askopenfilename(title="Pilih Dataset CSV", filetypes=[("CSV Files", "*.csv")])
        if path:
            self.dataset_path.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Pilih Folder Output")
        if path:
            self.output_path.set(path)

    def _open_output_folder(self):
        folder = self.output_path.get()
        if not os.path.exists(folder):
            log_message(self.log_widget, f"Folder tidak ditemukan: {folder}", "error")
            return
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def _clear_log(self):
        self.log_widget.config(state="normal")
        self.log_widget.delete("1.0", "end")
        self.log_widget.config(state="disabled")
        self._log_welcome()

    def _start_process_thread(self):
        if self.is_running:
            return
        self.is_running = True
        self.btn_run.config(state="disabled")
        self.status_label.config(text="⏳ Sedang memproses...")
        self.progress.start()
        thread = threading.Thread(target=self._run_process, daemon=True)
        thread.start()

    def _run_process(self):
        try:
            self.after(0, lambda: log_message(self.log_widget, "═══════════════════════════════════", "header"))
            self.after(0, lambda: log_message(self.log_widget, "ANALISIS DATA PENDIDIKAN INDONESIA", "header"))
            self.after(0, lambda: log_message(self.log_widget, "═══════════════════════════════════", "header"))
            data_path = self.dataset_path.get()
            output_dir = self.output_path.get()
            self.after(0, lambda: log_message(self.log_widget, f"📥 Memuat dataset: {data_path}", "info"))
            df = load_data(data_path)
            self.after(0, lambda: log_message(self.log_widget, f"✅ Dataset berhasil dimuat: {len(df)} provinsi", "success"))
            self.after(0, lambda: log_message(self.log_widget, "⚙️ Menjalankan feature engineering...", "info"))
            df = engineer_features(df)
            self.after(0, lambda: log_message(self.log_widget, "✅ Feature engineering selesai: 8 kolom baru ditambahkan", "success"))
            os.makedirs(output_dir, exist_ok=True)
            if self.opt_csv_feature.get():
                self.after(0, lambda: log_message(self.log_widget, "💾 Menyimpan CSV: feature_engineered.csv", "info"))
                df.to_csv(f"{output_dir}/feature_engineered.csv", index=False)
                self.after(0, lambda: log_message(self.log_widget, f"✅ Tersimpan: {output_dir}/feature_engineered.csv", "success"))
            if self.opt_csv_ranking.get():
            if self.opt_csv_ranking.get():
                self.after(0, lambda: log_message(self.log_widget, "💾 Menyimpan CSV: ranking_provinsi.csv", "info"))
                ranking_cols = ['Provinsi', 'Siswa', 'Sekolah', 'Rasio_Putus_Sekolah', 'Rasio_Mengulang', 'Persen_Kelas_Rusak', 'Rasio_Siswa_Guru', 'Persen_Guru_S1_Plus']
                ranking_df = df[ranking_cols].copy()
                ranking_df['Rank_Siswa'] = ranking_df['Siswa'].rank(method='dense', ascending=False).astype(int)
                ranking_df['Rank_Putus_Sekolah'] = ranking_df['Rasio_Putus_Sekolah'].rank(method='dense', ascending=False).astype(int)
                ranking_df['Rank_Kelas_Rusak'] = ranking_df['Persen_Kelas_Rusak'].rank(method='dense', ascending=False).astype(int)
                ranking_df = ranking_df.sort_values('Rank_Siswa', ascending=True)
                ranking_df.to_csv(f"{output_dir}/ranking_provinsi.csv", index=False)
                self.after(0, lambda: log_message(self.log_widget, f"✅ Tersimpan: {output_dir}/ranking_provinsi.csv", "success"))
            if self.opt_charts.get():
                self.after(0, lambda: log_message(self.log_widget, "📊 Membuat chart 1/3: Rasio Putus Sekolah...", "info"))
                self.after(0, lambda: log_message(self.log_widget, "📊 Membuat chart 2/3: Scatter Korelasi...", "info"))
                self.after(0, lambda: log_message(self.log_widget, "📊 Membuat chart 3/3: Kondisi Kelas...", "info"))
                generate_charts(df, output_dir)
                self.after(0, lambda: log_message(self.log_widget, "✅ Chart tersimpan: output/chart1_putus_sekolah.png", "success"))
                self.after(0, lambda: log_message(self.log_widget, "✅ Chart tersimpan: output/chart2_scatter_korelasi.png", "success"))
                self.after(0, lambda: log_message(self.log_widget, "✅ Chart tersimpan: output/chart3_kondisi_kelas.png", "success"))
            self.after(0, lambda: log_message(self.log_widget, "═══════════════════════════════════", "header"))
            self.after(0, lambda: log_message(self.log_widget, "🎉 SELESAI! Semua output telah dibuat.", "success"))
            self.after(0, lambda: log_message(self.log_widget, "═══════════════════════════════════", "header"))
            self.after(0, lambda: self.status_label.config(text=f"✅ Selesai! Output tersimpan di folder: {output_dir}/"))
        except Exception as e:
            self.after(0, lambda: log_message(self.log_widget, f"❌ Error: {str(e)}", "error"))
            self.after(0, lambda: self.status_label.config(text=f"❌ Error: {str(e)}"))
        finally:
            self.is_running = False
            self.after(0, lambda: self.btn_run.config(state="normal"))
            self.after(0, lambda: self.progress.stop())

if __name__ == "__main__":
    app = App()
    app.mainloop()

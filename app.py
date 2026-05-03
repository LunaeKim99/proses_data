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
        self.title("Analisis Data Pendidikan Indonesia")
        self.geometry("950x700")
        self.minsize(750, 550)
        self.configure(bg="#ECF0F1")
        self.option_add("*Font", ("Segoe UI", 10))
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[12, 8])

    def _build_header(self):
        header = tk.Frame(self, bg="#34495E", height=85)
        header.pack(fill="x")
        header.pack_propagate(False)
        title = tk.Label(header, text="Analisis Data Pendidikan Indonesia",
                        font=("Segoe UI", 18, "bold"), bg="#34495E", fg="white")
        title.pack(pady=(18, 3))
        subtitle = tk.Label(header, text="Data Sekolah, Siswa, Guru, dan Infrastruktur per Provinsi",
                           font=("Segoe UI", 10), bg="#34495E", fg="#BDC3C7")
        subtitle.pack()

    def _build_main_area(self):
        main = tk.Frame(self, bg="#ECF0F1")
        main.pack(fill="both", expand=True, padx=12, pady=12)
        main.columnconfigure(0, minsize=300)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = tk.Frame(main, bg="#FFFFFF")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._build_left_panel(left)

        right = tk.Frame(main, bg="#FFFFFF", relief="flat")
        right.grid(row=0, column=1, sticky="nsew")
        self._build_right_panel(right)

    def _build_left_panel(self, panel):
        panel.configure(bg="#FFFFFF")
        
        canvas = tk.Canvas(panel, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFFFFF")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Frame(scrollable_frame, height=2, bg="#E0E0E0").pack(fill="x", padx=20, pady=(20, 0))
        lbl1 = tk.Label(scrollable_frame, text="File Dataset", font=("Segoe UI", 11, "bold"),
                       bg="#FFFFFF", fg="#2C3E50")
        lbl1.pack(anchor="w", padx=20, pady=(15, 8))
        
        file_frame = tk.Frame(scrollable_frame, bg="#FFFFFF")
        file_frame.pack(fill="x", padx=20)
        file_frame.columnconfigure(0, weight=1)
        
        entry_file = ttk.Entry(file_frame, textvariable=self.dataset_path, state="readonly")
        entry_file.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        btn_file = ttk.Button(file_frame, text="Pilih File", command=self._browse_file, width=12)
        btn_file.grid(row=0, column=1)
        
        tk.Frame(scrollable_frame, height=2, bg="#E0E0E0").pack(fill="x", padx=20, pady=(20, 0))
        lbl2 = tk.Label(scrollable_frame, text="Folder Output", font=("Segoe UI", 11, "bold"),
                       bg="#FFFFFF", fg="#2C3E50")
        lbl2.pack(anchor="w", padx=20, pady=(15, 8))
        
        out_frame = tk.Frame(scrollable_frame, bg="#FFFFFF")
        out_frame.pack(fill="x", padx=20)
        out_frame.columnconfigure(0, weight=1)
        
        entry_out = ttk.Entry(out_frame, textvariable=self.output_path, state="readonly")
        entry_out.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        btn_out = ttk.Button(out_frame, text="Pilih Folder", command=self._browse_output, width=12)
        btn_out.grid(row=0, column=1)
        
        tk.Frame(scrollable_frame, height=2, bg="#E0E0E0").pack(fill="x", padx=20, pady=(20, 0))
        lbl3 = tk.Label(scrollable_frame, text="Pilihan Output", font=("Segoe UI", 11, "bold"),
                       bg="#FFFFFF", fg="#2C3E50")
        lbl3.pack(anchor="w", padx=20, pady=(15, 10))
        
        ttk.Checkbutton(scrollable_frame, text="Feature Engineering CSV", variable=self.opt_csv_feature).pack(anchor="w", padx=25, pady=3)
        ttk.Checkbutton(scrollable_frame, text="Ranking Provinsi CSV", variable=self.opt_csv_ranking).pack(anchor="w", padx=25, pady=3)
        ttk.Checkbutton(scrollable_frame, text="Generate Charts (PNG)", variable=self.opt_charts).pack(anchor="w", padx=25, pady=3)
        
        tk.Frame(scrollable_frame, height=2, bg="#E0E0E0").pack(fill="x", padx=20, pady=(25, 0))
        
        btn_frame = tk.Frame(scrollable_frame, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        self.btn_run = create_flat_button(btn_frame, "Jalankan Proses", "#27AE60", self._start_process_thread, is_primary=True)
        self.btn_run.pack(fill="x", pady=(0, 8))
        add_hover_effect(self.btn_run, "#27AE60", hover_colors["#27AE60"])
        
        self.btn_open = create_flat_button(btn_frame, "Buka Folder Output", "#2980B9", self._open_output_folder)
        self.btn_open.pack(fill="x", pady=(0, 8))
        add_hover_effect(self.btn_open, "#2980B9", hover_colors["#2980B9"])
        
        self.btn_clear = create_flat_button(btn_frame, "Bersihkan Log", "#95A5A6", self._clear_log)
        self.btn_clear.pack(fill="x")
        add_hover_effect(self.btn_clear, "#95A5A6", "#7F8C8D")

    def _build_right_panel(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: Log Proses
        log_frame = tk.Frame(notebook, bg="#FFFFFF")
        notebook.add(log_frame, text="  📋 Log Proses  ")
        self._build_log_area(log_frame)
        
        # Tab 2: Tabel Data (CSV SWITCH FIX: renamed from Tabel Ranking)
        table_frame = self._build_table_tab(notebook)
        notebook.add(table_frame, text="  📊 Tabel Data  ")  # CSV SWITCH FIX
        
        # Tab 3: Preview Chart
        chart_frame_tab = self._build_chart_tab(notebook)
        notebook.add(chart_frame_tab, text="  🖼 Preview Chart  ")
        
        self.notebook = notebook

    def _build_log_area(self, parent):
        header_frame = tk.Frame(parent, bg="#FFFFFF")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        tk.Label(header_frame, text="Log Proses", font=("Segoe UI", 12, "bold"),
                bg="#FFFFFF", fg="#2C3E50").pack(side="left")
        
        tk.Frame(parent, height=1, bg="#E0E0E0").pack(fill="x", padx=20)
        
        self.log_widget = scrolledtext.ScrolledText(parent, font=("Consolas", 10),
                                                    bg="#1E1E1E", fg="#D4D4D4",
                                                    state="disabled", wrap="word",
                                                    insertbackground="white")
        self.log_widget.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.log_widget.tag_configure("info", foreground="#4FC3F7")
        self.log_widget.tag_configure("success", foreground="#81C784")
        self.log_widget.tag_configure("warning", foreground="#FFD54F")
        self.log_widget.tag_configure("error", foreground="#E57373")
        self.log_widget.tag_configure("header", foreground="#CE93D8", font=("Consolas", 10, "bold"))

    # CSV SWITCH FIX: Complete rewrite to support both CSV files
    def _build_table_tab(self, parent):
        frame = tk.Frame(parent, bg="#FFFFFF")
        
        # Top bar: dropdown selector
        top_bar = tk.Frame(frame, bg="#F0F0F0", pady=8)
        top_bar.pack(fill="x", padx=0, pady=0)
        
        tk.Label(top_bar, text="  Tampilkan Data:", 
                 font=("Segoe UI", 10, "bold"),
                 bg="#F0F0F0", fg="#2C3E50").pack(side="left", padx=(12, 6))
        
        self.table_choice = tk.StringVar(value="ranking_provinsi.csv")
        dropdown = ttk.Combobox(
            top_bar,
            textvariable=self.table_choice,
            values=["ranking_provinsi.csv", "feature_engineered.csv"],
            state="readonly",
            width=28,
            font=("Segoe UI", 10)
        )
        dropdown.pack(side="left", padx=(0, 8))
        dropdown.bind("<<ComboboxSelected>>", lambda e: self._load_table_data())
        
        ttk.Button(top_bar, text="🔄 Refresh", 
                   command=self._load_table_data).pack(side="left", padx=4)
        
        # Row count label
        self.table_info_label = tk.Label(
            top_bar, text="", 
            font=("Segoe UI", 9, "italic"),
            bg="#F0F0F0", fg="#7F8C8D"
        )
        self.table_info_label.pack(side="right", padx=12)
        
        # Separator
        tk.Frame(frame, height=1, bg="#DCDCDC").pack(fill="x")
        
        # Treeview container
        tree_container = tk.Frame(frame, bg="#FFFFFF")
        tree_container.pack(fill="both", expand=True)
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Treeview - columns set dynamically in _load_table_data()
        self.ranking_tree = ttk.Treeview(tree_container, show="headings", height=20)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.ranking_tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.ranking_tree.xview)
        self.ranking_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.ranking_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Row color tags
        self.ranking_tree.tag_configure("oddrow", background="#F4F6F7")
        self.ranking_tree.tag_configure("evenrow", background="#FFFFFF")
        
        return frame

    # CSV SWITCH FIX: Dynamic loading for both CSV files
    def _load_table_data(self):
        import pandas as pd
        
        # Determine which file to load based on dropdown selection
        selected = self.table_choice.get()
        path = os.path.join(self.output_path.get(), selected)
        
        if not os.path.exists(path):
            self.table_info_label.config(text=f"File tidak ditemukan: {selected}")
            return
        
        df = pd.read_csv(path)
        
        # Dynamically set columns based on the loaded CSV
        columns = list(df.columns)
        self.ranking_tree.config(columns=columns)
        
        # Column display settings
        for col in columns:
            self.ranking_tree.heading(col, text=col.replace("_", " "))
            # Auto-width: wider for text columns, narrower for numeric
            if col in ("Provinsi",):
                width = 160
            elif any(kw in col for kw in ("Rusak", "Kelas", "Guru", "Sekolah", "Nama")):
                width = 130
            elif any(kw in col for kw in ("Rank", "Siswa", "Total")):
                width = 90
            else:
                width = 110
            self.ranking_tree.column(col, width=width, anchor="center", minwidth=60)
        
        # Clear existing rows and insert new data
        self.ranking_tree.delete(*self.ranking_tree.get_children())
        
        for i, row in df.iterrows():
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            values = [row[col] for col in columns]
            self.ranking_tree.insert("", "end", values=values, tags=(tag,))
        
        # Update info label
        self.table_info_label.config(
            text=f"Menampilkan {len(df)} baris · {len(columns)} kolom"
        )

    def _build_chart_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        
        self.chart_var = tk.StringVar(value="chart1_putus_sekolah.png")
        chart_options = [
            "chart1_putus_sekolah.png",
            "chart2_scatter_korelasi.png",
            "chart3_kondisi_kelas.png"
        ]
        
        top_bar = ttk.Frame(frame)
        top_bar.pack(fill='x', pady=(0, 8))
        ttk.Label(top_bar, text="Pilih Chart:").pack(side='left', padx=(0, 6))
        dropdown = ttk.Combobox(top_bar, textvariable=self.chart_var,
                                values=chart_options, state="readonly", width=35)
        dropdown.pack(side='left')
        dropdown.bind("<<ComboboxSelected>>", lambda e: self._show_chart())
        
        ttk.Button(top_bar, text="Refresh", command=self._show_chart).pack(side='left', padx=6)
        
        self.chart_canvas = tk.Label(frame, bg="#2B2B2B",
                                      text="Jalankan proses terlebih dahulu\nuntuk melihat chart.",
                                      fg="#888888", font=("Segoe UI", 11))
        self.chart_canvas.pack(fill='both', expand=True)
        
        return frame

    def _show_chart(self):
        try:
            from PIL import Image, ImageTk
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
            from PIL import Image, ImageTk
        
        filename = self.chart_var.get()
        path = os.path.join(self.output_path.get(), filename)
        if not os.path.exists(path):
            self.chart_canvas.config(text="File chart belum ada.\nJalankan proses terlebih dahulu.", image="")
            return
        
        img = Image.open(path)
        canvas_w = self.chart_canvas.winfo_width() or 600
        canvas_h = self.chart_canvas.winfo_height() or 400
        img.thumbnail((canvas_w, canvas_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.chart_canvas.config(image=photo, text="")
        self.chart_canvas._image_ref = photo

    def _build_status_bar(self):
        self.status_bar = tk.Frame(self, bg="#34495E", height=32)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_label = tk.Label(self.status_bar, text="Siap. Pilih file dataset dan klik Jalankan Proses.",
                                    font=("Segoe UI", 9), bg="#34495E", fg="white")
        self.status_label.pack(side="left", padx=15, pady=6)
        self.progress = ttk.Progressbar(self.status_bar, mode="indeterminate", length=140)
        self.progress.pack(side="right", padx=15, pady=5)

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
        self.status_label.config(text="Sedang memproses...")
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
            self.after(0, lambda: log_message(self.log_widget, f"Memuat dataset: {data_path}", "info"))
            df = load_data(data_path)
            self.after(0, lambda: log_message(self.log_widget, f"Dataset berhasil dimuat: {len(df)} provinsi", "success"))
            self.after(0, lambda: log_message(self.log_widget, "Menjalankan feature engineering...", "info"))
            df = engineer_features(df)
            self.after(0, lambda: log_message(self.log_widget, "Feature engineering selesai: 8 kolom baru ditambahkan", "success"))
            os.makedirs(output_dir, exist_ok=True)
            if self.opt_csv_feature.get():
                self.after(0, lambda: log_message(self.log_widget, "Menyimpan CSV: feature_engineered.csv", "info"))
                df.to_csv(f"{output_dir}/feature_engineered.csv", index=False)
                self.after(0, lambda: log_message(self.log_widget, f"Tersimpan: {output_dir}/feature_engineered.csv", "success"))
            if self.opt_csv_ranking.get():
                self.after(0, lambda: log_message(self.log_widget, "Menyimpan CSV: ranking_provinsi.csv", "info"))
                ranking_cols = ['Provinsi', 'Siswa', 'Sekolah', 'Rasio_Putus_Sekolah', 'Rasio_Mengulang', 'Persen_Kelas_Rusak', 'Rasio_Siswa_Guru', 'Persen_Guru_S1_Plus']
                ranking_df = df[ranking_cols].copy()
                ranking_df['Rank_Siswa'] = ranking_df['Siswa'].rank(method='dense', ascending=False).astype(int)
                ranking_df['Rank_Putus_Sekolah'] = ranking_df['Rasio_Putus_Sekolah'].rank(method='dense', ascending=False).astype(int)
                ranking_df['Rank_Kelas_Rusak'] = ranking_df['Persen_Kelas_Rusak'].rank(method='dense', ascending=False).astype(int)
                ranking_df = ranking_df.sort_values('Rank_Siswa', ascending=True)
                ranking_df.to_csv(f"{output_dir}/ranking_provinsi.csv", index=False)
                self.after(0, lambda: log_message(self.log_widget, f"Tersimpan: {output_dir}/ranking_provinsi.csv", "success"))
            if self.opt_charts.get():
                self.after(0, lambda: log_message(self.log_widget, "Membuat chart 1/3: Rasio Putus Sekolah...", "info"))
                self.after(0, lambda: log_message(self.log_widget, "Membuat chart 2/3: Scatter Korelasi...", "info"))
                self.after(0, lambda: log_message(self.log_widget, "Membuat chart 3/3: Kondisi Kelas...", "info"))
                generate_charts(df, output_dir)
                self.after(0, lambda: log_message(self.log_widget, "Chart tersimpan: output/chart1_putus_sekolah.png", "success"))
                self.after(0, lambda: log_message(self.log_widget, "Chart tersimpan: output/chart2_scatter_korelasi.png", "success"))
                self.after(0, lambda: log_message(self.log_widget, "Chart tersimpan: output/chart3_kondisi_kelas.png", "success"))
            self.after(0, lambda: log_message(self.log_widget, "═══════════════════════════════════", "header"))
            self.after(0, lambda: log_message(self.log_widget, "SELESAI! Semua output telah dibuat.", "success"))
            self.after(0, lambda: log_message(self.log_widget, "═══════════════════════════════════", "header"))
            self.after(0, lambda: self.status_label.config(text=f"Selesai! Output tersimpan di folder: {output_dir}/"))
            # Auto-switch to Table tab and load data
            self.after(0, self._load_table_data)
            self.after(0, self._show_chart)
            self.after(0, lambda: self.notebook.select(1))
        except Exception as e:
            self.after(0, lambda: log_message(self.log_widget, f"Error: {str(e)}", "error"))
            self.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
        finally:
            self.is_running = False
            self.after(0, lambda: self.btn_run.config(state="normal"))
            self.after(0, lambda: self.progress.stop())

if __name__ == "__main__":
    app = App()
    app.mainloop()

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

# ── DARK THEME COLOR PALETTE ────────────────────────────
COLORS = {
    # Backgrounds
    "bg_main": "#1A1A2E",      # deep dark navy — main window background
    "bg_panel": "#16213E",      # slightly lighter — left/right panel background
    "bg_card": "#0F3460",       # card/section background
    "bg_input": "#1A1A2E",     # entry/combobox background
    "bg_hover": "#1F4068",      # hover state for interactive elements
    "bg_terminal": "#0D0D0D",   # log terminal background (near-black)

    # Header & Status Bar
    "bg_header": "#0F3460",     # header background
    "bg_statusbar": "#0F3460",  # status bar background

    # Borders & Separators
    "border": "#2A2D3E",       # subtle border color
    "separator": "#2A2D3E",    # separator line color

    # Text
    "text_primary": "#E0E0E0",  # main text
    "text_secondary": "#A0AEC0", # muted/secondary text
    "text_header": "#FFFFFF",    # header title text
    "text_subtitle": "#8892A4", # subtitle text

    # Accent Colors (buttons)
    "accent_green": "#00B894",    # primary action button (run)
    "accent_green_hover": "#00A381",
    "accent_blue": "#0984E3",    # secondary button (open folder)
    "accent_blue_hover": "#0773C5",
    "accent_gray": "#2D3436",    # clear log button
    "accent_gray_hover": "#3D4446",

    # Treeview / Table
    "tree_bg": "#16213E",        # treeview background
    "tree_odd": "#1C2847",       # odd row
    "tree_even": "#16213E",      # even row
    "tree_selected": "#0984E3",   # selected row highlight
    "tree_heading": "#0F3460",    # column heading background
    "tree_fg": "#E0E0E0",       # treeview text

    # Log terminal text colors
    "log_info": "#4FC3F7",
    "log_success": "#81C784",
    "log_warning": "#FFD54F",
    "log_error": "#E57373",
    "log_header": "#CE93D8",

    # Notebook tabs
    "tab_active": "#0F3460",     # active tab background
    "tab_inactive": "#1A1A2E",  # inactive tab background
    "tab_text": "#E0E0E0",       # tab label text
}

hover_colors = {
    COLORS["accent_green"]: COLORS["accent_green_hover"],
    COLORS["accent_blue"]:  COLORS["accent_blue_hover"],
    COLORS["accent_gray"]:  COLORS["accent_gray_hover"],
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
        self.configure(bg=COLORS["bg_main"])  # DARK THEME
        self.option_add("*Font", ("Segoe UI", 10))
        self.option_add("*Background", COLORS["bg_main"])  # DARK THEME
        self.option_add("*Foreground", COLORS["text_primary"])  # DARK THEME

        # ttk Style for dark theme
        style = ttk.Style(self)
        style.theme_use("clam")

        # Notebook tabs
        style.configure("TNotebook",
            background=COLORS["bg_main"],  # DARK THEME
            borderwidth=0,
            tabmargins=[2, 2, 2, 0]
        )
        style.configure("TNotebook.Tab",
            background=COLORS["tab_inactive"],  # DARK THEME
            foreground=COLORS["tab_text"],  # DARK THEME
            padding=[12, 8],
            font=("Segoe UI", 10)
        )
        style.map("TNotebook.Tab",
            background=[("selected", COLORS["tab_active"]),  # DARK THEME
                        ("active", COLORS["bg_hover"])],  # DARK THEME
            foreground=[("selected", "#FFFFFF"),
                        ("active", COLORS["text_primary"])]  # DARK THEME
        )

        # Progressbar
        style.configure("green.Horizontal.TProgressbar",
            troughcolor=COLORS["bg_card"],  # DARK THEME
            background=COLORS["accent_green"],  # DARK THEME
            darkcolor=COLORS["accent_green"],  # DARK THEME
            lightcolor="#00D4A8",
            bordercolor=COLORS["bg_card"],  # DARK THEME
            thickness=14
        )

        # Treeview
        style.configure("Treeview",
            background=COLORS["tree_bg"],  # DARK THEME
            foreground=COLORS["tree_fg"],  # DARK THEME
            fieldbackground=COLORS["tree_bg"],  # DARK THEME
            rowheight=26,
            font=("Segoe UI", 10)
        )
        style.configure("Treeview.Heading",
            background=COLORS["tree_heading"],  # DARK THEME
            foreground=COLORS["text_primary"],  # DARK THEME
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        style.map("Treeview",
            background=[("selected", COLORS["tree_selected"])],  # DARK THEME
            foreground=[("selected", "#FFFFFF")]
        )
        style.map("Treeview.Heading",
            background=[("active", COLORS["bg_hover"])]  # DARK THEME
        )

        # Scrollbar
        style.configure("Vertical.TScrollbar",
            background=COLORS["bg_card"],  # DARK THEME
            troughcolor=COLORS["bg_panel"],  # DARK THEME
            arrowcolor=COLORS["text_secondary"],  # DARK THEME
            borderwidth=0
        )
        style.configure("Horizontal.TScrollbar",
            background=COLORS["bg_card"],  # DARK THEME
            troughcolor=COLORS["bg_panel"],  # DARK THEME
            arrowcolor=COLORS["text_secondary"],  # DARK THEME
            borderwidth=0
        )

        # Entry
        style.configure("TEntry",
            fieldbackground=COLORS["bg_input"],  # DARK THEME
            foreground=COLORS["text_primary"],  # DARK THEME
            insertcolor=COLORS["text_primary"],  # DARK THEME
            bordercolor=COLORS["border"],  # DARK THEME
            lightcolor=COLORS["border"],  # DARK THEME
            darkcolor=COLORS["border"]  # DARK THEME
        )

        # Combobox
        style.configure("TCombobox",
            fieldbackground=COLORS["bg_input"],  # DARK THEME
            background=COLORS["bg_input"],  # DARK THEME
            foreground=COLORS["text_primary"],  # DARK THEME
            arrowcolor=COLORS["text_secondary"],  # DARK THEME
            selectbackground=COLORS["bg_card"],  # DARK THEME
            selectforeground=COLORS["text_primary"]  # DARK THEME
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", COLORS["bg_input"])],  # DARK THEME
            foreground=[("readonly", COLORS["text_primary"])]  # DARK THEME
        )

        # Button (ttk)
        style.configure("TButton",
            background=COLORS["bg_card"],  # DARK THEME
            foreground=COLORS["text_primary"],  # DARK THEME
            relief="flat",
            padding=6
        )
        style.map("TButton",
            background=[("active", COLORS["bg_hover"])]  # DARK THEME
        )

        # Checkbutton
        style.configure("TCheckbutton",
            background=COLORS["bg_panel"],  # DARK THEME
            foreground=COLORS["text_primary"],  # DARK THEME
            focuscolor=COLORS["accent_green"]  # DARK THEME
        )
        style.map("TCheckbutton",
            background=[("active", COLORS["bg_panel"])],  # DARK THEME
            foreground=[("active", COLORS["text_primary"])]  # DARK THEME
        )

        # Frame
        style.configure("TFrame",
            background=COLORS["bg_panel"]  # DARK THEME
        )

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["bg_header"], height=85)  # DARK THEME
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header,
                 text="Analisis Data Pendidikan Indonesia",
                 font=("Segoe UI", 18, "bold"),
                 bg=COLORS["bg_header"],  # DARK THEME
                 fg=COLORS["text_header"]  # DARK THEME
        ).pack(pady=(18, 3))
        tk.Label(header,
                 text="Data Sekolah, Siswa, Guru, dan Infrastruktur per Provinsi",
                 font=("Segoe UI", 10),
                 bg=COLORS["bg_header"],  # DARK THEME
                 fg=COLORS["text_subtitle"]  # DARK THEME
        ).pack()

    def _build_main_area(self):
        main = tk.Frame(self, bg=COLORS["bg_main"])  # DARK THEME
        main.pack(fill="both", expand=True, padx=12, pady=12)
        main.columnconfigure(0, minsize=300)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = tk.Frame(main, bg=COLORS["bg_panel"])  # DARK THEME
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._build_left_panel(left)

        right = tk.Frame(main, bg=COLORS["bg_panel"])  # DARK THEME
        right.grid(row=0, column=1, sticky="nsew")
        self._build_right_panel(right)

    def _build_left_panel(self, panel):
        panel.configure(bg=COLORS["bg_panel"])  # DARK THEME
        
        canvas = tk.Canvas(panel, bg=COLORS["bg_panel"], highlightthickness=0)  # DARK THEME
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_panel"])  # DARK THEME
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Frame(scrollable_frame, height=2, bg=COLORS["separator"]).pack(fill="x", padx=20, pady=(20, 0))  # DARK THEME
        tk.Label(scrollable_frame, text="📂 File Dataset", font=("Segoe UI", 11, "bold"),
                bg=COLORS["bg_panel"], fg=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(15, 8))  # DARK THEME
        
        file_frame = tk.Frame(scrollable_frame, bg=COLORS["bg_panel"])  # DARK THEME
        file_frame.pack(fill="x", padx=20)
        file_frame.columnconfigure(0, weight=1)
        
        entry_file = ttk.Entry(file_frame, textvariable=self.dataset_path, state="readonly")
        entry_file.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        btn_file = ttk.Button(file_frame, text="Pilih File", command=self._browse_file, width=12)
        btn_file.grid(row=0, column=1)
        
        tk.Frame(scrollable_frame, height=2, bg=COLORS["separator"]).pack(fill="x", padx=20, pady=(20, 0))  # DARK THEME
        tk.Label(scrollable_frame, text="📁 Folder Output", font=("Segoe UI", 11, "bold"),
                bg=COLORS["bg_panel"], fg=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(15, 8))  # DARK THEME
        
        out_frame = tk.Frame(scrollable_frame, bg=COLORS["bg_panel"])  # DARK THEME
        out_frame.pack(fill="x", padx=20)
        out_frame.columnconfigure(0, weight=1)
        
        entry_out = ttk.Entry(out_frame, textvariable=self.output_path, state="readonly")
        entry_out.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        btn_out = ttk.Button(out_frame, text="Pilih Folder", command=self._browse_output, width=12)
        btn_out.grid(row=0, column=1)
        
        tk.Frame(scrollable_frame, height=2, bg=COLORS["separator"]).pack(fill="x", padx=20, pady=(20, 0))  # DARK THEME
        tk.Label(scrollable_frame, text="⚙️ Pilihan Output", font=("Segoe UI", 11, "bold"),
                bg=COLORS["bg_panel"], fg=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))  # DARK THEME
        
        ttk.Checkbutton(scrollable_frame, text="Feature Engineering CSV", variable=self.opt_csv_feature).pack(anchor="w", padx=25, pady=3)
        ttk.Checkbutton(scrollable_frame, text="Ranking Provinsi CSV", variable=self.opt_csv_ranking).pack(anchor="w", padx=25, pady=3)
        ttk.Checkbutton(scrollable_frame, text="Generate Charts (PNG)", variable=self.opt_charts).pack(anchor="w", padx=25, pady=3)
        
        tk.Frame(scrollable_frame, height=2, bg=COLORS["separator"]).pack(fill="x", padx=20, pady=(25, 0))  # DARK THEME
        
        btn_frame = tk.Frame(scrollable_frame, bg=COLORS["bg_panel"])  # DARK THEME
        btn_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        self.btn_run = create_flat_button(btn_frame, "Jalankan Proses", COLORS["accent_green"], self._start_process_thread, is_primary=True)  # DARK THEME
        self.btn_run.pack(fill="x", pady=(0, 8))
        add_hover_effect(self.btn_run, COLORS["accent_green"], hover_colors[COLORS["accent_green"]])  # DARK THEME
        
        self.btn_open = create_flat_button(btn_frame, "Buka Folder Output", COLORS["accent_blue"], self._open_output_folder)  # DARK THEME
        self.btn_open.pack(fill="x", pady=(0, 8))
        add_hover_effect(self.btn_open, COLORS["accent_blue"], hover_colors[COLORS["accent_blue"]])  # DARK THEME
        
        self.btn_clear = create_flat_button(btn_frame, "Bersihkan Log", COLORS["accent_gray"], self._clear_log)  # DARK THEME
        self.btn_clear.pack(fill="x")
        add_hover_effect(self.btn_clear, COLORS["accent_gray"], hover_colors[COLORS["accent_gray"]])  # DARK THEME

    def _build_right_panel(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: Log Proses
        log_frame = tk.Frame(notebook, bg=COLORS["bg_panel"])  # DARK THEME
        notebook.add(log_frame, text="  📋 Log Proses  ")
        self._build_log_area(log_frame)
        
        # Tab 2: Tabel Data
        table_frame = self._build_table_tab(notebook)
        notebook.add(table_frame, text="  📊 Tabel Data  ")
        
        # Tab 3: Preview Chart
        chart_frame_tab = self._build_chart_tab(notebook)
        notebook.add(chart_frame_tab, text="  🖼 Preview Chart  ")
        
        self.notebook = notebook

    def _build_log_area(self, parent):
        header_frame = tk.Frame(parent, bg=COLORS["bg_panel"])  # DARK THEME
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        tk.Label(header_frame,
                 text="📋 Log Proses",
                 font=("Segoe UI", 12, "bold"),
                 bg=COLORS["bg_panel"],  # DARK THEME
                 fg=COLORS["text_primary"]  # DARK THEME
        ).pack(side="left")
        
        tk.Frame(parent, height=1, bg=COLORS["separator"]).pack(fill="x", padx=20)  # DARK THEME
        
        self.log_widget = scrolledtext.ScrolledText(
            parent,
            font=("Consolas", 11),
            bg=COLORS["bg_terminal"],  # DARK THEME
            fg="#D4D4D4",
            state="disabled",
            wrap="word",
            insertbackground="white",
            selectbackground=COLORS["bg_card"],  # DARK THEME
            spacing1=2, spacing3=2
        )
        self.log_widget.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        self.log_widget.tag_configure("info", foreground=COLORS["log_info"])  # DARK THEME
        self.log_widget.tag_configure("success", foreground=COLORS["log_success"])  # DARK THEME
        self.log_widget.tag_configure("warning", foreground=COLORS["log_warning"])  # DARK THEME
        self.log_widget.tag_configure("error", foreground=COLORS["log_error"])  # DARK THEME
        self.log_widget.tag_configure("header", foreground=COLORS["log_header"], font=("Consolas", 11, "bold"))  # DARK THEME

    def _build_table_tab(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg_panel"])  # DARK THEME
        
        # Top bar: dropdown selector
        top_bar = tk.Frame(frame, bg=COLORS["bg_card"], pady=8)  # DARK THEME
        top_bar.pack(fill="x", padx=0, pady=0)
        
        tk.Label(top_bar,
                 text="  Tampilkan Data:",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS["bg_card"],  # DARK THEME
                 fg=COLORS["text_primary"]  # DARK THEME
        ).pack(side="left", padx=(12, 6))
        
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
            bg=COLORS["bg_card"],  # DARK THEME
            fg=COLORS["text_secondary"]  # DARK THEME
        )
        self.table_info_label.pack(side="right", padx=12)
        
        # Separator
        tk.Frame(frame, height=1, bg=COLORS["separator"]).pack(fill="x")  # DARK THEME
        
        # Treeview container
        tree_container = tk.Frame(frame, bg=COLORS["tree_bg"])  # DARK THEME
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
        self.ranking_tree.tag_configure("oddrow", background=COLORS["tree_odd"])  # DARK THEME
        self.ranking_tree.tag_configure("evenrow", background=COLORS["tree_even"])  # DARK THEME
        
        return frame

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
        frame = tk.Frame(parent, bg=COLORS["bg_panel"], padx=10, pady=10)  # DARK THEME
        
        top_bar = tk.Frame(frame, bg=COLORS["bg_card"], pady=6)  # DARK THEME
        top_bar.pack(fill="x", pady=(0, 8))
        
        tk.Label(top_bar,
                 text="  🖼 Pilih Chart:",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS["bg_card"],  # DARK THEME
                 fg=COLORS["text_primary"]  # DARK THEME
        ).pack(side="left", padx=(8, 6))
        
        self.chart_var = tk.StringVar(value="chart1_putus_sekolah.png")
        chart_options = [
            "chart1_putus_sekolah.png",
            "chart2_scatter_korelasi.png",
            "chart3_kondisi_kelas.png"
        ]
        
        dropdown = ttk.Combobox(top_bar, textvariable=self.chart_var,
                                values=chart_options, state="readonly", width=35)
        dropdown.pack(side="left")
        dropdown.bind("<<ComboboxSelected>>", lambda e: self._show_chart())
        
        ttk.Button(top_bar, text="Refresh", command=self._show_chart).pack(side="left", padx=6)
        
        self.chart_canvas = tk.Label(
            frame,
            bg=COLORS["bg_terminal"],  # DARK THEME
            text="Jalankan proses terlebih dahulu\nuntuk melihat chart.",
            fg="#555555",
            font=("Segoe UI", 11)
        )
        self.chart_canvas.pack(fill="both", expand=True)
        
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
        self.status_bar = tk.Frame(self, bg=COLORS["bg_statusbar"], height=32)  # DARK THEME
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            self.status_bar,
            text="Siap. Pilih file dataset dan klik Jalankan Proses.",
            font=("Segoe UI", 9),
            bg=COLORS["bg_statusbar"],  # DARK THEME
            fg=COLORS["text_primary"]  # DARK THEME
        )
        self.status_label.pack(side="left", padx=15, pady=6)
        
        self.progress = ttk.Progressbar(
            self.status_bar,
            style="green.Horizontal.TProgressbar",
            mode="indeterminate",
            length=140
        )
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

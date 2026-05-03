import tkinter as tk
from datetime import datetime

def create_flat_button(parent, text: str, bg: str, command, is_primary=False):
    font_size = ("Segoe UI", 11, "bold") if is_primary else ("Segoe UI", 10)
    height = 2 if is_primary else 1
    btn = tk.Button(parent, text=text, bg=bg, fg="#FFFFFF",
                   font=font_size, relief="flat", cursor="hand2", borderwidth=0,
                   activebackground=bg, activeforeground="#FFFFFF",
                   command=command, height=height)
    return btn

def add_hover_effect(button: tk.Button, normal_color: str, hover_color: str) -> None:
    def on_enter(e):
        button.config(bg=hover_color)
    def on_leave(e):
        button.config(bg=normal_color)
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

def log_message(widget, message: str, tag: str = "info") -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] {message}\n"
    widget.config(state="normal")
    widget.insert("end", formatted, tag)
    widget.config(state="disabled")
    widget.see("end")

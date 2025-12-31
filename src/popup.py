import tkinter as tk
from font.font import create_fonts

def show_popup(root, message):
    fonts = create_fonts(root)

    popup = tk.Toplevel(root)
    popup.configure(bg="#262b2b")
    popup.resizable(0, 0)
    popup.overrideredirect(True)
    popup.grab_set()
    popup.update_idletasks()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    width = 400
    height = 120
    x = root_x + (root_width // 2) - (width // 2)
    y = root_y + (root_height // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

    frame = tk.Frame(popup, bg="#262b2b")
    frame.pack(expand=True, fill="both")

    tk.Label(
        frame,
        text=message,
        fg="white",
        bg="#262b2b",
        font=fonts["popup_font"],
        anchor="center",
        wraplength=360,
        justify="center"
    ).pack(expand=True, pady=(20, 10))

    tk.Button(
        frame,
        text="Close",
        command=popup.destroy,
        bg="#3a3f3f",
        fg="white",
        font=fonts["button_font"],
        bd=0,
        relief="flat",
        highlightthickness=0,
        width=12,
    ).pack(pady=(0, 15))
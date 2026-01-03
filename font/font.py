import tkinter as tk
import tkinter.font as tkfont

def create_fonts(root):
    try:
        root.tk.call("font", "create", "AgaveCustom", "-family", "Agave Nerd Font", "-size", 12, "-weight", "bold")
    except tk.TclError:
        pass
    fonts = {
        "title_font": tkfont.Font(name="AgaveCustom", exists=True),
        "header_font": ("Agave Nerd Font", 15, "bold"),
        "menus_font": ("Agave Nerd Font", 20, "bold"),
        "artist_font": ("Agave Nerd Font", 10, "bold"),
        "info_title": ("Agave Nerd Font", 14, "bold"),
        "message": ("Agave Nerd Font", 12),
        "button_font": ("Agave Nerd Font", 10)
    }
    
    return fonts
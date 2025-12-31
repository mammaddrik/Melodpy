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
        "card_title_font": ("Agave Nerd Font", 12, "bold"),
        "card_artist_font": ("Agave Nerd Font", 10, "bold"),
        "popup_font": ("Agave Nerd Font", 12, "bold"),
        "button_font": ("Agave Nerd Font", 12)
    }
    
    return fonts
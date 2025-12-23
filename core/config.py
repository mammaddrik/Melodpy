import pygame
from tkinter import font as tkfont

BG_MAIN = "#1f2323"
BG_CARD = "#2b3030"

def init_app(root):
    root.title("Music player")
    root.geometry("1230x480")
    root.configure(bg=BG_MAIN)
    root.resizable(False, False)

    pygame.mixer.init()

    root.tk.call(
        "font", "create", "AgaveCustom",
        "-family", "Agave Nerd Font Propo",
        "-size", 14,
        "-weight", "bold"
    )

    tkfont.Font(name="AgaveCustom", exists=True)

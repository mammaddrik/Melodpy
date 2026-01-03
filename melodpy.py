#!/usr/bin/env python
#
#  /$$      /$$           /$$                 /$$                    
# | $$$    /$$$          | $$                | $$                    
# | $$$$  /$$$$  /$$$$$$ | $$  /$$$$$$   /$$$$$$$  /$$$$$$  /$$   /$$
# | $$ $$/$$ $$ /$$__  $$| $$ /$$__  $$ /$$__  $$ /$$__  $$| $$  | $$
# | $$  $$$| $$| $$$$$$$$| $$| $$  \ $$| $$  | $$| $$  \ $$| $$  | $$
# | $$\  $ | $$| $$_____/| $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$
# | $$ \/  | $$|  $$$$$$$| $$|  $$$$$$/|  $$$$$$$| $$$$$$$/|  $$$$$$$
# |__/     |__/ \_______/|__/ \______/  \_______/| $$____/  \____  $$
#                                                | $$       /$$  | $$
#                                                | $$      |  $$$$$$/
#                                                |__/       \______/ 
#                            Music Player                            
#                         Github: mammaddrik                         

#::::: Libraries to be installed :::::
try:
    import pygame
    import mutagen
    import regex
    import arabic_reshaper
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TCON, TDRC
    from lyricsgenius import Genius
    from bidi.algorithm import get_display
    from PIL import Image, ImageTk
except ImportError:
    os.system("pip install -r requirements.txt")

#::::: Default Library :::::
import tkinter as tk
from tkinter import font as tkfont, messagebox, filedialog
import os
import io
import contextlib
import subprocess
import sys
import json
import socket
import webbrowser

#::::: Fonts :::::
from font.font import create_fonts

#::::: Melodpy :::::
root = tk.Tk()
w, h = 1200, 480
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = (screen_w - w) // 2
y = (screen_h - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")
root.configure(bg="#1f2323")
root.overrideredirect(True)
fonts = create_fonts(root)
# root.resizable(0, 0)
pygame.mixer.init()

#::::: Header :::::
header = tk.Frame(root, bg="#1f2323", height=50)
header.pack(fill="x", side="top")
title = tk.Label(header, text="Melodpy", bg="#3a3f3f", fg="#ffffff",
                 font=fonts["header_font"], padx=20, pady=6)
title.place(relx=0.5, anchor="n")
canvas = tk.Canvas(header, width=20, height=20, bg="#1f2424", highlightthickness=0)
canvas.pack(side="right", padx=10, pady=10)
circle = canvas.create_oval(2, 2, 18, 18, fill="#c94a44", outline="")

def on_enter(e):
    canvas.itemconfig(circle, fill="#e0443e")
def on_leave(e):
    canvas.itemconfig(circle, fill="#ff5f56")
def close_app(e):
    save_favorites()
    root.destroy()

canvas.bind("<Enter>", on_enter)
canvas.bind("<Leave>", on_leave)
canvas.bind("<Button-1>", close_app)

def start_move(e):
    header._x = e.x_root - root.winfo_x()
    header._y = e.y_root - root.winfo_y()

def do_move(e):
    x = e.x_root - header._x
    y = e.y_root - header._y
    root.geometry(f"+{x}+{y}")

header.bind("<Button-1>", start_move)
header.bind("<B1-Motion>", do_move)
title.bind("<Button-1>", start_move)
title.bind("<B1-Motion>", do_move)

#::::: Main :::::
main = tk.Frame(root, bg="#1f2323")
main.pack(fill="both", expand=True,pady=8)
content = tk.Frame(main, bg="#1f2323")
content.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()

# try:
#     root.mainloop()
# except KeyboardInterrupt:
#     sys.exit()
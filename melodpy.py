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
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TCON, TDRC
    from lyricsgenius import Genius
    import arabic_reshaper
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

#::::: Fonts :::::
from font.font import create_fonts

#::::: Src :::::
from src.header import header

#::::: Window :::::
root = tk.Tk()
w, h = 1230, 480
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = (screen_w - w) // 2
y = (screen_h - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")
root.configure(bg="#1f2323")
root.overrideredirect(True)
fonts = create_fonts(root)
header(root, fonts)
pygame.mixer.init()

#::::: Song Data :::::
song_files = []
active_playlist = []
current_playlist_index = 0
current_index = 0
offset_sec = 0
paused = False
is_playing = False
is_loop = False
search_cache = {}
card_widgets = []

#::::: Main :::::
main = tk.Frame(root, bg="#00ffff")
main.pack(fill="both", expand=True, padx=20, pady=10)
content = tk.Frame(root, bg="#ffbb00")
content.pack(fill="both", expand=True, padx=10, pady=10)

#::::: Menus :::::
library_header = tk.Frame(main, bg="#1f2323")
library_header.pack(fill="x", pady=5)
library_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/library.png").resize((24, 24)))
heart_empty_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/heart_empty.png").resize((24, 24)))
library_icon = tk.Label(library_header, image=library_icon_img, bg="#1f2323", bd=0, highlightthickness=0)
library_icon.pack(side="left", padx=(0, 5))
library_label = tk.Label(library_header, text="Library", fg="#ffffff", bg="#1f2323", font=fonts["menus_font"])
library_label.pack(side="left", anchor="w")

#::::: Library Scroll :::::
library_canvas = tk.Canvas(content, bg="#1f2323", bd=0, highlightthickness=0)
library_canvas.pack(side="top", fill="x", expand=False)
albums_frame = tk.Frame(library_canvas, bg="#1f2323")
library_canvas.create_window((0, 0), window=albums_frame, anchor="nw")
def update_scrollregion(event=None):
    library_canvas.configure(scrollregion=library_canvas.bbox("all"))
albums_frame.bind("<Configure>", update_scrollregion)
def on_mousewheel(event):
    scroll_speed = 0.03
    if sys.platform.startswith("win"):
        delta = -1 * (event.delta / 120)
    elif sys.platform.startswith("linux"):
        delta = -1 if event.num == 5 else 1
    else:
        delta = -1 * (event.delta)
    current = library_canvas.xview()[0]
    new = current + delta * scroll_speed
    new = max(0, min(new, 1))
    library_canvas.xview_moveto(new)

library_canvas.bind_all("<MouseWheel>", on_mousewheel)
library_canvas.bind_all("<Button-4>", on_mousewheel)
library_canvas.bind_all("<Button-5>", on_mousewheel)


#::::: Search :::::
search_var = tk.StringVar()
search_frame = tk.Frame(library_header, bg="#2b3030")
search_frame.pack(side="right", padx=5, pady=5)
search_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/search.png").resize((24, 24)))
search_icon = tk.Label(search_frame, image=search_icon_img, bg="#2b3030", bd=0, highlightthickness=0)
search_icon.pack(side="left", padx=3)
search_entry = tk.Entry(search_frame, textvariable=search_var, font=fonts["title_font"], bg="#2b3030", fg="white", insertbackground="white", relief="flat", bd=0, highlightthickness=0, width=25)
search_entry.pack(side="left")
placeholder_text = "Search song or artist..."

def on_entry_click(event):
    if search_entry.get() == placeholder_text:
        search_entry.delete(0, "end")
        search_entry.config(fg="white")

def on_focusout(event):
    if search_entry.get() == "":
        search_entry.insert(0, placeholder_text)
        search_entry.config(fg="gray")
        root.focus()

search_entry.insert(0, placeholder_text)
search_entry.config(fg="gray")
search_entry.bind("<FocusIn>", on_entry_click)
search_entry.bind("<FocusOut>", on_focusout)

root.mainloop()

# try:
#     root.mainloop()
# except KeyboardInterrupt:
#     sys.exit()
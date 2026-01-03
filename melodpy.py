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

#::::: Genius :::::
GENIUS_TOKEN = ""

genius = Genius(
    GENIUS_TOKEN,
    timeout=10,
    retries=1,
    remove_section_headers=True
)

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

#:::::  :::::
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
lyric_is_open = False

#::::: Header :::::
header = tk.Frame(root, bg="#1f2323", height=50)
header.pack(fill="x", side="top")
title = tk.Label(header, text="Melodpy", bg="#3a3f3f", fg="#ffffff", font=fonts["header_font"], padx=20, pady=6)
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

#::::: Favorites :::::
FAVORITES_FILE = "favorites.json"
def save_favorites():
    current_favs = [mp3 for card, mp3, idx in card_widgets if getattr(card, "is_favorite", False)]
    try:
        with open(FAVORITES_FILE, "w") as f:
            json.dump(current_favs, f, indent=4)
    except Exception as e:
        pass

def on_closing():
    save_favorites()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

def load_favorites():
    try:
        with open(FAVORITES_FILE, "r") as f:
            fav_list = json.load(f)
    except:
        fav_list = []
    valid_favs = [f for f in fav_list if os.path.exists(f)]
    if valid_favs != fav_list:
        with open(FAVORITES_FILE, "w") as f:
            json.dump(valid_favs, f)
    for card, mp3, idx in card_widgets:
        if mp3 in valid_favs:
            card.is_favorite = True
            card.heart_label.config(image=card.heart_filled)

#::::: Check Connection :::::
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

#::::: Popup :::::
def popup(message, title="Info", width = 400, height = 140):
    popup = tk.Toplevel(root)
    popup.configure(bg="#262b2b")
    popup.overrideredirect(True)
    popup.grab_set()
    popup.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    x = root_x + (root_w // 2) - (width // 2)
    y = root_y + (root_h // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

    frame = tk.Frame(popup, bg="#262b2b")
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text=title, fg="white", bg="#262b2b", font=fonts["info_title"]).pack(pady=(15, 5))
    tk.Label(frame, text=message, fg="white", bg="#262b2b", font=fonts["message"], anchor="center").pack(pady=(0, 10))
    tk.Button(frame, text="Close", command=popup.destroy, bg="#3a3f3f", fg="white", font=fonts["button_font"], bd=0, relief="flat", highlightthickness=0, width=12, height=2).pack(pady=(0, 15))

#::::: Open Github :::::
def open_github(event=None):
    if not is_connected():
        popup("You are not connected to the internet.\nPlease check your connection and try again.",title="No Internet Connection")
        return
    try:
        webbrowser.open_new_tab("https://github.com/mammaddrik")
    except Exception as e:
        popup(f"Cannot open browser:\n{e}", title="Error")
title.bind("<Double-Button-1>", open_github)
title.config(cursor="hand2")

#::::: Main :::::
main = tk.Frame(root, bg="#1f2323")
main.pack(fill="both", expand=True,pady=8)
content = tk.Frame(main, bg="#1f2323")
content.pack(fill="both", expand=True, padx=10, pady=10)
library_header = tk.Frame(content, bg="#1f2323")
library_header.pack(fill="x", pady=5)
library_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/library.png").resize((24, 24)))
heart_empty_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/heart_empty.png").resize((24, 24)))
library_icon = tk.Label(library_header, image=library_icon_img, bg="#1f2323", bd=0, highlightthickness=0)
library_icon.pack(side="left", padx=(0, 5))
library_label = tk.Label(library_header, text="Library", fg="#ffffff", bg="#1f2323", font=fonts["menus_font"])
library_label.pack(side="left", anchor="w")
library_canvas = tk.Canvas(main, bg="#1f2323", bd=0, highlightthickness=0)
library_canvas.pack(side="top", fill="x", expand=False)
albums_frame = tk.Frame(library_canvas, bg="#1f2323")
library_canvas.create_window((0, 0), window=albums_frame, anchor="nw")

def on_mousewheel(event):
    if lyric_is_open:
        return
    widget = event.widget
    if widget.winfo_class() in ("Text", "Scrollbar"):
        return
    if sys.platform.startswith(("win", "linux")):
        library_canvas.xview_scroll(-1 * int(event.delta / 120), "units")
    else:
        library_canvas.xview_scroll(-1 * int(event.delta), "units")

main.bind_all("<MouseWheel>", on_mousewheel)

def update_scrollregion(event=None):
    library_canvas.configure(scrollregion=library_canvas.bbox("all"))

albums_frame.bind("<Configure>", update_scrollregion)

#::::: Search :::::
search_var = tk.StringVar()
search_frame = tk.Frame(library_header, bg="#2b3030")
search_frame.pack(side="right", padx=5, pady=5)
search_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/search.png").resize((24, 24)))
search_icon = tk.Label(search_frame, image=search_icon_img, bg="#2b3030", bd=0, highlightthickness=0)
search_icon.pack(side="left", padx=3)
search_entry = tk.Entry(search_frame, textvariable=search_var, font=fonts["title_font"], bg="#2b3030",
                        fg="white", insertbackground="white", relief="flat", bd=0, highlightthickness=0, width=25)
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

#::::: Functions :::::

root.mainloop()

# try:
#     root.mainloop()
# except KeyboardInterrupt:
#     sys.exit()
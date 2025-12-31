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
    from PIL import Image, ImageTk
except ImportError:
    os.system("pip install -r requirements.txt")

#::::: Default Library :::::
import tkinter as tk
import pygame
import os

#::::: Fonts :::::
from font.font import create_fonts

#::::: Src :::::
from src.header import header

#::::: Window :::::
root = tk.Tk()
w, h = 1230, 500
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

# ---------- MAIN ----------
main = tk.Frame(root, bg="#1f2323")
main.pack(fill="both", expand=True)
content = tk.Frame(main, bg="#1f2323")
content.pack(fill="both", expand=True, padx=30, pady=20)

# ---------- LIBRARY HEADER ----------
library_header = tk.Frame(content, bg="#1f2323")
library_header.pack(fill="x", pady=5)
library_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/library.png").resize((24, 24)))
heart_empty_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/heart_empty.png").resize((24, 24)))
library_icon = tk.Label(library_header, image=library_icon_img, bg="#1f2323", bd=0, highlightthickness=0)
library_icon.pack(side="left", padx=(0, 5))
library_label = tk.Label(library_header, text="Library", fg="#ffffff", bg="#1f2323", font=fonts["menus_font"])
library_label.pack(side="left", anchor="w")

# ---------- SEARCH ----------
search_var = tk.StringVar()
search_frame = tk.Frame(library_header, bg="#2b3030")
search_frame.pack(side="right", padx=5, pady=5)
search_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/search.png").resize((24, 24)))
search_icon = tk.Label(search_frame, image=search_icon_img, bg="#2b3030", bd=0, highlightthickness=0)
search_icon.pack(side="left", padx=3)
search_entry = tk.Entry(search_frame, textvariable=search_var, font=fonts["title_font"], bg="#2b3030", fg="white", insertbackground="white", relief="flat", bd=0, highlightthickness=0, width=25)
search_entry.pack(side="left")
placeholder_text = "Search song or artist..."

# ---------- PLAYER ----------
player_frame = tk.Frame(root, bg="#f80000", height=160)
player_frame.pack(fill="x", side="bottom")
info_frame = tk.Frame(player_frame, bg="#6f00ff")
info_frame.pack(side="left", padx=10)
cover_label = tk.Label(info_frame, bg="#5eff00")
cover_label.pack(side="left", padx=(0,10))

root.mainloop()

# try:
#     root.mainloop()
# except KeyboardInterrupt:
#     sys.exit()
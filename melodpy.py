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

#::::: Main :::::
main = tk.Frame(root, bg="#1f2323")
main.pack(fill="both", expand=True, padx=10, pady=10)
content = tk.Frame(root, bg="#1f2323")
content.pack(fill="both", expand=True, padx=10, pady=10)



root.mainloop()

# try:
#     root.mainloop()
# except KeyboardInterrupt:
#     sys.exit()
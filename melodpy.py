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

#::::: Default Library :::::
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font as tkfont
import os

#::::: Libraries to be installed :::::
try:
    from PIL import Image, ImageTk
except ImportError:
    os.system("pip install -r requirements.txt")


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
from tkinter import messagebox, filedialog
import os
import io
import contextlib
import subprocess
import sys
import json
import socket
import webbrowser

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
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

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
repeat_states = ["off", "one", "shuffle"]
repeat_state = "off"
original_title_text = ""
original_artist_text = ""
scroll_title_pos = 0
scroll_artist_pos = 0
is_muted = False
prev_volume = 70

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

def get_genius_client():
    if not is_connected():
        popup("You are not connected to the internet.\nPlease check your connection.", title="No Internet Connection")
        return None

    if not os.path.exists("token.txt"):
        popup("token.txt file not found.\nLyrics feature is disabled.", title="Missing Token")
        return None

    try:
        with open("token.txt", "r", encoding="utf-8") as f:
            token = f.read().strip()
    except Exception as e:
        popup(f"Failed to read token.txt:\n{e}", title="Token Error")
        return None

    if not token:
        popup("token.txt file is empty.\nPlease put your Genius API token inside it.", title="Invalid Token")
        return None

    try:
        return Genius(token, timeout=10, retries=1, remove_section_headers=True)
    except Exception as e:
        popup(f"Failed to initialize Genius:\n{e}", title="Genius Error")
        return None

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

#::::: Player :::::
def get_song_info(mp3_path):
    audio = MP3(mp3_path, ID3=ID3)
    title = audio.tags.get("TIT2")
    artist = audio.tags.get("TPE1")
    cover_data = None
    for tag in audio.tags.keys():
        if tag.startswith("APIC"):
            cover_data = audio.tags[tag].data
            break
    title = title.text[0] if title else os.path.basename(mp3_path)
    artist = artist.text[0] if artist else "Unknown"
    length = audio.info.length
    return title, artist, cover_data, length

def play_song_by_path(mp3_path):
    if mp3_path in active_playlist:
        global current_playlist_index
        current_playlist_index = active_playlist.index(mp3_path)
        song_index = song_files.index(mp3_path)
        play_song(song_index)

def highlight_current_card():
    for card, mp3, idx in card_widgets:
        bg_color = "#3a3f3f" if idx == current_index else "#2b3030"
        card.config(bg=bg_color)
        for child in card.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=bg_color)

def play_song(index_in_song_files, start_pos=0):
    global current_index, offset_sec, paused, is_playing, current_playlist_index
    current_index = index_in_song_files
    offset_sec = start_pos
    paused = False
    is_playing = True
    song_path = song_files[current_index]
    with open(os.devnull, "w"), contextlib.redirect_stderr(None):
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(start=start_pos)
    update_song_ui()
    highlight_current_card()
    play_pause_btn.config(image=pause_icon)
    if song_path in active_playlist:
        current_playlist_index = active_playlist.index(song_path)
    progress_slider.set(offset_sec)
    elapsed_time_label.config(text=f"{int(offset_sec//60)}:{int(offset_sec%60):02d}")

def toggle_play_pause():
    global is_playing, paused
    if not song_files:
        return
    if not is_playing and not paused:
        play_song(0)
        return

    if is_playing:
        pygame.mixer.music.pause()
        paused = True
        is_playing = False
        play_pause_btn.config(image=play_icon)
    else:
        if paused:
            pygame.mixer.music.unpause()
        else:
            play_from_position(offset_sec)
        paused = False
        is_playing = True
        play_pause_btn.config(image=pause_icon)
    highlight_current_card()

def toggle_repeat():
    global repeat_state
    idx = repeat_states.index(repeat_state)
    repeat_state = repeat_states[(idx + 1) % len(repeat_states)]
    if repeat_state == "off":
        loop_btn.config(image=loop_icon_off)
    elif repeat_state == "one":
        loop_btn.config(image=loop_icon_on)
    elif repeat_state == "shuffle":
        loop_btn.config(image=shuffle_icon)

def next_song():
    global current_playlist_index
    if not active_playlist:
        return
    
    if repeat_state == "one":
        song_path = active_playlist[current_playlist_index]
        play_song(song_files.index(song_path))
    elif repeat_state == "shuffle":
        import random
        remaining_songs = [song for song in active_playlist if song != active_playlist[current_playlist_index]]
        if remaining_songs:
            song_path = random.choice(remaining_songs)
            current_playlist_index = active_playlist.index(song_path)
        else:
            song_path = active_playlist[current_playlist_index]
        play_song(song_files.index(song_path))
    else:
        current_playlist_index = (current_playlist_index + 1) % len(active_playlist)
        song_path = active_playlist[current_playlist_index]
        play_song(song_files.index(song_path))

def prev_song():
    global current_playlist_index
    if not active_playlist:
        return
    current_playlist_index = (current_playlist_index - 1) % len(active_playlist)
    song_path = active_playlist[current_playlist_index]
    play_song(song_files.index(song_path))

def get_current_time_sec():
    pos = pygame.mixer.music.get_pos()
    if pos < 0:
        pos = 0
    return offset_sec + (pos / 1000)

def seek_forward_10():
    if not song_files:
        return
    new_pos = min(get_current_time_sec() + 10, progress_slider.cget("to"))
    play_from_position(new_pos)

def seek_backward_10():
    if not song_files:
        return
    new_pos = max(get_current_time_sec() - 10, 0)
    play_from_position(new_pos)

def filter_songs(*args):
    query = search_var.get().lower().strip()

    if query == placeholder_text.lower():
        query = ""
        root.focus()

    for card, mp3_path, idx in card_widgets:
        card.pack_forget()

    for card, mp3_path, idx in sorted(card_widgets, key=lambda x: x[2]):
        data = search_cache.get(mp3_path)
        if not data:
            continue

        if query in data["title"] or query in data["artist"]:
            card.pack(side="left", padx=10)

    update_scrollregion()
search_var.trace_add("write", filter_songs)

player_frame = tk.Frame(root, bg="#262b2b", height=160)
player_frame.pack(fill="x", side="bottom")
info_frame = tk.Frame(player_frame, bg="#262b2b")
info_frame.pack(side="left", padx=10)
cover_label = tk.Label(info_frame, bg="#262b2b")
cover_label.pack(side="left", padx=(0,10))
song_title = tk.Label(info_frame, text="", fg="white", bg="#262b2b",font=fonts["title_font"], width=20, anchor="w")
song_title.pack(anchor="w", pady=10)
song_artist = tk.Label(info_frame, text="", fg="#a0a0a0", bg="#262b2b",font=fonts["artist_font"], width=20, anchor="w")
song_artist.pack(anchor="w")

def set_song_title(title):
    global original_title_text, scroll_title_pos
    original_title_text = title + "   "
    scroll_title_pos = 0
    song_title.config(text=original_title_text[:20])

def set_song_artist(artist):
    global original_artist_text, scroll_artist_pos
    original_artist_text = artist + "   "
    scroll_artist_pos = 0
    song_artist.config(text=original_artist_text[:20])

def scroll_texts():
    global scroll_title_pos, scroll_artist_pos
    if is_playing:
        if len(original_title_text) > 20:
            scroll_title_pos = (scroll_title_pos + 1) % len(original_title_text)
            display_title = original_title_text[scroll_title_pos:] + original_title_text[:scroll_title_pos]
            song_title.config(text=display_title[:20])
        if len(original_artist_text) > 20:
            scroll_artist_pos = (scroll_artist_pos + 1) % len(original_artist_text)
            display_artist = original_artist_text[scroll_artist_pos:] + original_artist_text[:scroll_artist_pos]
            song_artist.config(text=display_artist[:20])
    root.after(300, scroll_texts)
scroll_texts()

def update_song_ui():
    title, artist, cover_data, length = get_song_info(song_files[current_index])
    set_song_title(title)
    set_song_artist(artist)
    total_time_label.config(text=f"{int(length//60)}:{int(length%60):02d}")
    progress_slider.config(to=length)
    if cover_data:
        cover_img = Image.open(io.BytesIO(cover_data))
    else:
        cover_img = Image.new("RGB", (60, 60), color="#444")
    cover_img = cover_img.resize((60, 60))
    img = ImageTk.PhotoImage(cover_img)

    cover_label.config(image=img)
    cover_label.image = img

progress_frame = tk.Frame(player_frame, bg="#262b2b")
progress_frame.pack(side="top", fill="x", pady=5)
elapsed_time_label = tk.Label(progress_frame, text="0:00", fg="white", bg="#262b2b", font=fonts["title_font"])
elapsed_time_label.pack(side="left", padx=15)
progress_var = tk.DoubleVar()
progress_slider = tk.Scale(progress_frame, variable=progress_var, from_=0, to=100, orient="horizontal", bg="#262b2b", troughcolor="#444",
                           highlightthickness=0, bd=0, length=500, showvalue=False,
                           sliderrelief="flat",command=lambda val: set_song_position(val))
progress_slider.pack(side="left", fill="x", expand=True)
total_time_label = tk.Label(progress_frame, text="0:00", fg="white", bg="#262b2b", font=fonts["title_font"])
total_time_label.pack(side="right", padx=15)

def update_progress():
    global offset_sec, is_playing, paused
    if pygame.mixer.music.get_busy():
        pos_sec = pygame.mixer.music.get_pos() / 1000 + offset_sec
        progress_var.set(pos_sec)
        elapsed_time_label.config(text=f"{int(pos_sec//60)}:{int(pos_sec%60):02d}")
    else:
        if is_playing and not paused:
            next_song()
            offset_sec = 0
    root.after(200, update_progress)

progress_slider.bind(
    "<Button-1>",
    lambda e: (
        progress_slider.set(
            (e.x / progress_slider.winfo_width()) * progress_slider.cget("to")
        ),
        play_from_position(progress_slider.get()),
        "break"
    )
)

def play_from_position(seconds):
    global offset_sec, paused, is_playing

    offset_sec = seconds
    pygame.mixer.music.stop()
    pygame.mixer.music.play()
    pygame.mixer.music.set_pos(offset_sec)

    paused = False
    is_playing = True
    play_pause_btn.config(image=pause_icon)

def set_song_position(val):
    try:
        play_from_position(float(val))
    except:
        pass
def choose_folder():
    global songs_folder, song_files, card_widgets, search_cache, active_playlist, current_playlist_index, current_index
    folder = filedialog.askdirectory()
    if not folder:
        return
    if folder:
        songs_folder = folder
        song_files = [os.path.join(songs_folder, f) for f in os.listdir(songs_folder) if f.endswith(".mp3")]
        song_files.sort()
        active_playlist = song_files.copy()
        current_playlist_index = 0
        current_index = 0
        for card, mp3, idx in card_widgets:
            card.destroy()
        card_widgets.clear()
        search_cache.clear()
        for i, mp3 in enumerate(song_files):
            album_card(albums_frame, mp3, i)
        update_scrollregion()
        load_favorites()
    if song_files:
        play_song(0)

#::::: Icons :::::
play_icon = ImageTk.PhotoImage(Image.open("assets/icons/play.png").resize((30,30)))
pause_icon = ImageTk.PhotoImage(Image.open("assets/icons/pause.png").resize((30,30)))
next_icon = ImageTk.PhotoImage(Image.open("assets/icons/next.png").resize((30,30)))
prev_icon = ImageTk.PhotoImage(Image.open("assets/icons/prev.png").resize((30,30)))
loop_icon_off = ImageTk.PhotoImage(Image.open("assets/icons/loop_off.png").resize((30,30)))
loop_icon_on  = ImageTk.PhotoImage(Image.open("assets/icons/loop_on.png").resize((30,30)))
shuffle_icon  = ImageTk.PhotoImage(Image.open("assets/icons/shuffle.png").resize((30,30)))
seek_back_icon = ImageTk.PhotoImage(Image.open("assets/icons/seek_back.png").resize((30,30)))
seek_forward_icon = ImageTk.PhotoImage(Image.open("assets/icons/seek_forward.png").resize((30,30)))
folder_btn_icon = ImageTk.PhotoImage(Image.open("assets/icons/folder.png").resize((30,30)))
volume_mute_icon = ImageTk.PhotoImage(Image.open("assets/icons/volume_mute.png").resize((20,20)))
volume_low_icon = ImageTk.PhotoImage(Image.open("assets/icons/volume_low.png").resize((20,20)))
volume_medium_icon = ImageTk.PhotoImage(Image.open("assets/icons/volume_medium.png").resize((20,20)))
volume_high_icon = ImageTk.PhotoImage(Image.open("assets/icons/volume_high.png").resize((20,20)))

controls = tk.Frame(player_frame, bg="#262b2b")
controls.pack(side="top", pady=5, fill="x")
prev_btn = tk.Button(controls, image=prev_icon, bg="#262b2b", fg="white", bd=0, highlightthickness=0, relief="flat", command=prev_song)
prev_btn.pack(side="left", padx=5)
seek_back_btn = tk.Button(controls, image=seek_back_icon, bg="#262b2b", bd=0,highlightthickness=0, relief="flat", command=seek_backward_10)
seek_back_btn.pack(side="left", padx=5)
play_pause_btn = tk.Button(controls, image=play_icon, bg="#262b2b", fg="white", bd=0, highlightthickness=0, relief="flat", command=toggle_play_pause)
play_pause_btn.pack(side="left", padx=5)
seek_forward_btn = tk.Button(controls, image=seek_forward_icon, bg="#262b2b", bd=0, highlightthickness=0, relief="flat", command=seek_forward_10)
seek_forward_btn.pack(side="left", padx=5)
next_btn = tk.Button(controls, image=next_icon, bg="#262b2b", fg="white", bd=0, highlightthickness=0, relief="flat", command=next_song)
next_btn.pack(side="left", padx=5)
loop_btn = tk.Button(controls, image=loop_icon_off, bg="#262b2b", fg="white", bd=0, highlightthickness=0, relief="flat", command=toggle_repeat)
loop_btn.pack(side="left", padx=5)
folder_btn = tk.Button(controls, image=folder_btn_icon, bg="#262b2b", bd=0, highlightthickness=0, relief="flat", command=choose_folder)
folder_btn.pack(side="left", padx=5)
volume_frame = tk.Frame(controls, bg="#262b2b")
volume_frame.pack(side="right", padx=10,)
volume_icon = tk.Label(volume_frame, image=volume_medium_icon, bg="#262b2b", bd=0, highlightthickness=0)
volume_icon.pack(side="left", padx=(0,5))

def update_volume_icon(val=None):
    global is_muted
    vol = int(volume_slider.get())
    if is_muted or vol == 0:
        volume_icon.config(image=volume_mute_icon)
    elif vol < 40:
        volume_icon.config(image=volume_low_icon)
    elif vol < 80:
        volume_icon.config(image=volume_medium_icon)
    else:
        volume_icon.config(image=volume_high_icon)

def toggle_mute(event=None):
    global is_muted, prev_volume
    if not is_muted:
        prev_volume = volume_slider.get()
        volume_slider.set(0)
        pygame.mixer.music.set_volume(0)
        is_muted = True
    else:
        volume_slider.set(prev_volume)
        pygame.mixer.music.set_volume(prev_volume/100)
        is_muted = False
    update_volume_icon()

volume_icon.bind("<Button-1>", toggle_mute)

volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient="horizontal", bg="#262b2b", troughcolor="#444", highlightthickness=0, bd=0, length=120, showvalue=False, sliderrelief="flat", command=lambda v: set_volume(v))
volume_slider.set(70)
volume_slider.pack(side="left")
volume_value = tk.Label(volume_frame, text="70%", fg="white", bg="#262b2b", font=fonts["title_font"], width=4, anchor="e")
volume_value.pack(side="right", padx=5)

def set_volume(val):
    global is_muted
    vol = int(float(val))
    pygame.mixer.music.set_volume(vol/100)
    volume_value.config(text=f"{vol}%")
    if vol > 0:
        is_muted = False
    update_volume_icon()

volume_slider.bind(
    "<Button-1>",
    lambda e: (
        volume_slider.set(
            min(100, volume_slider.get() + 4)
            if e.x > volume_slider.winfo_width() / 2
            else max(0, volume_slider.get() - 4)
        ),
        set_volume(volume_slider.get())
    )
)

def delete_song(card, path):
    global song_files, active_playlist, current_playlist_index, current_index
    card.destroy()
    if path in song_files:
        removed_index = song_files.index(path)
        song_files.remove(path)
        if current_index >= len(song_files):
            current_index = max(0, len(song_files) - 1)
        elif removed_index < current_index:
            current_index -= 1
    if path in active_playlist:
        removed_playlist_index = active_playlist.index(path)
        active_playlist.remove(path)
        if current_playlist_index >= len(active_playlist):
            current_playlist_index = 0
        elif removed_playlist_index < current_playlist_index:
            current_playlist_index -= 1
    global card_widgets
    card_widgets = [
        (c, mp3, idx)
        for c, mp3, idx in card_widgets
        if mp3 != path
    ]
    update_scrollregion()
    save_favorites()

def edit_metadata(card, path):
    if path == song_files[current_index]:
        popup("Unable to edit the song's metadata.\nCannot edit the metadata of the selected song.", title="Cannot Edit")
        return

    audio = MP3(path, ID3=ID3)

    def get_tag_text(tag_name):
        tag = audio.tags.get(tag_name)
        return tag.text[0] if tag else ""

    audio = MP3(path, ID3=ID3)
    title = get_tag_text("TIT2")
    artist = get_tag_text("TPE1")
    album = get_tag_text("TALB")
    genre = get_tag_text("TCON")
    date = str(get_tag_text("TDRC"))
    track = get_tag_text("TRCK")
    comment = get_tag_text("COMM")
    composer = get_tag_text("TCOM")
    album_artist = get_tag_text("TPE2")

    cover_data = None
    for tag in audio.tags.keys():
        if tag.startswith("APIC"):
            cover_data = audio.tags[tag].data
            break

    win = tk.Toplevel(root)
    win.title("Edit Metadata")
    win.configure(bg="#262b2b", highlightbackground="black", highlightthickness=2)
    win.geometry("500x650")
    win.resizable(0, 0)
    win.transient(root)
    win.grab_set()
    win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (500 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (650 // 2)
    win.geometry(f"+{x}+{y}")

    cover_label = tk.Label(win, bg="#262b2b")
    cover_label.pack(pady=20)
    if cover_data:
        img = Image.open(io.BytesIO(cover_data)).resize((50,50))
    else:
        img = Image.new("RGB", (50,50), color="#444")
    cover_photo = ImageTk.PhotoImage(img)
    cover_label.config(image=cover_photo)
    cover_label.image = cover_photo
    def change_cover():
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            img = Image.open(file_path).resize((50,50))
            cover_photo = ImageTk.PhotoImage(img)
            cover_label.config(image=cover_photo)
            cover_label.image = cover_photo
            cover_label.new_cover_path = file_path
    cover_label.bind("<Button-1>", lambda e: change_cover())

    labels = ["Title", "Artist", "Album", "Genre", "Date", "Track", "Comment", "Composer", "Album Artist"]
    vars_ = [tk.StringVar(value=x) for x in [title, artist, album, genre, date, track, comment, composer, album_artist]]

    for i, (label_text, var) in enumerate(zip(labels, vars_)):
        row_frame = tk.Frame(win, bg="#262b2b")
        row_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(row_frame, text=f"{label_text}", fg="white", bg="#262b2b", font=fonts["title_font"], anchor="w").pack(side="top", anchor="w")
        tk.Entry(row_frame, textvariable=var, width=30, font=fonts["message"], bg="#2b3030", fg="white", insertbackground="white", bd=0, highlightthickness=0).pack(side="top", fill="x", expand=True, pady=2)

    btn_frame = tk.Frame(win, bg="#262b2b")
    btn_frame.pack(pady=20)

    def save_changes():
            tag_names = ["TIT2","TPE1","TALB","TCON","TDRC","TRCK","COMM","TCOM","TPE2"]
            for tname, var in zip(tag_names, vars_):
                if tname == "COMM":
                    audio.tags.add(mutagen.id3.COMM(encoding=3, lang="eng", text=var.get()))
                else:
                    audio.tags.add(getattr(mutagen.id3, tname)(encoding=3, text=var.get()))
                if hasattr(cover_label, "new_cover_path"):
                    audio.tags.delall("APIC")
                    with open(cover_label.new_cover_path, "rb") as f:
                        audio.tags.add(mutagen.id3.APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=f.read()))
                if hasattr(cover_label, "new_cover_path"):
                    new_cover_img = Image.open(cover_label.new_cover_path).resize((60, 60))
                    new_cover_photo = ImageTk.PhotoImage(new_cover_img)
                    cover_label_main = globals()['cover_label']
                    cover_label_main.config(image=new_cover_photo)
                    cover_label_main.image = new_cover_photo
                    card_widgets_dict = {mp3: c for c, mp3, idx in card_widgets}
                    current_card = card_widgets_dict[path]
                    new_card_cover_img = Image.open(cover_label.new_cover_path).resize((160, 140))
                    new_card_photo = ImageTk.PhotoImage(new_card_cover_img)
                    card_cover_label = current_card.winfo_children()[0]
                    card_cover_label.config(image=new_card_photo)
                    card_cover_label.image = new_card_photo
            audio.save()

            card_widgets_dict = {mp3: c for c, mp3, idx in card_widgets}
            current_card = card_widgets_dict[path]
            display_title = vars_[0].get() if len(vars_[0].get()) <= 20 else vars_[0].get()[:17] + "..."
            display_artist = vars_[1].get() if len(vars_[1].get()) <= 20 else vars_[1].get()[:17] + "..."
            current_card.winfo_children()[1].config(text=display_title)
            current_card.winfo_children()[2].config(text=display_artist)

            if path == song_files[current_index]:
                update_song_ui()
                highlight_current_card()
            search_cache[path] = {
                    "title": vars_[0].get().lower(),
                    "artist": vars_[1].get().lower()
            }
            win.destroy()

    tk.Button(btn_frame, text="Save", bg="#3a3f3f", fg="white", font=fonts["button_font"], width=12, height=2, bd=0, relief="flat", highlightthickness=0, command=save_changes).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", bg="#3a3f3f", fg="white", font=fonts["button_font"], width=12, height=2, bd=0, relief="flat", highlightthickness=0, command=win.destroy).pack(side="left", padx=10)

def open_location(path):
    try:
        if sys.platform == "win32":
            os.startfile(os.path.dirname(path))
        elif sys.platform == "darwin":
            subprocess.run(["open", os.path.dirname(path)])
        else:
            subprocess.run(["xdg-open", os.path.dirname(path)])
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open folder: {e}")

def show_menu(event, card, mp3_path):
    def delayed_popup():
        menu = tk.Menu(root, tearoff=0, bg="#2b3030", fg="white", font=fonts["message"], bd=0, relief="flat")

        def confirm_delete():
            if mp3_path == song_files[current_index]:
                popup("Cannot delete the song currently playing.",title="Cannot delete", height=120)
            else:
                confirm_win = tk.Toplevel(root)
                confirm_win.configure(bg="#262b2b")
                confirm_win.title("Confirm Delete")
                confirm_win.geometry("400x120")
                confirm_win.resizable(0, 0)
                confirm_win.overrideredirect(True)
                confirm_win.grab_set()
                confirm_win.update_idletasks()
                root_x = root.winfo_x()
                root_y = root.winfo_y()
                root_width = root.winfo_width()
                root_height = root.winfo_height()
                width = 400
                height = 120
                x = root_x + (root_width // 2) - (width // 2)
                y = root_y + (root_height // 2) - (height // 2)
                confirm_win.geometry(f"{width}x{height}+{x}+{y}")
                frame = tk.Frame(confirm_win, bg="#262b2b")
                frame.pack(expand=True, fill="both")
                tk.Label(frame, text="Confirm Delete", fg="white", bg="#262b2b", font=fonts["info_title"]).pack(pady=(15, 5))
                tk.Label(frame, text="Are you sure you want to delete this song?", fg="white", bg="#262b2b", font=fonts["message"]).pack(pady=(0, 10))
                btn_frame = tk.Frame(frame, bg="#262b2b")
                btn_frame.pack()

                def yes_action():
                    try:
                        os.remove(mp3_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not delete file: {e}")
                    delete_song(card, mp3_path)
                    confirm_win.destroy()

                tk.Button(btn_frame, text="Yes", command=yes_action,
                          bg="#3a3f3f", fg="white", font=fonts["button_font"], bd=0, relief="flat", highlightthickness=0 ,width=12, height=2).pack(side="left", padx=10)
                tk.Button(btn_frame, text="No", command=confirm_win.destroy,
                          bg="#3a3f3f", fg="white", font=fonts["button_font"], bd=0, relief="flat", highlightthickness=0 ,width=12, height=2).pack(side="right", padx=10)

        delete_icon = ImageTk.PhotoImage(Image.open("assets/icons/delete.png").resize((20,20)))
        edit_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/edit.png").resize((20,20)))
        lyrics_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/lyrics.png").resize((20,20)))
        open_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/folder.png").resize((20,20)))
        props_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/properties.png").resize((20,20)))
        menu.add_command(label=" Delete Song", image=delete_icon, compound="left", command=confirm_delete)
        menu.add_command(label=" Edit Metadata", image=edit_icon_img, compound="left", command=lambda: edit_metadata(card, mp3_path))
        menu.add_command(label=" Song Lyric", image=lyrics_icon_img, compound="left", command=lambda: fetch_and_show_lyrics(mp3_path))
        menu.add_command(label=" Open Location", image=open_icon_img, compound="left",command=lambda: open_location(mp3_path))
        menu.add_command(label=" Properties", image=props_icon_img, compound="left", command=lambda: show_properties(mp3_path))
        menu.delete_icon = delete_icon
        menu.edit_icon_img = edit_icon_img
        menu.lyrics_icon_img = lyrics_icon_img
        menu.open_icon_img = open_icon_img
        menu.props_icon_img = props_icon_img
        menu.tk_popup(event.x_root, event.y_root)
    root.after(200, delayed_popup)

def fetch_and_show_lyrics(mp3_path):
    if mp3_path != song_files[current_index]:
        popup("You can only see the lyrics of the song\n that's playing right now.",title="Lyrics")
        return
    genius = get_genius_client()
    if not genius:
        return
    title, artist, _, _ = get_song_info(mp3_path)
    try:
        song = genius.search_song(title, artist)
    except Exception as e:
        popup(f"Failed to fetch lyrics from Genius.\nPlease check the token.", title="Lyrics Error")
        return
    if not song or not song.lyrics:
        popup("Lyrics were not found.\nCheck the song metadata.", title="Lyrics Not Found")
        return
    lyrics_text = regex.sub(r'[^\p{L}\p{N}\s:.]', '', song.lyrics)

    def process_multilang_text(text):
        if any('\u0590' <= c <= '\u06FF' for c in text):
            reshaped_text = arabic_reshaper.reshape(text)
            final_text = get_display(reshaped_text)
            align = "right"
        else:
            final_text = text
            align = "left"
        return final_text, align

    global lyric_is_open
    lyric_is_open = True

    def close_lyrics():
        global lyric_is_open
        lyric_is_open = False
        win.destroy()

    processed_text, align = process_multilang_text(lyrics_text)

    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.configure(bg="#262b2b")
    win.grab_set()

    frame = tk.Frame(win, bg="#262b2b")
    frame.pack(expand=True, fill="both")

    text_widget = tk.Text(frame, bg="#262b2b", fg="white", font=fonts["title_font"], wrap="word",
                          bd=0, highlightthickness=0)
    text_widget.insert("1.0", processed_text)
    text_widget.tag_configure("align", justify="center", spacing1=4, spacing3=4)
    text_widget.tag_add("align", "1.0", "end")
    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both", padx=10, pady=(10,0))

    close_btn = tk.Button(frame, text="Close", font=fonts["button_font"], bg="#3a3f3f", fg="white", bd=0,
        relief="flat",highlightthickness=0, width=12,height=2,command=close_lyrics)
    close_btn.pack(side="bottom",pady=(0, 15))

    win.update_idletasks()
    width = text_widget.winfo_reqwidth() + 20
    height = text_widget.winfo_reqheight() + close_btn.winfo_reqheight() + 30
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    def start_move(event):
        win.x = event.x
        win.y = event.y

    def do_move(event):
        x = win.winfo_x() + (event.x - win.x)
        y = win.winfo_y() + (event.y - win.y)
        win.geometry(f"+{x}+{y}")

    frame.bind("<Button-1>", start_move)
    frame.bind("<B1-Motion>", do_move)
    
    lyrics_song_index = current_index
    def check_lyrics_window():
        global lyric_is_open
        if current_index != lyrics_song_index:
            try:
                lyric_is_open = False
                win.destroy()
            except:
                pass
        else:
            win.after(500, check_lyrics_window)
    check_lyrics_window()

def show_properties(mp3_path):
    audio = MP3(mp3_path, ID3=ID3)

    title_tag = audio.tags.get("TIT2")
    artist_tag = audio.tags.get("TPE1")
    album_tag = audio.tags.get("TALB")
    genre_tag = audio.tags.get("TCON")
    date_tag = audio.tags.get("TDRC")
    track_tag = audio.tags.get("TRCK")
    comment_tag = audio.tags.get("COMM")
    composer_tag = audio.tags.get("TCOM")
    album_artist_tag = audio.tags.get("TPE2")
    size_bytes = os.path.getsize(mp3_path)

    title = title_tag.text[0] if title_tag else os.path.basename(mp3_path)
    artist = artist_tag.text[0] if artist_tag else "Unknown"
    album = album_tag.text[0] if album_tag else "Unknown"
    genre = genre_tag.text[0] if genre_tag else "Unknown"
    recording_date = str(date_tag.text[0]) if date_tag else "Unknown"
    track = track_tag.text[0] if track_tag else "Unknown"
    comment = comment_tag.text[0] if comment_tag else "Unknown"
    composer = composer_tag.text[0] if composer_tag else "Unknown"
    album_artist = album_artist_tag.text[0] if album_artist_tag else "Unknown"
    size_mb = f"{size_bytes / (1024*1024):.2f} MB"
    
    props_win = tk.Toplevel(root)
    props_win.configure(bg="#262b2b")
    props_win.title("Properties")
    props_win.resizable(0, 0)
    props_win.overrideredirect(True)
    props_win.grab_set()

    labels = [
        ("Title", title),
        ("Artist", artist),
        ("Album", album),
        ("Genre", genre),
        ("Date", recording_date),
        ("Track", track),
        ("Comment", comment),
        ("Composer", composer),
        ("Album Artist", album_artist),
        ("Size", size_mb)
    ]

    frame = tk.Frame(props_win, bg="#262b2b", bd=2)
    frame.pack(expand=True, fill="both")

    for i, (label, value) in enumerate(labels):
        row = tk.Frame(frame, bg="#262b2b")
        row.pack(fill="x", padx=10, pady=(5 if i == 0 else 2))
        tk.Label(row, text=f"{label}:", fg="white", bg="#262b2b", font=fonts["title_font"], anchor="w").pack(side="left")
        tk.Label(row, text=value, fg="white", bg="#262b2b", font=fonts["message"], anchor="w").pack(side="left", padx=(5,0))

    tk.Button(frame, text="Close", command=props_win.destroy, bg="#3a3f3f", fg="white",
              font=fonts["button_font"], width=12, height=2,bd=0, relief="flat",highlightthickness=0).pack(pady=10)

    props_win.update_idletasks()
    width = props_win.winfo_width()
    height = props_win.winfo_height()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    props_win.geometry(f"+{x}+{y}")
def album_card(parent, mp3_path, song_index):
    title, artist, cover_data, length = get_song_info(mp3_path)
    card = tk.Frame(parent, bg="#2b3030", width=180, height=240)
    card_widgets.append((card, mp3_path, song_index))
    
    card.is_favorite = False

    if cover_data:
        cover_img = Image.open(io.BytesIO(cover_data))
    else:
        cover_img = Image.new("RGB", (160, 140), color="#444")
    cover_img = cover_img.resize((160, 140))
    img = ImageTk.PhotoImage(cover_img)
    cover = tk.Label(card, image=img, bg="#2b3030", bd=0, highlightthickness=0)
    cover.image = img
    cover.pack(pady=10)

    max_chars = 20

    if len(title) > max_chars:
        display_title = title[:max_chars-3] + "..."
    else:
        display_title = title
    if len(artist) > max_chars:
        display_artist = artist[:max_chars-3] + "..."
    else:
        display_artist = artist

    tk.Label(card, text=display_title, fg="white", bg="#2b3030",
            font=fonts["title_font"], anchor="w").pack(fill="x", padx=10)
    tk.Label(card, text=display_artist, fg="#a0a0a0", bg="#2b3030",
            font=fonts["artist_font"], anchor="w").pack(fill="x", padx=10)

    total_time = f"{int(length//60)}:{int(length%60):02d}"
    time_label = tk.Label(card, text=total_time, fg="white", bg="#2b3030", font=fonts["artist_font"])
    time_label.place(x=10, y=card.winfo_reqheight()-25)

    heart_empty = ImageTk.PhotoImage(Image.open("assets/icons/heart_empty.png").resize((20,20)))
    heart_filled = ImageTk.PhotoImage(Image.open("assets/icons/heart_filled.png").resize((20,20)))
    card.heart_empty = heart_empty
    card.heart_filled = heart_filled
    heart_label = tk.Label(card, image=heart_empty, bg="#2b3030", bd=0)
    heart_label.pack(side="bottom", pady=5)
    card.heart_label = heart_label
    search_cache[mp3_path] = {
        "title": title.lower(),
        "artist": artist.lower()
    }
    def toggle_favorite(event=None):
        card.is_favorite = not card.is_favorite
        heart_label.config(image=heart_filled if card.is_favorite else heart_empty)
    
    heart_label.bind("<Button-1>", toggle_favorite)

    dots_icon_img = ImageTk.PhotoImage(Image.open("assets/icons/three_dots.png").resize((20,20)))
    three_dot_label = tk.Label(card, image=dots_icon_img, bg="#2b3030", bd=0)
    three_dot_label.image = dots_icon_img
    three_dot_label.place(x=card.winfo_reqwidth()-30, y=card.winfo_reqheight()-25)
    three_dot_label.bind("<Button-1>", lambda e: show_menu(e, card, mp3_path))

    card.bind("<Button-1>", lambda e, p=mp3_path: play_song_by_path(p))
    cover.bind("<Button-1>", lambda e, p=mp3_path: play_song_by_path(p))
    card.pack(side="left", padx=10)
    card.pack_propagate(False)

def show_all_songs():
    if not card_widgets:
        return

    global active_playlist, current_playlist_index
    active_playlist = [mp3 for c, mp3, idx in card_widgets]
    current_playlist_index = 0
    library_label.config(text="Library")
    library_icon.config(image=library_icon_img)

    for card, mp3, idx in card_widgets:
        card.pack_forget()
    for card, mp3, idx in sorted(card_widgets, key=lambda x: x[2]):
        card.pack(side="left", padx=10)
    update_scrollregion()

def show_favorites():
    global active_playlist, current_playlist_index
    if not card_widgets:
        return

    active_playlist = [
        mp3 for card, mp3, idx in card_widgets
        if getattr(card, "is_favorite", False)
    ]
    current_playlist_index = 0
    library_label.config(text="Favorites")
    library_icon.config(image=heart_empty_icon_img)

    for card, mp3, idx in card_widgets:
        card.pack_forget()
    for card, mp3, idx in sorted(card_widgets, key=lambda x: x[2]):
        if getattr(card, "is_favorite", False):
            card.pack(side="left", padx=10)
    update_scrollregion()

all_songs_icon = ImageTk.PhotoImage(Image.open("assets/icons/library.png").resize((20,20)))
favorites_icon = ImageTk.PhotoImage(Image.open("assets/icons/heart_empty.png").resize((20,20)))
library_menu = tk.Menu(root, tearoff=0, bg="#2b3030", fg="white",
                       font=fonts["header_font"], bd=0, relief="flat")
library_menu.add_command(label="Library", image=all_songs_icon, compound="left",
                         command=show_all_songs)
library_menu.add_command(label="Favorites", image=favorites_icon, compound="left",
                         command=show_favorites)
library_menu.all_songs_icon = all_songs_icon
library_menu.favorites_icon = favorites_icon

def library_click(event):
    def delayed_menu():
        library_menu.tk_popup(event.x_root, event.y_root)
    root.after(200, delayed_menu)

library_label.bind("<Button-1>", library_click)
library_icon.bind("<Button-1>", library_click)
for i, mp3 in enumerate(song_files):
    album_card(albums_frame, mp3, i)
load_favorites()

update_progress()
try:
    root.mainloop()
except KeyboardInterrupt:
    sys.exit()
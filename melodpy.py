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

#::::: Main :::::
main = tk.Frame(root, bg="#1f2323")
main.pack(fill="both", expand=True,pady=8)
content = tk.Frame(main, bg="#1f2323")
content.pack(fill="both", expand=True, padx=10, pady=10)
library_header = tk.Frame(content, bg="#1f2323")
library_header.pack(fill="x", pady=5)
library_icon_img = ImageTk.PhotoImage(Image.open("assets/assets/icons/library.png").resize((24, 24)))
heart_empty_icon_img = ImageTk.PhotoImage(Image.open("assets/assets/icons/heart_empty.png").resize((24, 24)))
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
search_icon_img = ImageTk.PhotoImage(Image.open("assets/assets/icons/search.png").resize((24, 24)))
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

def toggle_loop():
    global is_loop
    is_loop = not is_loop
    loop_btn.config(image=loop_icon_on if is_loop else loop_icon_off)

# ---------- ICONS ----------
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
play_pause_btn = tk.Button(controls, image=play_icon, bg="#262b2b", fg="white", bd=0, highlightthickness=0, relief="flat", command=toggle_play_pause)
play_pause_btn.pack(side="left", padx=5)
seek_back_btn = tk.Button(controls, image=seek_back_icon, bg="#262b2b", bd=0,highlightthickness=0, relief="flat", command=seek_backward_10)
seek_back_btn.pack(side="left", padx=5)
next_btn = tk.Button(controls, image=next_icon, bg="#262b2b", fg="white", bd=0, highlightthickness=0, relief="flat", command=next_song)
next_btn.pack(side="left", padx=5)
seek_forward_btn = tk.Button(controls, image=seek_forward_icon, bg="#262b2b", bd=0, highlightthickness=0, relief="flat", command=seek_forward_10)
seek_forward_btn.pack(side="left", padx=5)
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


root.mainloop()

# try:
#     root.mainloop()
# except KeyboardInterrupt:
#     sys.exit()
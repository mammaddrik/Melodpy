import tkinter as tk
from PIL import ImageTk
from audio.metadata import get_song_info
from core import state

def create_song_card(parent, mp3_path, index, play_callback):
    title, artist, cover, length = get_song_info(mp3_path)

    card = tk.Frame(parent, bg="#2b3030", width=180, height=240)
    state.card_widgets.append((card, mp3_path, index))

    if cover:
        cover = cover.resize((160, 140))
        img = ImageTk.PhotoImage(cover)
    else:
        img = None

    lbl = tk.Label(card, image=img, bg="#2b3030")
    lbl.image = img
    lbl.pack(pady=10)

    tk.Label(card, text=title, fg="white", bg="#2b3030").pack()
    tk.Label(card, text=artist, fg="#aaa", bg="#2b3030").pack()

    card.bind("<Button-1>", lambda e: play_callback(index))
    card.pack(side="left", padx=10)

    return card

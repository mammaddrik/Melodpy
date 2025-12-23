import tkinter as tk
import os
from ui.cards import create_song_card
from audio.player import play_song
from core import state

def create_library(root):
    frame = tk.Frame(root, bg="#1f2323")
    frame.pack(fill="both", expand=True)

    songs_dir = "songs"
    state.song_files = [
        os.path.join(songs_dir, f)
        for f in os.listdir(songs_dir)
        if f.endswith(".mp3")
    ]

    for i, mp3 in enumerate(state.song_files):
        create_song_card(frame, mp3, i, play_song)

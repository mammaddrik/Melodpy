import tkinter as tk
from audio.player import toggle_play_pause

def create_player(root):
    frame = tk.Frame(root, bg="#262b2b", height=140)
    frame.pack(side="bottom", fill="x")

    btn = tk.Button(frame, text="Play / Pause", command=toggle_play_pause)
    btn.pack(pady=20)

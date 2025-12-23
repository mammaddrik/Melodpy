import pygame
from core import state
from audio.metadata import get_song_info

def play_song(index, start=0):
    state.current_index = index
    state.offset_sec = start
    state.is_playing = True
    state.paused = False

    pygame.mixer.music.load(state.song_files[index])
    pygame.mixer.music.play(start=start)

def toggle_play_pause():
    if state.is_playing:
        pygame.mixer.music.pause()
        state.paused = True
        state.is_playing = False
    else:
        pygame.mixer.music.unpause()
        state.paused = False
        state.is_playing = True

import os
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image

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

    cover = Image.open(io.BytesIO(cover_data)) if cover_data else None
    return title, artist, cover, length

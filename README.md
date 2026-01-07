<div id="top"></div>
<p align="center">
    <a href="https://github.com/mammaddrik/Melodpy">
    <img src="https://i.postimg.cc/RFW74jn0/Melodpy.png" alt="Melodpy logo"></a>
</p>

# Melodpy
Melodpy is a lightweight desktop music player built with Python, Tkinter, and pygame.  
It focuses on simplicity, local music libraries, and a clean user experience.
<details>
<summary>Contents</summary>

[Features](#Features)<br>
[Installation](#installation)<br>
[Screenshots](#Screenshots)<br>
[License](#license)

</details>

<p align="center">
    <img src="https://i.postimg.cc/HxZLqPpf/musicplayer.png" alt="Music Player">
</p>

## Features
- 🎧 Play local MP3 files
- 📁 Load music from any folder
- ❤️ Favorite songs system
- 🔁 Repeat modes (One / Shuffle)
- 🔍 Search by song title or artist
- 🖼 Display album covers
- 📝 Edit MP3 metadata (title, artist, album, cover, etc.)
- 🎶 Fetch lyrics from Genius (optional)
- 🌍 Supports multilingual lyrics (LTR & RTL)

## Installation
### <img src="https://i.postimg.cc/nLp4jWx0/Windows.png" width="15" height="15" alt="Windows"/> Windows
> **Note:** Melodpy isn't compatible with python2, run it with python3 instead.<br>
```
git clone https://github.com/mammaddrik/Melodpy.git
cd Melodpy
python pip install -r requirements.txt
python Melodpy.py
```
Or you can use exe file on [releases](https://github.com/mammaddrik/Melodpy/releases)

### <img src="https://cdn.simpleicons.org/docker/2496ED" width="15" height="15" alt="docker"/> Docker
install docker on your system. [docker](https://www.docker.com/)
```
docker build -t Melodpy .
docker run -ti Melodpy
```
### <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/skills/linux-colored.svg" width="15" height="15" alt="Linux"/> Linux
> **Note:** Melodpy isn't compatible with python2, run it with python3 instead.<br>
```
git clone https://github.com/mammaddrik/Melodpy.git
cd Melodpy
python pip install -r requirements.txt
python Melodpy.py
```

### requirements
| **Requirements**  | **Command**  | **Link**  | **Version**  |
| ------------- | ------------- | ------------- | ------------- |
| pillow | `python pip install pillow`  | [pypi](https://pypi.org/project/pillow/)  | 12.1.0 |
| mutagen | `python pip install mutagen` | [pypi](https://pypi.org/project/mutagen/)  | 1.47.0 |
| pygame | `python pip install pygame`  | [pypi](https://pypi.org/project/pygame/)  | 2.6.1 |
| lyricsgenius | `python pip install lyricsgenius`  | [pypi](https://pypi.org/project/lyricsgenius/)  | 3.7.5 |
| arabic-reshaper | `python pip install arabic-reshaper`  | [pypi](https://pypi.org/project/arabic-reshaper/)  | 3.0.0 |
| python-bidi | `python pip install python-bidi`  | [pypi](https://pypi.org/project/python-bidi/)  | 0.6.7 |
> **Note:** You may encounter an error while installing this requirements. If an error occurs, use the following command.

```
python -m pip install --upgrade pip
python pip install -r requirements.txt
```

## Screenshots
<p align="center">
    <img src="https://i.postimg.cc/hPtdnFWR/lyrics.png" alt="lyrics">
    <img src="https://i.postimg.cc/4d1YCPW6/Favorite.png" alt="Favorite">
</p>

## License
Melodpy is licensed under [MIT License](https://github.com/mammaddrik/Melodpy/blob/main/LICENSE).

<p align="right"><a href="#top">back to top</a></p>

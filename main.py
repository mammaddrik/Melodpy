import tkinter as tk
from ui.header import create_header
from ui.library import create_library
from ui.player import create_player
from core.config import init_app

def main():
    root = tk.Tk()
    init_app(root)

    create_header(root)
    create_library(root)
    create_player(root)

    root.mainloop()

if __name__ == "__main__":
    main()

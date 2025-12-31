import tkinter as tk
import webbrowser
from src.internet import coonnected
from src.popup import show_popup

offset_x = 0
offset_y = 0

def start_move(event, root):
    global offset_x, offset_y
    offset_x = event.x_root - root.winfo_x()
    offset_y = event.y_root - root.winfo_y()

def stop_move(event, root):
    x = event.x_root - offset_x
    y = event.y_root - offset_y
    root.geometry(f"+{x}+{y}")

def open_link(root):
    if coonnected():
        webbrowser.open_new("https://github.com/mammaddrik")
    else:
        show_popup(root, "No Internet Connection!")

def header(root, fonts, title_text="Melodpy"):
    header = tk.Frame(root, bg="#1f2323", height=40)
    header.pack(fill="x", side="top")
    title = tk.Label(
        header,
        text=title_text,
        bg="#3a3f3f",
        fg="#ffffff",
        font=fonts["header_font"],
        padx=20,
        pady=6
    )
    title.place(relx=0.5, anchor="n")

    title.bind("<Double-Button-1>", lambda e: open_link(root))

    close_canvas = tk.Canvas(
        header,
        width=20,
        height=20,
        bg="#1f2323",
        highlightthickness=0
    )
    close_canvas.place(x=header.winfo_width() - 35, y=5)

    close_circle = close_canvas.create_oval(
        2, 2, 18, 18,
        fill="#ff5f56",
        outline="#e0443e"
    )

    close_canvas.tag_bind(
        close_circle,
        "<Button-1>",
        lambda e: root.destroy()
    )

    close_canvas.tag_bind(
        close_circle,
        "<Enter>",
        lambda e: close_canvas.itemconfig(close_circle, fill="#e0443e")
    )
    close_canvas.tag_bind(
        close_circle,
        "<Leave>",
        lambda e: close_canvas.itemconfig(close_circle, fill="#ff5f56")
    )

    def update_close_position(event):
        close_canvas.place(x=header.winfo_width() - 35, y=5)

    header.bind("<Configure>", update_close_position)

    header.bind("<Button-1>", lambda e: start_move(e, root))
    header.bind("<B1-Motion>", lambda e: stop_move(e, root))

    title.bind("<Button-1>", lambda e: start_move(e, root))
    title.bind("<B1-Motion>", lambda e: stop_move(e, root))

    return header
import tkinter as tk
from tkinter import ttk, END
from sqlalchemy import create_engine, text
import unicodedata

# --- DB CONNECTION ---
engine = create_engine(
    "mysql+pymysql://root:123@192.168.0.115/cddb?charset=utf8mb4",
    echo=False
)

# --- NORMALIZE TEXT ---
def normalize_text(s):
    return ''.join(
        '-' if 'HYPHEN' in unicodedata.name(c, '') else c
        for c in s.strip()
    )

# --- GET ALBUMS ---
def get_albums():
    query = text("""
        SELECT album_id, album_title
        FROM albums
        WHERE disc_id = 0
        ORDER BY album_title
    """)
    with engine.connect() as conn:
        result = conn.execute(query)
        return [f"{row.album_id:03d} | {row.album_title}" for row in result]

# --- CHECK ALBUM ---
def check_cdslot(disc_id):
    query = text("SELECT album_id, album_title, disc_id FROM albums WHERE disc_id = :disc_id")
    with engine.connect() as conn:
        result = conn.execute(query, {"disc_id": disc_id})
        return result.fetchall()

# --- UPDATE ---
def update_disc_id(album_id, new_disc_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT album_id, album_title FROM albums WHERE disc_id = :disc_id"),
            {"disc_id": new_disc_id}
        ).fetchone()

        duplicate_info = None

        if result:
            duplicate_info = result[1]
            conn.execute(
                text("UPDATE albums SET disc_id = 0 WHERE album_id = :album_id"),
                {"album_id": result[0]}
            )

        conn.execute(
            text("UPDATE albums SET disc_id = :disc_id WHERE album_id = :album_id"),
            {"disc_id": new_disc_id, "album_id": album_id}
        )

        conn.commit()
        return duplicate_info

# --- COLORS ---
AMBER = "#FFBF00"
BG = "#000000"
FIELD_BG = "#111111"

# --- ROOT ---
root = tk.Tk()
root.title("Pioneer CD Manager")
root.configure(bg=BG)

# --- STYLE ---
style = ttk.Style()
style.theme_use("default")

style.configure("TButton",
    background=AMBER,
    foreground="black",
    font=("Courier", 10),
    padding=5
)

style.map("TButton",
    background=[("active", "#e6ac00")]
)

style.configure("TEntry",
    fieldbackground=FIELD_BG,
    foreground=AMBER,
    insertcolor=AMBER
)

# --- TITLE ---
title = tk.Label(root,
    text="PIONEER CD MANAGER",
    font=("Courier", 18, "bold"),
    fg=AMBER, bg=BG
)
title.pack(pady=(10,5))

# --- LISTBOX FRAME ---
list_frame = tk.Frame(root, bg=BG)
list_frame.pack(padx=10, pady=5)

album_listbox = tk.Listbox(list_frame,
    width=70, height=10,
    bg=BG, fg=AMBER,
    selectbackground=AMBER,
    selectforeground="black",
    font=("Courier", 11),
    relief="flat",
    highlightthickness=1,
    highlightcolor=AMBER
)
album_listbox.pack()

# --- INPUT ROW ---
input_frame = tk.Frame(root, bg=BG)
input_frame.pack(pady=5)

tk.Label(input_frame, text="ALBUM:",
         fg=AMBER, bg=BG,
         font=("Courier", 11)).grid(row=0, column=0, sticky="w")

album_entry = ttk.Entry(input_frame, width=40, font=("Courier", 11))
album_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="DISC ID:",
         fg=AMBER, bg=BG,
         font=("Courier", 11)).grid(row=0, column=2, padx=(15,0))

disc_entry = ttk.Entry(input_frame, width=10, font=("Courier", 11))
disc_entry.grid(row=0, column=3, padx=5)

# --- OUTPUT ---
output = tk.Text(root,
    width=70, height=8,
    bg=FIELD_BG, fg=AMBER,
    insertbackground=AMBER,
    font=("Courier", 10),
    relief="flat",
    highlightthickness=1,
    highlightcolor=AMBER
)
output.pack(padx=10, pady=5)

# --- FUNCTIONS ---
def log(msg):
    output.delete("1.0", END)
    output.insert(END, msg)

def append(msg):
    output.insert(END, msg)

def refresh_list():
    album_listbox.delete(0, END)
    for item in get_albums():
        album_listbox.insert(END, item)
    append("Library refreshed.\n")

def on_select(event):
    selection = album_listbox.curselection()
    if selection:
        selected = album_listbox.get(selection[0])
        album_id = int(selected[0:3])
        album_name = selected.split("|", 1)[1].strip()

        album_entry.delete(0, END)
        album_entry.insert(0, album_name)

        log(f"Selected: {album_id} {album_name}\n")

def check():
    disc_id = disc_entry.get()
    result = check_cdslot(disc_id)

    if result:
        text_out = "FOUND:\n"
        for row in result:
            text_out += f"{row.album_id:03d} | {row.album_title} | Disc {row.disc_id}\n"
    else:
        text_out = "NOT FOUND\n"

    log(text_out)

def insert():
    selection = album_listbox.curselection()
    if not selection:
        log("⚠️ Select an album first\n")
        return

    selected = album_listbox.get(selection[0])
    album_id = int(selected[0:3])
    album_name = selected.split("|", 1)[1].strip()
    disc_id = disc_entry.get()

    try:
        disc_id = int(disc_id)
    except ValueError:
        log("⚠️ Disc ID must be a number\n")
        return

    duplicate = update_disc_id(album_id, disc_id)

    if duplicate:
        append(
            f"⚠️ Duplicate found!\n"
            f"Album '{duplicate}' had Disc_ID {disc_id}\n"
            f"→ Reset to 0\n"
            f"→ Updated successfully\n"
        )
    else:
        append(f"✅ Disc_ID {disc_id} assigned\n")

    append(f"INSERTED: Album_ID {album_id} {album_name} into Disc slot {disc_id}\n")
    refresh_list()

# --- BUTTONS ---
btn_frame = tk.Frame(root, bg=BG)
btn_frame.pack(pady=5)

ttk.Button(btn_frame, text="CHECK", command=check).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="INSERT", command=insert).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="REFRESH", command=refresh_list).grid(row=0, column=2, padx=5)
ttk.Button(btn_frame, text="EXIT", command=root.quit).grid(row=0, column=3, padx=5)

# --- EVENTS ---
album_listbox.bind("<<ListboxSelect>>", on_select)

# --- INIT ---
refresh_list()

root.mainloop()
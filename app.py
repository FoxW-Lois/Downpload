import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pytubefix import YouTube
from pydub import AudioSegment
from PIL import Image, ImageTk
import os
import sqlite3
from datetime import datetime

# --- Base de données ---
conn = sqlite3.connect("downloads.db")
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        format TEXT,
        path TEXT,
        date TEXT
    )
''')
conn.commit()

def log_download(title, url, format_type, path):
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO downloads (title, url, format, path, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, url, format_type, path, date_now))
    conn.commit()

# --- Fonction principale de téléchargement ---
def download_video(url, path, audio_only):
    try:
        yt = YouTube(url)
        title = yt.title

        if audio_only:
            stream = yt.streams.get_audio_only()
            downloaded_file = stream.download(output_path=path)

            base, _ = os.path.splitext(downloaded_file)
            mp3_file = base + ".mp3"

            audio = AudioSegment.from_file(downloaded_file, format="m4a")
            audio.export(mp3_file, format="mp3")
            os.remove(downloaded_file)

            log_download(title, url, "Audio", mp3_file)
            messagebox.showinfo("Succès", "Fichier MP3 téléchargé et converti avec succès !")

        else:
            stream = yt.streams.get_highest_resolution()
            final_path = stream.download(output_path=path)

            log_download(title, url, "Video", final_path)
            messagebox.showinfo("Succès", "Fichier MP4 téléchargé avec succès !")

    except Exception as e:
        messagebox.showerror("Erreur", f"Téléchargement échoué: {e}")

# --- Autres fonctions ---
def start_download(audio_only):
    url = url_entry.get()
    path = path_entry.get()
    if url and path:
        download_video(url, path, audio_only)
    else:
        messagebox.showwarning("Attention", "Veuillez fournir une URL et un chemin de téléchargement.")

def browse_folder():
    folder_selected = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_selected)


# --- Interface graphique ---
root = tk.Tk()
root.title("DownPload - YouTube Downloader")
root.geometry("400x400")
root.resizable(False, False)

# Frame pour l'entête
header_frame = tk.Frame(root)
header_frame.pack(pady=10)

# Image du logo
logo_img = Image.open("icon.png")
logo_img = logo_img.resize((36, 36))
logo_tk = ImageTk.PhotoImage(logo_img)

# Double logo encadrant le nom
logo_label = tk.Label(header_frame, image=logo_tk)
logo_label.pack(side="left", padx=(0, 10))
logo_label2 = tk.Label(header_frame, image=logo_tk)
logo_label2.pack(side="right", padx=(10, 0))

# Titre
header_text = tk.Label(header_frame, text="DownPload", font=("Helvetica", 14, "bold"))
header_text.pack(side="left")

# Icon de l'application
path = "icon.png"
load = Image.open(path)
render = ImageTk.PhotoImage(load)
root.iconphoto(False, render)

# Entrée pour URL
url_label = tk.Label(root, text="URL de la vidéo YouTube :")
url_label.pack(pady=(20,0))
url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=5)

# Choix du format
format_label = tk.Label(root, text="Format :")
format_label.pack(pady=(20,0))
format_var = tk.StringVar(value="Video")
format_choice = ttk.Combobox(root, textvariable=format_var, values=["Video", "Audio"])
format_choice.pack(pady=5)

# Entrée pour chemin de téléchargement
path_label = tk.Label(root, text="Dossier de téléchargement :")
path_label.pack(pady=(20,0))
path_entry = ttk.Entry(root, width=50)
path_entry.pack(pady=5)

# Bouton téléchargement
browse_button = ttk.Button(root, text="Parcourir", command=browse_folder)
browse_button.pack(pady=5)

download_btn = ttk.Button(
    root, text="Télécharger",
    command=lambda: start_download(audio_only=(format_var.get() == "Audio"))
)
download_btn.pack(pady=30)

root.mainloop()

# Ferme la connexion à la base de données quand l'app se ferme
conn.close()

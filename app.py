import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pytubefix import YouTube
from pydub import AudioSegment
from PIL import Image, ImageTk
import os
import sqlite3
from datetime import datetime
import subprocess
import re

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
def download_video(url, path, audio_only, format_source):
	try:
		yt = YouTube(url)
		title = re.sub(r'[\\/:*?"<>|]', '', yt.title)

		if audio_only:
			stream = yt.streams.get_audio_only()
			downloaded_file = stream.download(output_path=path)

			base, _ = os.path.splitext(downloaded_file)
			mp3_file = base + ".mp3"

			audio = AudioSegment.from_file(downloaded_file, format="m4a")
			audio.export(mp3_file, format="mp3", bitrate="320k")
			os.remove(downloaded_file)

			log_download(title, url, "Audio", mp3_file)
			update_counter()
			messagebox.showinfo("Succès", "Fichier MP3 téléchargé et converti avec succès !")

		else:
			# Récupère la résolution vidéo choisie
			format = format_source.split(" ")[-1]

			# Télécharger l'image et l'audio séparément
			video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, res=format).first()
			audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()

			if not video_stream or not audio_stream:
				raise Exception("Flux vidéo ", format, " ou audio introuvable.")

			video_path = video_stream.download(output_path=path, filename="temp_video.mp4")
			audio_path = audio_stream.download(output_path=path, filename="temp_audio.mp4")

			base_audio, _ = os.path.splitext(audio_path)
			converted_audio_file = base_audio + "_320.mp3"
			audio = AudioSegment.from_file(audio_path, format="mp4")
			audio.export(converted_audio_file, format="mp3", bitrate="320k")

			output_path = os.path.join(path, f"{title}.mp4")

			# Fusionner avec ffmpeg
			cmd = [
				"ffmpeg",
				"-i", video_path,
				"-i", converted_audio_file,
				"-c:v", "copy",
				"-c:a", "aac",
				"-b:a", "320k",
				"-strict", "experimental",
				output_path
			]
			subprocess.run(cmd, check=True)

			# Nettoyer les fichiers temporaires
			os.remove(video_path)
			os.remove(audio_path)
			os.remove(converted_audio_file)

			log_download(title, url, format_source, output_path)
			update_counter()
			messagebox.showinfo("Succès", f"Vidéo téléchargée en {format} avec succès !")

	except Exception as e:
		messagebox.showerror("Erreur", f"Téléchargement échoué: {e}")

# --- Autres fonctions ---
def start_download():
	url = url_entry.get()
	path = path_entry.get()
	selected_format = format_var.get()

	if url and path:
		audio_only = (selected_format == "Audio")
		download_video(url, path, audio_only, selected_format)
	else:
		messagebox.showwarning("Attention", "Veuillez fournir une URL et un chemin de téléchargement.")


def browse_folder():
	folder_selected = filedialog.askdirectory()
	path_entry.delete(0, tk.END)
	path_entry.insert(0, folder_selected)


# --- Mise à jour du compteur ---
def update_counter():
	c.execute("SELECT COUNT(*) FROM downloads")
	total = c.fetchone()[0]

	c.execute("SELECT COUNT(*) FROM downloads WHERE format IN ('Video 240p', 'Video 360p', 'Video 480p', 'Video 720p', 'Video 1080p')")
	videos = c.fetchone()[0]

	c.execute("SELECT COUNT(*) FROM downloads WHERE format = 'Audio'")
	audios = c.fetchone()[0]

	counter_var.set(f"Total : {total}\nVidéos : {videos}\nMusiques : {audios}")

# --- Fonction pour l'historique ---
def show_history():
	history_window = tk.Toplevel(root)
	history_window.title("Historique des téléchargements")
	history_window.geometry("800x350")
	history_window.iconphoto(False, render)

	tree = ttk.Treeview(history_window, columns=("Titre", "Format", "Date", "Chemin"), show="headings")
	tree.heading("Titre", text="Titre")
	tree.heading("Format", text="Format")
	tree.heading("Date", text="Date")
	tree.heading("Chemin", text="Chemin")

	# Colonnes taille adaptative
	tree.column("Titre", width=160)
	tree.column("Format", width=80)
	tree.column("Date", width=120)
	tree.column("Chemin", width=340)

	c.execute("SELECT title, format, date, path FROM downloads ORDER BY date DESC")
	rows = c.fetchall()
	for row in rows:
		tree.insert("", tk.END, values=row)

	tree.pack(fill="both", expand=True, padx=10, pady=10)


# --- Interface graphique ---
root = tk.Tk()
root.title("DownPload - YouTube Downloader")
root.geometry("400x430")
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
format_var = tk.StringVar(value="Video 1080p")
format_choice = ttk.Combobox(root, textvariable=format_var, values=["Audio", "Video 240p", "Video 360p", "Video 480p", "Video 720p", "Video 1080p"])
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
	command=start_download
)
download_btn.pack(pady=(30,0))

# --- Footer avec compteur et bouton historique ---
footer_frame = tk.Frame(root)
footer_frame.pack(side="bottom", fill="x", pady=5, padx=10)

counter_var = tk.StringVar()
counter_label = tk.Label(footer_frame, textvariable=counter_var, font=("Arial", 9), anchor="w", justify="left")
counter_label.pack(side="left")

history_button = ttk.Button(footer_frame, text="Historique", command=show_history)
history_button.pack(side="right")


# Mise à jour initiale
update_counter()

root.mainloop()

# Ferme la connexion à la base de données quand l'app se ferme
conn.close()

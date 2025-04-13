# 🎵📥 DownPload - YouTube Downloader

DownPload est une petite application de bureau en Python (Tkinter) permettant de télécharger facilement des vidéos ou de la musique depuis YouTube, au format MP4 ou MP3.  
Une base de données SQLite intégrée garde la trace de tous vos téléchargements 📊.

(Attention les vidéos ne sont pour l'instant téléchargeables qu'en 360p !)

---

## ⚙️ Fonctionnalités

- Téléchargement de vidéos YouTube en qualité maximale (MP4)
- Téléchargement d'audio uniquement, avec conversion en MP3 (via `ffmpeg`)
- Interface simple et intuitive avec `Tkinter`
- Historique automatique des téléchargements (SQLite)
- Compatible Windows

---

## 💻 Installation

### 1. Clonez le repo
```bash
git clone https://github.com/votre-utilisateur/downpload.git
cd downpload
```

### 2. Installez les dépendances Python
Utilisez un environnement virtuel si possible (recommandé) :
```bash
python -m venv venv
venv\Scripts\activate   # Sur Windows
```

Puis installez les paquets :
```bash
pip install -r requirements.txt
```

**Fichier `requirements.txt` suggéré :**
```text
pytubefix
pydub
pillow
```

---

## 🔧 Installation de `ffmpeg` (obligatoire pour l'audio)

La conversion en MP3 nécessite `ffmpeg`, un outil puissant de traitement audio/vidéo. Voici comment l'installer :

1. Rendez-vous sur 👉 [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Téléchargez l'archive **`ffmpeg-git-full.7z`**
3. Extrayez-la dans un dossier de votre choix (ex: `C:\ffmpeg`)
4. Copiez le chemin du dossier `bin` (ex: `C:\ffmpeg\bin`)
5. Ajoutez ce chemin à la variable d'environnement **`PATH`** :
    - Recherche "variables d'environnement" dans le menu Démarrer
    - Cliquez sur "Path" > Modifier > Nouveau
    - Collez le chemin du dossier `bin`
6. Redémarrez votre terminal ou votre éditeur de code

---

## 🚀 Lancer l'application

```bash
python app.py
```

---

## 🗃️ Base de données

L'application crée un fichier `downloads.db` qui enregistre automatiquement :
- Le titre de la vidéo
- L’URL
- Le format (Audio ou Vidéo)
- Le chemin de sauvegarde
- La date du téléchargement

---

## 📸 Aperçu

![Screenshot de l'application](downpload.png)

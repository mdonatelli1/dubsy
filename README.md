## Dubsy — Video Subtitle Translator

Outil complet pour générer automatiquement des sous-titres traduits à partir d’une vidéo, puis les intégrer (hard/soft) et permettre le téléchargement du fichier `.mp4` et/ou `.srt`.

### Stack

-   **Backend**: FastAPI, Uvicorn, MoviePy, OpenAI (Whisper + chat models)
-   **Frontend**: HTML/CSS/JS vanilla (interface d’upload et suivi de progression)

### Arborescence

```
dubsy/
  client/               # Frontend statique
  server/               # API FastAPI
    api/                # Routes
    services/           # Pipeline vidéo (audio, srt, intégration)
    utils/              # Exceptions, validateurs, helpers
    config/             # Chargement/validation des env
```

### Prérequis

-   Python 3.10+ (recommandé 3.11)
-   Une clé API OpenAI (variable `OPENAI_API_KEY`)
-   FFmpeg (recommandé). MoviePy peut télécharger un binaire via `imageio-ffmpeg`, mais l’installation locale de FFmpeg est plus fiable.

### Quickstart

1. Installer le backend

```
cd server
python -m venv .venv && .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt

# Variables d’environnement (à adapter)
$env:OPENAI_API_KEY = "sk-..."
$env:HOST = "0.0.0.0"
$env:PORT = "8000"
$env:DEBUG = "true"
$env:TEMP_DIR = "$PWD/tmp"

python main.py
# Docs Swagger: http://localhost:8000/docs
```

2. Lancer le frontend

```
cd ../client
# Option 1: ouvrir index.html directement dans le navigateur
# Option 2 (recommandé pour CORS): servir via un petit serveur
python -m http.server 5500  # puis ouvrir http://localhost:5500
```

3. Utilisation

-   Déposer une vidéo (`.mp4/.avi/.mov/.mkv`) dans l’UI
-   Choisir la langue source et la langue cible
-   Lancer la traduction → suivre la progression → télécharger la vidéo sous-titrée et/ou le `.srt`

### Configuration serveur (env)

-   `OPENAI_API_KEY` (obligatoire)
-   `HOST` (défaut `0.0.0.0`)
-   `PORT` (défaut `8000`)
-   `DEBUG` (`true`/`false`)
-   `TEMP_DIR` (défaut `/tmp`)
-   `MAX_FILE_SIZE` (défini dans le code à 100MB)
-   `DEFAULT_SOURCE_LANG` (défaut `en`)
-   `DEFAULT_TARGET_LANG` (défaut `fr`)

### Documentation détaillée

-   Backend/API: voir `server/README.md`
-   Frontend: voir `client/README.md`

### Dépannage

-   Erreur taille fichier: vérifier `MAX_FILE_SIZE` et la taille de la vidéo
-   404 au téléchargement: le fichier temporaire peut avoir été nettoyé; relancer un traitement
-   CORS: le backend autorise `*`, mais préférez servir le client via HTTP local

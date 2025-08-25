## Server — FastAPI (Video Subtitle Translator API)

API pour téléverser une vidéo, transcrire (Whisper), traduire (modèles OpenAI), générer un `.srt` et produire une vidéo avec sous-titres (hard/soft), puis permettre le téléchargement.

### Installation

```
cd server
python -m venv .venv && .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
```

### Configuration (env)

Les variables sont lues via `config/settings.py` (dotenv supporté).

-   `OPENAI_API_KEY` (obligatoire)
-   `HOST` (défaut `0.0.0.0`)
-   `PORT` (défaut `8000`)
-   `DEBUG` (`true`/`false`)
-   `TEMP_DIR` (défaut `/tmp`)
-   `MAX_FILE_SIZE` (100MB dans le code)
-   `ALLOWED_EXTENSIONS` (`.mp4,.avi,.mov,.mkv`)
-   `WHISPER_MODEL` (`whisper-1`)
-   `TRANSLATION_MODEL` (`gpt-3.5-turbo`)

Au démarrage, la config est validée. En l’absence de `OPENAI_API_KEY` ou si `TEMP_DIR` est invalide, l’application échoue explicitement.

### Lancement

```
python main.py
# Swagger: http://localhost:8000/docs
```

### Endpoints

1. POST `/upload-and-translate`

-   Form-data:
    -   `file`: UploadFile (vidéo)
    -   `source_lang`: `en` par défaut
    -   `target_lang`: `fr` par défaut
    -   `subtitle_type`: `hard` ou `soft` (par défaut `hard`)
-   Réponse JSON (exemple):

```json
{
    "message": "Traduction et intégration terminées avec succès",
    "srt_file_path": "/tmp/subtitles_123.srt",
    "video_with_subtitles": "/tmp/video_123.mp4",
    "segments_count": 42,
    "subtitle_type": "hard",
    "status": "completed"
}
```

-   Codes erreurs: `400` (validation), `413` (fichier trop volumineux), `500` (erreur interne)

2. GET `/download-video/{filename}`

-   Télécharge la vidéo sous-titrée (`video/mp4`) depuis `TEMP_DIR`.
-   404 si le fichier n’existe plus.

3. GET `/download-srt/{filename}`

-   Télécharge le fichier `.srt` (`text/plain`) depuis `TEMP_DIR`.
-   404 si le fichier n’existe plus.

4. GET `/health`

-   Renvoie l’état du service et les fonctionnalités disponibles.

### Notes d’implémentation

-   Les validations fichier et langues sont gérées via `utils.validators`.
-   Les erreurs spécifiques remontent `utils.exceptions` et sont interceptées globalement.
-   Le pipeline principal est orchestré par `services.video_processor.VideoProcessor.process_video`.
-   Les fichiers temporaires d’entrée sont nettoyés en fin de traitement.

### Développement

-   Activer le mode DEBUG (`DEBUG=true`) pour le reload Uvicorn.
-   Les dépendances sont listées dans `requirements.txt`.

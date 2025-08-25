import os
import uuid

from config.settings import settings
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse
from services.video_processor import VideoProcessor
from utils.exceptions import FileValidationError, VideoProcessingError
from utils.progress_manager import progress_manager
from utils.validators import (
    sanitize_filename,
    validate_language_code,
    validate_video_file,
)

router = APIRouter()
video_processor = VideoProcessor()


@router.post("/upload-and-translate")
async def upload_and_translate(
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
    subtitle_type: str = Form("hard"),  # "hard" ou "soft"
    job_id: str = Form(None),
):
    """Endpoint pour uploader une vidéo et générer une vidéo avec sous-titres"""

    temp_video_path = None

    try:
        # Validation du fichier
        validate_video_file(file)

        # Validation des langues
        if not validate_language_code(source_lang):
            raise HTTPException(
                status_code=400, detail=f"Code de langue source invalide: {source_lang}"
            )

        if not validate_language_code(target_lang):
            raise HTTPException(
                status_code=400, detail=f"Code de langue cible invalide: {target_lang}"
            )

        # Validation du type de sous-titres
        if subtitle_type not in ["hard", "soft"]:
            subtitle_type = "hard"

        # Sauvegarder le fichier temporairement
        safe_filename = sanitize_filename(file.filename)
        temp_filename = f"temp_{uuid.uuid4().hex}_{safe_filename}"
        temp_video_path = os.path.join(settings.TEMP_DIR, temp_filename)

        # Lire et sauvegarder le fichier
        content = await file.read()

        # Vérifier la taille
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Fichier trop volumineux. Taille maximum: {settings.MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        with open(temp_video_path, "wb") as buffer:
            buffer.write(content)

        # Traiter la vidéo (pipeline complet)
        # notifier le démarrage
        if job_id:
            await progress_manager.send(job_id, "started", {"filename": safe_filename})

        result = await video_processor.process_video(
            temp_video_path, source_lang, target_lang, subtitle_type, job_id=job_id
        )

        response = {
            "message": "Traduction et intégration terminées avec succès",
            "srt_file_path": result["srt_file"],
            "video_with_subtitles": result["video_with_subtitles"],
            "segments_count": result["segments_count"],
            "subtitle_type": result["subtitle_type"],
            "status": result["status"],
        }
        if job_id:
            await progress_manager.send(job_id, "completed", response)
        return response

    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except VideoProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

    finally:
        # Nettoyage du fichier d'entrée
        if temp_video_path and os.path.exists(temp_video_path):
            video_processor.cleanup_temp_file(temp_video_path)


@router.websocket("/ws/{job_id}")
async def ws_progress(websocket: WebSocket, job_id: str):
    await progress_manager.connect(job_id, websocket)
    try:
        while True:
            # keep the connection open; we don't expect messages from client
            await websocket.receive_text()
    except WebSocketDisconnect:
        progress_manager.disconnect(job_id, websocket)


@router.get("/download-video/{filename}")
async def download_video(filename: str):
    """Endpoint pour télécharger la vidéo avec sous-titres"""
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(settings.TEMP_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier vidéo non trouvé")

    return FileResponse(path=file_path, filename=safe_filename, media_type="video/mp4")


@router.get("/download-srt/{filename}")
async def download_srt(filename: str):
    """Endpoint pour télécharger le fichier SRT"""
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(settings.TEMP_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier SRT non trouvé")

    return FileResponse(path=file_path, filename=safe_filename, media_type="text/plain")


@router.get("/health")
async def health_check():
    """Endpoint de santé"""
    return {
        "status": "healthy",
        "service": "Video Subtitle Translator",
        "version": "1.0.0",
        "features": [
            "audio_extraction",
            "transcription",
            "translation",
            "subtitle_integration",
        ],
    }

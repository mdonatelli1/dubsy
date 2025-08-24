import os
import uuid

from config.settings import settings
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from services.video_processor import VideoProcessor
from utils.exceptions import FileValidationError, VideoProcessingError
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
    source_lang: str = Form(settings.DEFAULT_SOURCE_LANG),
    target_lang: str = Form(settings.DEFAULT_TARGET_LANG),
):
    """Endpoint pour uploader une vidéo et générer des sous-titres traduits"""

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

        # Traiter la vidéo
        result = await video_processor.process_video(
            temp_video_path, source_lang, target_lang
        )

        return {
            "message": "Traduction terminée avec succès",
            "srt_file_path": result["srt_file"],
            "segments_count": result["segments_count"],
            "status": result["status"],
        }

    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except VideoProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

    finally:
        # Nettoyage
        if temp_video_path and os.path.exists(temp_video_path):
            video_processor.cleanup_temp_file(temp_video_path)


@router.get("/download-srt/{filename}")
async def download_srt(filename: str):
    """Endpoint pour télécharger le fichier SRT"""
    # Sécurité: nettoyer le nom de fichier
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(settings.TEMP_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")

    return FileResponse(path=file_path, filename=safe_filename, media_type="text/plain")


@router.get("/health")
async def health_check():
    """Endpoint de santé"""
    return {
        "status": "healthy",
        "service": "Video Subtitle Translator",
        "version": "1.0.0",
    }

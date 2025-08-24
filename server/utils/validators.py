from pathlib import Path

from config.settings import settings
from fastapi import UploadFile

from .exceptions import FileValidationError


def validate_video_file(file: UploadFile) -> None:
    """Valide un fichier vidéo uploadé"""
    if not file.filename:
        raise FileValidationError("Nom de fichier manquant")

    # Vérifier l'extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Format non supporté. Extensions autorisées: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Note: La taille sera vérifiée lors de la lecture du fichier


def validate_language_code(lang_code: str) -> bool:
    """Valide un code de langue"""
    valid_languages = {
        "en",
        "fr",
        "es",
        "de",
        "it",
        "pt",
        "zh",
        "ja",
        "ko",
        "ru",
        "ar",
        "hi",
        "nl",
        "sv",
        "no",
        "da",
        "fi",
    }
    return lang_code in valid_languages


def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier"""
    # Remplacer les caractères dangereux
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    return "".join(c if c in safe_chars else "_" for c in filename)

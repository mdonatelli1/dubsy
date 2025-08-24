class VideoProcessingError(Exception):
    """Exception de base pour le traitement vidéo"""

    pass


class AudioExtractionError(VideoProcessingError):
    """Erreur lors de l'extraction audio"""

    pass


class TranscriptionError(VideoProcessingError):
    """Erreur lors de la transcription"""

    pass


class TranslationError(VideoProcessingError):
    """Erreur lors de la traduction"""

    pass


class SubtitleGenerationError(VideoProcessingError):
    """Erreur lors de la génération de sous-titres"""

    pass


class FileValidationError(Exception):
    """Erreur de validation de fichier"""

    pass

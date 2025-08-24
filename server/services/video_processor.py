import os
from typing import Dict

from config.settings import settings
from utils.exceptions import VideoProcessingError

from .audio_service import AudioService
from .subtitle_service import SubtitleService
from .transcription_service import TranscriptionService
from .translation_service import TranslationService


class VideoProcessor:
    def __init__(self):
        self.audio_service = AudioService(settings.TEMP_DIR)
        self.transcription_service = TranscriptionService(settings.OPENAI_API_KEY)
        self.translation_service = TranslationService(settings.OPENAI_API_KEY)
        self.subtitle_service = SubtitleService(settings.TEMP_DIR)

    async def process_video(
        self, video_path: str, source_lang: str = "en", target_lang: str = "fr"
    ) -> Dict[str, any]:
        """Pipeline complet de traitement vidéo"""
        audio_path = None

        try:
            # 1. Extraction audio
            audio_path = self.audio_service.extract_audio_from_video(video_path)

            # 2. Transcription
            transcript = self.transcription_service.transcribe_audio(
                audio_path, source_lang
            )

            # 3. Traduction
            translated_segments = await self.translation_service.translate_segments(
                transcript["segments"], target_lang
            )

            # 4. Génération SRT
            srt_path = self.subtitle_service.create_srt_file(translated_segments)

            return {
                "srt_file": srt_path,
                "original_transcript": transcript,
                "translated_segments": translated_segments,
                "segments_count": len(translated_segments),
                "status": "success",
            }

        except Exception as e:
            raise VideoProcessingError(
                f"Erreur dans le pipeline de traitement: {str(e)}"
            )

        finally:
            # Nettoyage
            if audio_path:
                self.audio_service.cleanup_audio_file(audio_path)

    def cleanup_temp_file(self, file_path: str) -> None:
        """Nettoie un fichier temporaire"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

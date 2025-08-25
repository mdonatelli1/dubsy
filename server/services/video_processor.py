import os
from typing import Dict

from config.settings import settings
from utils.exceptions import VideoProcessingError

from .audio_service import AudioService
from .subtitle_service import SubtitleService
from .transcription_service import TranscriptionService
from .translation_service import TranslationService
from .video_combiner import VideoCombinerService


class VideoProcessor:
    def __init__(self):
        self.audio_service = AudioService(settings.TEMP_DIR)
        self.transcription_service = TranscriptionService(settings.OPENAI_API_KEY)
        self.translation_service = TranslationService(settings.OPENAI_API_KEY)
        self.subtitle_service = SubtitleService(settings.TEMP_DIR)
        self.video_combiner = VideoCombinerService(settings.TEMP_DIR)

    async def process_video(
        self,
        video_path: str,
        source_lang: str = "en",
        target_lang: str = "fr",
        subtitle_type: str = "hard",  # "hard" ou "soft"
    ) -> Dict[str, any]:
        """Pipeline complet de traitement vidéo avec intégration"""
        audio_path = None
        srt_path = None

        try:
            print(f"🎬 Début du traitement: {video_path}")

            # 1. Extraction audio
            print("🎵 Extraction de l'audio...")
            audio_path = self.audio_service.extract_audio_from_video(video_path)
            print(f"✅ Audio extrait: {audio_path}")

            # 2. Transcription
            print("🎤 Transcription avec Whisper...")
            transcript = self.transcription_service.transcribe_audio(
                audio_path, source_lang
            )
            print(f"✅ Transcription terminée: {len(transcript['segments'])} segments")

            # 3. Traduction
            print("🔤 Traduction des segments...")
            translated_segments = await self.translation_service.translate_segments(
                transcript["segments"], target_lang
            )
            print(f"✅ Traduction terminée: {len(translated_segments)} segments")

            # 4. Génération SRT
            print("📝 Génération du fichier SRT...")
            srt_path = self.subtitle_service.create_srt_file(translated_segments)
            print(f"✅ SRT généré: {srt_path}")

            # 5. Intégration à la vidéo
            print("🎬 Intégration des sous-titres à la vidéo...")
            if subtitle_type == "soft":
                video_output_path = self.video_combiner.create_soft_subtitles(
                    video_path, srt_path
                )
            else:
                video_output_path = self.video_combiner.combine_video_with_subtitles(
                    video_path, srt_path
                )

            print(f"✅ Vidéo finale créée: {video_output_path}")

            return {
                "srt_file": srt_path,
                "video_with_subtitles": video_output_path,
                "original_transcript": transcript,
                "translated_segments": translated_segments,
                "segments_count": len(translated_segments),
                "subtitle_type": subtitle_type,
                "status": "success",
            }

        except Exception as e:
            print(f"❌ Erreur dans le pipeline: {str(e)}")
            raise VideoProcessingError(
                f"Erreur dans le pipeline de traitement: {str(e)}"
            )

        finally:
            # Nettoyage des fichiers intermédiaires
            if audio_path:
                print("🧹 Nettoyage des fichiers temporaires...")
                self.audio_service.cleanup_audio_file(audio_path)

    def cleanup_temp_file(self, file_path: str) -> None:
        """Nettoie un fichier temporaire"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Fichier supprimé: {file_path}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage de {file_path}: {e}")

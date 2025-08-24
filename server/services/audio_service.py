import os
import uuid

from moviepy.video.io.VideoFileClip import VideoFileClip
from utils.exceptions import AudioExtractionError


class AudioService:
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir

    def extract_audio_from_video(self, video_path: str) -> str:
        """Extrait l'audio d'une vidéo et la sauvegarde en format WAV"""
        try:
            # Générer un nom unique pour l'audio
            audio_filename = f"audio_{uuid.uuid4().hex}.wav"
            audio_path = os.path.join(self.temp_dir, audio_filename)

            # Extraire l'audio
            with VideoFileClip(video_path) as video:
                audio = video.audio
                if audio is None:
                    raise AudioExtractionError(
                        "Aucune piste audio trouvée dans la vidéo"
                    )

                audio.write_audiofile(audio_path, logger=None)

            return audio_path

        except Exception as e:
            if "AudioExtractionError" in str(type(e)):
                raise
            raise AudioExtractionError(f"Erreur lors de l'extraction audio: {str(e)}")

    def cleanup_audio_file(self, audio_path: str) -> None:
        """Nettoie un fichier audio temporaire"""
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass  # Ignore les erreurs de nettoyage

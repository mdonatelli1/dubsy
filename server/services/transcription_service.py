from typing import Dict

import openai
from config.settings import settings
from utils.exceptions import TranscriptionError


class TranscriptionService:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict:
        """Transcrit un fichier audio avec Whisper"""
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=settings.WHISPER_MODEL,
                    file=audio_file,
                    response_format="verbose_json",
                    language=language,
                )

            result = transcript.model_dump()

            # Validation du résultat
            if not result.get("segments"):
                raise TranscriptionError("Aucun segment trouvé dans la transcription")

            return result

        except openai.APIError as e:
            raise TranscriptionError(f"Erreur API OpenAI: {str(e)}")
        except FileNotFoundError:
            raise TranscriptionError(f"Fichier audio non trouvé: {audio_path}")
        except Exception as e:
            raise TranscriptionError(f"Erreur lors de la transcription: {str(e)}")

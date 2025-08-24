import os
import uuid
from datetime import timedelta
from typing import Dict, List

import pysrt
from utils.exceptions import SubtitleGenerationError


class SubtitleService:
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir

    def create_srt_file(self, segments: List[Dict]) -> str:
        """Crée un fichier SRT à partir des segments traduits"""
        if not segments:
            raise SubtitleGenerationError("Aucun segment à convertir")

        try:
            # Générer un nom unique pour le fichier SRT
            srt_filename = f"subtitles_{uuid.uuid4().hex}.srt"
            srt_path = os.path.join(self.temp_dir, srt_filename)

            subs = pysrt.SubRipFile()

            for i, segment in enumerate(segments, 1):
                # Convertir les timestamps
                start_time = self._seconds_to_srt_time(segment["start"])
                end_time = self._seconds_to_srt_time(segment["end"])

                # Créer le sous-titre
                sub = pysrt.SubRipItem(
                    index=i, start=start_time, end=end_time, text=segment["text"]
                )
                subs.append(sub)

            # Sauvegarder le fichier
            subs.save(srt_path, encoding="utf-8")
            return srt_path

        except Exception as e:
            raise SubtitleGenerationError(
                f"Erreur lors de la création du fichier SRT: {str(e)}"
            )

    def _seconds_to_srt_time(self, seconds: float) -> pysrt.SubRipTime:
        """Convertit les secondes en format de temps SRT"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        milliseconds = int((td.total_seconds() % 1) * 1000)

        return pysrt.SubRipTime(hours, minutes, secs, milliseconds)

    def read_srt_content(self, srt_path: str) -> str:
        """Lit le contenu d'un fichier SRT"""
        try:
            with open(srt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise SubtitleGenerationError(
                f"Erreur lors de la lecture du fichier SRT: {str(e)}"
            )

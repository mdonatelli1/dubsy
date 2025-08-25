import os
import subprocess
import uuid
from pathlib import Path
from typing import Optional

from utils.exceptions import VideoProcessingError


class VideoCombinerService:
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Vérifie si FFmpeg est disponible"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise VideoProcessingError(
                "FFmpeg n'est pas installé. Installez-le depuis https://ffmpeg.org"
            )

    def combine_video_with_subtitles(
        self, video_path: str, srt_path: str, output_filename: Optional[str] = None
    ) -> str:
        """Combine une vidéo avec des sous-titres (hard-coded)"""
        try:
            # Générer un nom pour la vidéo de sortie
            if not output_filename:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_filename = (
                    f"{base_name}_with_subtitles_{uuid.uuid4().hex[:8]}.mp4"
                )

            srt_path = Path(srt_path).as_posix()
            video_path = Path(video_path).as_posix()
            output_path = (Path(self.temp_dir) / output_filename).as_posix()

            print("🎬 Intégration des sous-titres...")
            print(f"📹 Vidéo source: {video_path}")
            print(f"📄 Sous-titres: {srt_path}")
            print(f"🎯 Sortie: {output_path}")

            # Commande FFmpeg pour intégrer les sous-titres (hard-coded)
            cmd = [
                "ffmpeg",
                "-i",
                video_path,  # Vidéo d'entrée
                "-vf",
                f"subtitles='{srt_path}'",  # Filtre de sous-titres
                "-c:a",
                "copy",  # Copier l'audio sans réencodage
                "-c:v",
                "libx264",  # Codec vidéo
                "-preset",
                "medium",  # Qualité/vitesse
                "-crf",
                "23",  # Qualité vidéo
                output_path,  # Fichier de sortie
                "-y",  # Overwrite
            ]

            print("⚙️ Commande FFmpeg:", " ".join(cmd))

            # Exécuter FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes max
            )

            if result.returncode != 0:
                raise VideoProcessingError(
                    f"Erreur FFmpeg lors de l'intégration: {result.stderr}"
                )

            # Vérifier que le fichier a été créé
            if not os.path.exists(output_path):
                raise VideoProcessingError(
                    "La vidéo avec sous-titres n'a pas été créée"
                )

            # Vérifier que le fichier n'est pas vide
            if os.path.getsize(output_path) == 0:
                raise VideoProcessingError("La vidéo avec sous-titres est vide")

            print(f"✅ Vidéo avec sous-titres créée: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            raise VideoProcessingError("Timeout lors de l'intégration des sous-titres")
        except Exception as e:
            if isinstance(e, VideoProcessingError):
                raise
            raise VideoProcessingError(f"Erreur lors de l'intégration: {str(e)}")

    def create_soft_subtitles(
        self, video_path: str, srt_path: str, output_filename: Optional[str] = None
    ) -> str:
        """Alternative: Ajouter les sous-titres comme piste séparée (soft subs)"""
        try:
            if not output_filename:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_filename = (
                    f"{base_name}_with_soft_subs_{uuid.uuid4().hex[:8]}.mkv"
                )

            output_path = os.path.join(self.temp_dir, output_filename)

            cmd = [
                "ffmpeg",
                "-i",
                video_path,
                "-vf",
                f"subtitles={srt_path}",
                "-c:a",
                "copy",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                output_path,
                "-y",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise VideoProcessingError(
                    f"Erreur FFmpeg (soft subs): {result.stderr}"
                )

            return output_path

        except Exception as e:
            raise VideoProcessingError(f"Erreur soft subtitles: {str(e)}")

    def cleanup_video_file(self, video_path: str) -> None:
        """Nettoie un fichier vidéo temporaire"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"🗑️ Vidéo supprimée: {video_path}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage vidéo: {e}")

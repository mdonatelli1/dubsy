import argparse
import asyncio
import os

from config.settings import settings
from services.video_processor import VideoProcessor


async def main():
    """Interface en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Transcrire, traduire et sous-titrer une vidéo"
    )
    parser.add_argument("video_path", help="Chemin de la vidéo à traiter")
    parser.add_argument("source_lang", help="Langue source (ex: en, fr, es)")
    parser.add_argument("target_lang", help="Langue cible (ex: fr, en, es)")
    parser.add_argument(
        "--subtitle-type",
        choices=["hard", "soft"],
        default="hard",
        help="Type de sous-titres: hard (gravés) ou soft (piste)",
    )

    args = parser.parse_args()

    video_path = args.video_path
    source_lang = args.source_lang
    target_lang = args.target_lang
    subtitle_type = args.subtitle_type

    if not os.path.exists(video_path):
        print(f"❌ Erreur: Le fichier {video_path} n'existe pas")
        return

    try:
        # Validation de la configuration
        settings.validate()

        print(f"🎬 Traitement de: {video_path}")
        print(f"🌍 Langues: {source_lang} → {target_lang}")
        print(f"📝 Sous-titres: {subtitle_type}")
        print("=" * 50)

        processor = VideoProcessor()
        result = await processor.process_video(
            video_path,
            source_lang,
            target_lang,
            subtitle_type=subtitle_type,
        )

        print("✅ Traduction terminée!")
        print(f"📁 Fichier SRT créé: {result['srt_file']}")
        print(f"🎞️ Vidéo sortie: {result['video_with_subtitles']}")
        print(f"📊 Nombre de segments: {result['segments_count']}")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())

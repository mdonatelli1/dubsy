import asyncio
import os
import sys

from config.settings import settings
from services.video_processor import VideoProcessor


async def main():
    """Interface en ligne de commande"""
    if len(sys.argv) < 2:
        print("Usage: python cli.py <video_path> [source_lang] [target_lang]")
        print("Exemple: python cli.py video.mp4 en fr")
        return

    video_path = sys.argv[1]
    source_lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    target_lang = sys.argv[3] if len(sys.argv) > 3 else "fr"

    if not os.path.exists(video_path):
        print(f"❌ Erreur: Le fichier {video_path} n'existe pas")
        return

    try:
        # Validation de la configuration
        settings.validate()

        print(f"🎬 Traitement de: {video_path}")
        print(f"🌍 Langues: {source_lang} → {target_lang}")
        print("=" * 50)

        processor = VideoProcessor()
        result = await processor.process_video(video_path, source_lang, target_lang)

        print("✅ Traduction terminée!")
        print(f"📁 Fichier SRT créé: {result['srt_file']}")
        print(f"📊 Nombre de segments: {result['segments_count']}")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())

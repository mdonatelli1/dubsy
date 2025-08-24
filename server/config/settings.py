import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # File Configuration
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv"]
    TEMP_DIR = os.getenv("TEMP_DIR", "/tmp")

    # Processing Configuration
    WHISPER_MODEL = "whisper-1"
    TRANSLATION_MODEL = "gpt-3.5-turbo"
    DEFAULT_SOURCE_LANG = "en"
    DEFAULT_TARGET_LANG = "fr"

    # Rate Limiting
    TRANSLATION_DELAY = 0.1  # seconds between translations

    @classmethod
    def validate(cls):
        """Valide la configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        if not os.path.exists(cls.TEMP_DIR):
            try:
                os.makedirs(cls.TEMP_DIR, exist_ok=True)
            except Exception:
                raise ValueError(f"Cannot create temp directory: {cls.TEMP_DIR}")


settings = Settings()

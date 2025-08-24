import uvicorn
from api.routes import router
from config.settings import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.exceptions import VideoProcessingError

# Validation de la configuration au démarrage
try:
    settings.validate()
except ValueError as e:
    print(f"❌ Erreur de configuration: {e}")
    exit(1)

# Création de l'application FastAPI
app = FastAPI(
    title="Video Subtitle Translator API",
    description="API pour la traduction automatique de sous-titres vidéo",
    version="1.0.0",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(router)


# Handler d'exception global
@app.exception_handler(VideoProcessingError)
async def video_processing_exception_handler(request, exc):
    return {"error": "Erreur de traitement vidéo", "detail": str(exc)}


if __name__ == "__main__":
    print("🚀 Démarrage du serveur Video Subtitle Translator...")
    print(
        f"📝 Documentation disponible sur: http://{settings.HOST}:{settings.PORT}/docs"
    )
    print(f"🔧 Mode debug: {settings.DEBUG}")

    uvicorn.run(
        "main:app" if settings.DEBUG else app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

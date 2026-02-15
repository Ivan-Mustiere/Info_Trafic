import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.predict import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fil Rouge – API IA Trafic",
    description="API de prédiction d'état du trafic routier",
    version="1.0.0"
)

# Middleware CORS pour permettre l'accès depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("API démarrée avec succès")

# Endpoint de santé
@app.get("/health")
def health_check():
    from model_loader import model
    return {
        "status": "ok",
        "model_loaded": model is not None
    }

# Inclure les endpoints
app.include_router(router, prefix="/api")
    
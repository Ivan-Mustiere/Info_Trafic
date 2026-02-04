from fastapi import FastAPI
from pathlib import Path
import joblib

# pour la santé et charger le modèle
from api.endpoints.predict import router

app = FastAPI(title="Fil Rouge – API IA Trafic")

MODEL_PATH = "/app/models/model.joblib"

model = joblib.load(MODEL_PATH)

# health check simple
@app.get("/health")
def health_check():
    return {"status": "ok"}

# inclure les endpoints
app.include_router(router, prefix="/api")

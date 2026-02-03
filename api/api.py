from fastapi import FastAPI
import joblib
from pathlib import Path
from schemas import PredictionInput

# Création de l'app FastAPI
app = FastAPI(title="Fil Rouge – API IA Trafic")

# Chemin vers le modèle entraîné (pipeline scaler + modèle)
MODEL_PATH = Path(__file__).resolve().parent / "models" / "model.joblib"

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle chargé depuis {MODEL_PATH}")
except FileNotFoundError:
    print(
        f"⚠️  Modèle non trouvé à {MODEL_PATH}. "
        f"L'API démarrera mais les prédictions ne fonctionneront pas."
    )
    model = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: PredictionInput):
    """
    Endpoint de prédiction d'état du trafic.
    """
    if model is None:
        return {"error": "Modèle non disponible. Veuillez d'abord entraîner le modèle."}

    # Les features doivent être passées dans le même ordre que pendant le training
    X = [
        [
            data.identifiant_arc,
            data.heure,
            data.jour_semaine,
            data.is_weekend,
            data.taux_occupation,
            data.lat,
            data.lon,
        ]
    ]

    prediction = model.predict(X)

    return {
        "prediction": str(prediction[0]),
    }

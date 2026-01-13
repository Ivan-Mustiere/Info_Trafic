from fastapi import FastAPI
import joblib
from pathlib import Path
from schemas import PredictionInput

# Création de l'app FastAPI
app = FastAPI(title="Fil Rouge – API IA")

# Chargement du modèle au démarrage
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model_v1.joblib"
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    print(f"⚠️  Modèle non trouvé à {MODEL_PATH}. L'API démarrera mais les prédictions ne fonctionneront pas.")
    model = None

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: PredictionInput):
    """
    Endpoint de prédiction
    """
    if model is None:
        return {"error": "Modèle non disponible. Veuillez d'abord entraîner le modèle."}
    
    # Transformation des données en tableau
    X = [[
        data.age,
        data.tenure,
        data.monthly_fee
    ]]

    prediction = model.predict(X)

    return {
        "prediction": prediction[0]
    }

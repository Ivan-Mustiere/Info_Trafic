from fastapi import APIRouter
from schemas import PredictionInput, PredictionOutput
from model_loader import model

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput):
    """
    Endpoint de prédiction d'état du trafic.
    """
    if model is None:
        return PredictionOutput(prediction="Modèle non disponible")

    # Préparer les features pour le modèle
    X = [[
        data.identifiant_arc,
        data.heure,
        data.jour_semaine,
        data.is_weekend,
        data.taux_occupation,
        data.lat,
        data.lon
    ]]

    y_pred = model.predict(X)
    return PredictionOutput(prediction=str(y_pred[0]))

from fastapi import APIRouter
from schemas import PredictionInput, PredictionOutput
from api import model  # on importe le modèle chargé depuis api.py

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput):
    if model is None:
        return PredictionOutput(prediction="Modèle non disponible")

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

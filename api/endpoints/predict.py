from fastapi import APIRouter, HTTPException
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
    # Ordre attendu (training):
    # Identifiant arc, Débit horaire, Taux d'occupation, jour_semaine, is_weekend, Heure de comptage
    X = [[
        data.numero_route,
        data.debit_horaire,
        data.taux_occupation,
        data.jour_semaine,
        int(data.is_weekend),
        data.heure,
    ]]

    try:
        y_pred = model.predict(X)
        return PredictionOutput(prediction=str(y_pred[0]))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erreur de prédiction: {exc}")

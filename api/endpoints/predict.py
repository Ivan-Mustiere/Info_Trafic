import logging
from fastapi import APIRouter, HTTPException
from schemas import PredictionInput, PredictionOutput
from model_loader import model

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput):
    """
    Endpoint de prédiction d'état du trafic.
    
    Args:
        data: Données d'entrée pour la prédiction
    
    Returns:
        PredictionOutput: Résultat de la prédiction
    """
    if model is None:
        logger.error("Tentative de prédiction avec modèle non disponible")
        raise HTTPException(
            status_code=503,
            detail="Modèle non disponible. Vérifiez que le modèle est correctement chargé."
        )

    # Validation des données
    if data.debit_horaire < 0:
        raise HTTPException(status_code=400, detail="Le débit horaire doit être positif")
    if not (0 <= data.taux_occupation <= 100):
        raise HTTPException(status_code=400, detail="Le taux d'occupation doit être entre 0 et 100")
    if not (0 <= data.heure < 24):
        raise HTTPException(status_code=400, detail="L'heure doit être entre 0 et 24")

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
        prediction = str(y_pred[0])
        logger.info(f"Prédiction réussie: {prediction} pour route {data.numero_route}")
        return PredictionOutput(prediction=prediction)
    except ValueError as exc:
        logger.error(f"Erreur de validation: {exc}")
        raise HTTPException(status_code=400, detail=f"Données invalides: {exc}")
    except Exception as exc:
        logger.error(f"Erreur lors de la prédiction: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur interne: {exc}")

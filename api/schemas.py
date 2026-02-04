from pydantic import BaseModel

# Entrée pour /predict
class PredictionInput(BaseModel):
    identifiant_arc: int
    heure: float
    jour_semaine: int
    is_weekend: bool
    taux_occupation: float
    lat: float
    lon: float

# Sortie pour /predict
class PredictionOutput(BaseModel):
    prediction: str  # ou float si tu veux

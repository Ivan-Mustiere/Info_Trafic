from pydantic import BaseModel

# Entrée pour /predict
class PredictionInput(BaseModel):
    numero_route: int
    debit_horaire: float
    taux_occupation: float
    jour_semaine: int
    is_weekend: bool
    heure: float

# Sortie pour /predict
class PredictionOutput(BaseModel):
    prediction: str  # ou float si tu veux

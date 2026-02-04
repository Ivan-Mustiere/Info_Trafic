from pydantic import BaseModel

# Entrée pour le endpoint /predict
class PredictionInput(BaseModel):
    identifiant_arc: int
    heure: float
    jour_semaine: int
    is_weekend: bool
    taux_occupation: float
    lat: float
    lon: float

# Sortie du endpoint /predict
class PredictionOutput(BaseModel):
    prediction: str  # ou float si ton modèle renvoie un float directement

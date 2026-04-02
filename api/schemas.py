from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Entrée pour /predict
class PredictionInput(BaseModel):
    numero_route: int = Field(..., ge=0, description="Numéro de la route")
    debit_horaire: float = Field(..., ge=0, description="Débit horaire (véhicules/heure)")
    taux_occupation: float = Field(..., ge=0, le=100, description="Taux d'occupation (%)")
    jour_semaine: int = Field(..., ge=0, le=6, description="Jour de la semaine (0=lundi, 6=dimanche)")
    is_weekend: bool = Field(..., description="Indique si c'est un week-end")
    heure: float = Field(..., ge=0, lt=24, description="Heure de la journée (0-24)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "numero_route": 1,
                "debit_horaire": 1000.0,
                "taux_occupation": 5.0,
                "jour_semaine": 3,
                "is_weekend": False,
                "heure": 14.5
            }
        }

# Sortie pour /predict
class PredictionOutput(BaseModel):
    prediction: str = Field(..., description="État du trafic prédit")

from pydantic import BaseModel


class PredictionInput(BaseModel):
    """
    Schéma d'entrée pour la prédiction de l'état du trafic.
    Les champs correspondent aux features utilisées pendant le training.
    """

    identifiant_arc: int
    heure: int  # 0-23
    jour_semaine: int  # 0=lundi, 6=dimanche
    is_weekend: int  # 0 ou 1
    taux_occupation: float
    lat: float
    lon: float
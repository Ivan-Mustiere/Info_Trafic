import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
import joblib

from schemas import PredictionInput

# Ajouter le root directory pour les imports
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.training.deployment import ModelLoader, DeploymentStrategy, ModelRegistry
from utils.log_utils import logger

# Logger pour l'API
log = logger("API")

# Création de l'app FastAPI
app = FastAPI(title="Fil Rouge – API IA Trafic")

# Configuration du modèle
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")
DEPLOYMENT_STRATEGY = os.getenv("DEPLOYMENT_STRATEGY", "production").lower()

log.info(f"API démarrée avec MODEL_VERSION={MODEL_VERSION}, DEPLOYMENT_STRATEGY={DEPLOYMENT_STRATEGY}")

# Registre des modèles
registry = ModelRegistry()
log.info(f"Production version: {registry.get_production_version()}")
log.info(f"Available versions: {registry.get_available_versions()}")

# Charger le modèle
model = ModelLoader.load_model(MODEL_VERSION)
deployment_strategy = None

if model is None:
    log.error(f"❌ Impossible de charger le modèle {MODEL_VERSION}")
else:
    log.info(f"✅ Modèle {MODEL_VERSION} chargé avec succès")

# Initialiser la stratégie de déploiement si shadow ou canary
if DEPLOYMENT_STRATEGY in ["shadow", "canary"]:
    current_version = registry.get_production_version()
    new_version = MODEL_VERSION if MODEL_VERSION != current_version else "v2"
    try:
        deployment_strategy = DeploymentStrategy(current_version, new_version)
        log.info(f"✅ Stratégie de déploiement {DEPLOYMENT_STRATEGY} initialisée")
    except Exception as e:
        log.error(f"Erreur lors de l'initialisation de la stratégie: {e}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "deployment_strategy": DEPLOYMENT_STRATEGY,
    }


@app.get("/model-info")
def model_info():
    """Retourne les informations sur le modèle courant."""
    return {
        "current_version": MODEL_VERSION,
        "production_version": registry.get_production_version(),
        "available_versions": registry.get_available_versions(),
        "deployment_strategy": DEPLOYMENT_STRATEGY,
        "model_loaded": model is not None,
    }


@app.post("/predict")
def predict(data: PredictionInput):
    """
    Endpoint de prédiction d'état du trafic.
    Supporte différentes stratégies de déploiement:
    - production: Utilise le modèle en production (v1 ou v2)
    - shadow: Compare v1 et v2, mais retourne v1
    - canary: 10% trafic vers v2, 90% vers v1
    """
    if model is None:
        log.error("Modèle non disponible")
        raise HTTPException(status_code=503, detail="Modèle non disponible")

    try:
        # Construire les features dans le bon ordre
        X = [
            [
                data.identifiant_arc,
                data.heure,
                data.jour_semaine,
                data.is_weekend,
                data.taux_occupation,
                data.lat,
                data.lon,
            ]
        ]

        # Exécuter la prédiction selon la stratégie
        if DEPLOYMENT_STRATEGY == "shadow" and deployment_strategy:
            log.debug("Exécution en mode shadow deployment")
            pred_current, pred_shadow = deployment_strategy.shadow_deployment(X)
            if pred_current is None:
                raise Exception("Shadow deployment échoué")
            prediction = pred_current[0]
            meta = {"mode": "shadow", "shadow_available": pred_shadow is not None}

        elif DEPLOYMENT_STRATEGY == "canary" and deployment_strategy:
            log.debug("Exécution en mode canary deployment")
            result = deployment_strategy.canary_deployment(X, canary_percentage=0.1)
            if result is None:
                raise Exception("Canary deployment échoué")
            prediction = result["prediction"]
            meta = {
                "mode": "canary",
                "model_used": result["model_version"],
                "is_canary": result["canary"],
            }

        else:
            # Mode production simple
            log.debug(f"Exécution en mode production (version {MODEL_VERSION})")
            prediction = model.predict(X)
            prediction = prediction[0]
            meta = {"mode": "production", "model_version": MODEL_VERSION}

        log.info(f"Prédiction: {prediction} ({data.identifiant_arc})")

        return {
            "prediction": str(prediction),
            "model_version": MODEL_VERSION,
            "deployment_strategy": DEPLOYMENT_STRATEGY,
            "metadata": meta,
        }

    except Exception as e:
        log.error(f"Erreur lors de la prédiction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@app.post("/predict-batch")
def predict_batch(data_list: list):
    """
    Endpoint pour prédictions en batch.
    """
    if model is None:
        log.error("Modèle non disponible")
        raise HTTPException(status_code=503, detail="Modèle non disponible")

    try:
        predictions = []
        for data in data_list:
            X = [
                [
                    data.get("identifiant_arc"),
                    data.get("heure"),
                    data.get("jour_semaine"),
                    data.get("is_weekend"),
                    data.get("taux_occupation"),
                    data.get("lat"),
                    data.get("lon"),
                ]
            ]
            pred = model.predict(X)[0]
            predictions.append({
                "arc_id": data.get("identifiant_arc"),
                "prediction": str(pred),
            })

        log.info(f"Batch de {len(predictions)} prédictions effectuées")
        return {
            "predictions": predictions,
            "count": len(predictions),
            "model_version": MODEL_VERSION,
        }

    except Exception as e:
        log.error(f"Erreur lors des prédictions batch: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

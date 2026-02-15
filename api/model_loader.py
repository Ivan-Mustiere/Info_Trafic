from pathlib import Path
import joblib
import logging

logger = logging.getLogger(__name__)

# Chemin vers le modèle
MODEL_PATH = "/app/models/model.joblib"

try:
    model = joblib.load(MODEL_PATH)
    logger.info(f"✅ Modèle chargé depuis {MODEL_PATH}")
except FileNotFoundError:
    logger.error(f"⚠️ Modèle non trouvé à {MODEL_PATH}. Les prédictions ne fonctionneront pas.")
    model = None
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
    model = None

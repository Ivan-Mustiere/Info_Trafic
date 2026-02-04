from pathlib import Path
import joblib

# Chemin vers le modèle
MODEL_PATH = "/app/models/model.joblib"

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modèle chargé depuis {MODEL_PATH}")
except FileNotFoundError:
    print(f"⚠️ Modèle non trouvé à {MODEL_PATH}. Les prédictions ne fonctionneront pas.")
    model = None

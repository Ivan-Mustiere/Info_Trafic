
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from utils.log_utils import logger

# Répertoires du projet
ROOT_DIR = Path(__file__).resolve().parents[2]   # remonte de src/training/train.py -> src -> racine projet
DATA_DIR = ROOT_DIR / "data" / "processed"
MODEL_DIR = ROOT_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# Logger spécifique pour le training
log = logger("Training")

def load_data():
    df = pd.read_csv(DATA_DIR / "dataset_processed.csv")
    # Supprimer les lignes avec target Inconnu
    df = df[df["Etat trafic"] != "Inconnu"]
    return df

def split_features_target(df):
    features = [
        "Identifiant arc",
        "heure",
        "jour_semaine",
        "is_weekend",
        "Taux d'occupation",
        "lat",
        "lon",
    ]

    df = df.dropna(subset=features + ["Etat trafic"])
    X = df[features]
    y = df["Etat trafic"]

    return X, y

def main():
    log.info("🤖 Démarrage du training du modèle de trafic...")

    df = load_data()
    log.info(f"Dataset chargé depuis {DATA_DIR / 'dataset_processed.csv'} (shape={df.shape})")

    X, y = split_features_target(df)
    log.info(f"Features et target préparées (X.shape={X.shape}, y.shape={y.shape})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Pipeline = StandardScaler + Régression Logistique
    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=5000)),
        ]
    )

    log.info("Entraînement de la pipeline (StandardScaler + LogisticRegression)...")
    pipeline.fit(X_train, y_train)
    log.info("Entraînement terminé.")

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    log.info(f"Accuracy : {accuracy:.3f}")

    report = classification_report(y_test, y_pred)
    log.info("Classification report :\n" + report)

    # On sauvegarde toute la pipeline (scaler + modèle) pour le serving
    model_path = MODEL_DIR / "model.joblib"
    joblib.dump(pipeline, model_path)
    log.info(f"💾 Modèle sauvegardé dans {model_path}")

if __name__ == "__main__":
    main()

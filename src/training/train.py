import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from joblib import dump
from utils.log_utils import logger
from utils.file_utils import read_csv  # Utilisation de file_utils

container_name = os.getenv("CONTAINER_NAME", "default_logger")
log = logger(container_name)

PROCESSED_DIR = "/app/processed"
MODELS_DIR = "/app/models"

# Création du dossier modèle si nécessaire
os.makedirs(MODELS_DIR, exist_ok=True)

def main():
    # Récupération automatique du fichier CSV dans le dossier processed
    files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".csv")]
    if not files:
        raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {PROCESSED_DIR}")
    processed_path = os.path.join(PROCESSED_DIR, files[0])
    model_path = os.path.join(MODELS_DIR, "model.joblib")

    # Chargement des données
    log.info(f"Chargement des données depuis le fichier : {processed_path}")
    data = read_csv(processed_path)
    log.info(f"Dataset chargé avec {data.shape[0]} lignes et {data.shape[1]} colonnes.")

    # Séparation features / target
    target_column = "Etat trafic"
    if target_column not in data.columns:
        raise ValueError(f"Colonne cible '{target_column}' non trouvée dans le dataset.")
    X = data.drop(columns=[target_column])
    y = data[target_column]
    log.info(f"Features et target séparés. Nombre de features : {X.shape[1]}.")

    # Split train/test
    random_state = 42
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )
    log.info(f"Split train/test effectué : {X_train.shape[0]} lignes pour l'entraînement, {X_test.shape[0]} pour le test.")

    # Entraînement du modèle
    model_type = "RandomForest"  # Ou "LogisticRegression"
    if model_type == "RandomForest":
        model = RandomForestClassifier(random_state=random_state)
    elif model_type == "LogisticRegression":
        model = LogisticRegression(random_state=random_state, max_iter=1000)
    else:
        raise ValueError("Modèle non supporté.")
    
    log.info(f"Entraînement du modèle {model_type}.")
    model.fit(X_train, y_train)
    log.info("Modèle entraîné avec succès.")

    # Évaluation du modèle
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    log.info(f"Accuracy : {accuracy:.4f}, F1-score : {f1:.4f}")

    # Sauvegarde du modèle
    dump(model, model_path)
    log.info(f"Modèle sauvegardé à l'emplacement : {model_path}")


if __name__ == "__main__":
    main()

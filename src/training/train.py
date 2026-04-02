import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from joblib import dump
from utils.log_utils import logger
from utils.file_utils import read_csv, write_json
import numpy as np

container_name = os.getenv("CONTAINER_NAME", "default_logger")
log = logger(container_name)

PROCESSED_DIR = "/app/processed"
MODELS_DIR = "/app/models"

# Configuration via variables d'environnement
MODEL_TYPE = os.getenv("MODEL_TYPE", "RandomForest")
TEST_SIZE = float(os.getenv("TEST_SIZE", "0.2"))
RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))
N_ESTIMATORS = int(os.getenv("N_ESTIMATORS", "100"))  # Pour RandomForest
MAX_DEPTH = int(os.getenv("MAX_DEPTH", "10")) if os.getenv("MAX_DEPTH") else None

# Création du dossier modèle si nécessaire
os.makedirs(MODELS_DIR, exist_ok=True)

def main():
    try:
        # Récupération automatique du fichier CSV dans le dossier processed
        files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".csv")]
        if not files:
            raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {PROCESSED_DIR}")
        processed_path = os.path.join(PROCESSED_DIR, files[0])
        model_path = os.path.join(MODELS_DIR, "model.joblib")
        metrics_path = os.path.join(MODELS_DIR, "metrics.json")

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
        log.info(f"Distribution des classes: {dict(y.value_counts())}")

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        log.info(f"Split train/test effectué : {X_train.shape[0]} lignes pour l'entraînement, {X_test.shape[0]} pour le test.")

        # Entraînement du modèle
        log.info(f"Configuration: MODEL_TYPE={MODEL_TYPE}, RANDOM_STATE={RANDOM_STATE}, TEST_SIZE={TEST_SIZE}")
        
        if MODEL_TYPE == "RandomForest":
            model = RandomForestClassifier(
                n_estimators=N_ESTIMATORS,
                max_depth=MAX_DEPTH,
                random_state=RANDOM_STATE,
                n_jobs=-1
            )
            log.info(f"RandomForest configuré: n_estimators={N_ESTIMATORS}, max_depth={MAX_DEPTH}")
        elif MODEL_TYPE == "LogisticRegression":
            model = LogisticRegression(random_state=RANDOM_STATE, max_iter=1000, n_jobs=-1)
        else:
            raise ValueError(f"Modèle non supporté: {MODEL_TYPE}")
        
        log.info(f"Entraînement du modèle {MODEL_TYPE}...")
        model.fit(X_train, y_train)
        log.info("✅ Modèle entraîné avec succès.")

        # Évaluation du modèle
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        test_f1 = f1_score(y_test, y_pred_test, average="weighted")
        
        log.info(f"Train Accuracy : {train_accuracy:.4f}")
        log.info(f"Test Accuracy  : {test_accuracy:.4f}")
        log.info(f"Test F1-score  : {test_f1:.4f}")
        
        # Métriques détaillées
        log.info("\nRapport de classification:")
        report = classification_report(y_test, y_pred_test, output_dict=True)
        log.info(classification_report(y_test, y_pred_test))
        
        # Matrice de confusion
        conf_matrix = confusion_matrix(y_test, y_pred_test)
        log.info(f"\nMatrice de confusion:\n{conf_matrix}")
        
        # Importance des features (si disponible)
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(X.columns, model.feature_importances_))
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            log.info("\nImportance des features (top 5):")
            for feat, imp in sorted_features[:5]:
                log.info(f"  {feat}: {imp:.4f}")

        # Sauvegarde des métriques
        metrics = {
            "model_type": MODEL_TYPE,
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "test_f1_score": float(test_f1),
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "n_samples_train": int(X_train.shape[0]),
            "n_samples_test": int(X_test.shape[0]),
            "n_features": int(X.shape[1]),
            "classification_report": report
        }
        
        if hasattr(model, 'feature_importances_'):
            metrics["feature_importance"] = {k: float(v) for k, v in feature_importance.items()}
        
        write_json(metrics, metrics_path)
        log.info(f"Métriques sauvegardées à : {metrics_path}")

        # Sauvegarde du modèle
        dump(model, model_path)
        log.info(f"✅ Modèle sauvegardé à l'emplacement : {model_path}")
        
    except FileNotFoundError as e:
        log.error(f"❌ Fichier non trouvé: {e}")
        raise
    except ValueError as e:
        log.error(f"❌ Erreur de validation: {e}")
        raise
    except Exception as e:
        log.error(f"❌ Erreur inattendue lors de l'entraînement: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

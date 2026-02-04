"""
train_v2.py - Training script pour modèle v2 du prédicteur de trafic.

Objectif : Entraîner un modèle reproductible et versionnée avec:
- Preprocessing complet (imputation NA, encoding, scaling)
- Pipeline scikit-learn
- Sauvegarde des artefacts (model, metrics, params, schema)
- Logging détaillé
"""

import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Ajouter le parent directory pour les imports
ROOT_DIR = Path(__file__).resolve().parents[2]  # src/training -> src -> racine
sys.path.insert(0, str(ROOT_DIR))

from utils.log_utils import logger

# Logger pour le training
log = logger("Training_V2")

# Configuration
DATA_DIR = ROOT_DIR / "data" / "processed"
ARTIFACTS_DIR = ROOT_DIR / "artifacts" / "v2"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Seed pour reproductibilité
RANDOM_STATE = 42
TEST_SIZE = 0.2
MODEL_PARAMS = {
    "algorithm": "RandomForest",
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": RANDOM_STATE,
}


def load_data(dataset_path: Path) -> pd.DataFrame:
    """
    Charge le dataset depuis un CSV ou Parquet.

    Args:
        dataset_path: Chemin vers le fichier de données

    Returns:
        DataFrame chargé
    """
    log.info(f"📂 Chargement du dataset depuis {dataset_path}...")

    if not dataset_path.exists():
        log.error(f"Fichier non trouvé: {dataset_path}")
        raise FileNotFoundError(f"Dataset introuvable: {dataset_path}")

    try:
        if dataset_path.suffix == ".csv":
            df = pd.read_csv(dataset_path)
        elif dataset_path.suffix == ".parquet":
            df = pd.read_parquet(dataset_path)
        else:
            raise ValueError(f"Format non supporté: {dataset_path.suffix}")

        log.info(f"✅ Dataset chargé (shape={df.shape})")
        log.info(f"   Colonnes: {list(df.columns)}")
        return df

    except Exception as e:
        log.error(f"Erreur lors du chargement: {e}")
        raise


def prepare_features_and_target(
    df: pd.DataFrame,
    feature_columns: list,
    target_column: str,
) -> tuple:
    """
    Prépare les features (X) et la target (y).

    Args:
        df: DataFrame
        feature_columns: Liste des colonnes de features
        target_column: Nom de la colonne cible

    Returns:
        (X, y, feature_names)
    """
    log.info(f"🔧 Préparation des features et target...")
    log.info(f"   Features: {feature_columns}")
    log.info(f"   Target: {target_column}")

    # Supprimer les lignes avec target inconnue ou invalide
    if target_column in df.columns:
        initial_rows = len(df)
        df = df[df[target_column] != "Inconnu"]
        df = df.dropna(subset=[target_column])
        log.info(f"   Lignes après suppression des 'Inconnu': {len(df)} (supprimées: {initial_rows - len(df)})")

    # Supprimer les lignes avec NA dans features ou target
    df = df.dropna(subset=feature_columns + [target_column])
    log.info(f"   Lignes après suppression des NA: {len(df)}")

    X = df[feature_columns].copy()
    y = df[target_column].copy()

    log.info(f"✅ Features et target préparées (X.shape={X.shape}, y.shape={y.shape})")
    return X, y, feature_columns


def create_preprocessing_pipeline(feature_columns: list) -> Pipeline:
    """
    Crée un pipeline de preprocessing.

    Args:
        feature_columns: Liste des noms des features

    Returns:
        Pipeline scikit-learn
    """
    log.info("🔨 Création du pipeline de preprocessing...")

    # Pipeline simple: StandardScaler (assume que les features sont numériques)
    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
        ]
    )

    log.info("✅ Pipeline créé: StandardScaler")
    return pipeline


def create_model_pipeline(
    preprocessing_pipeline: Pipeline,
    model_params: dict,
) -> Pipeline:
    """
    Crée le pipeline complet (preprocessing + modèle).

    Args:
        preprocessing_pipeline: Pipeline de preprocessing
        model_params: Paramètres du modèle

    Returns:
        Pipeline complet
    """
    log.info("🤖 Création du pipeline de modèle...")

    # Extraire les étapes du preprocessing
    preprocessing_steps = preprocessing_pipeline.steps.copy()

    # Ajouter le modèle
    if model_params["algorithm"] == "RandomForest":
        preprocessing_steps.append(
            (
                "model",
                RandomForestClassifier(
                    n_estimators=model_params["n_estimators"],
                    max_depth=model_params["max_depth"],
                    min_samples_split=model_params["min_samples_split"],
                    min_samples_leaf=model_params["min_samples_leaf"],
                    random_state=model_params["random_state"],
                    n_jobs=-1,
                    verbose=1,
                ),
            )
        )
    else:
        raise ValueError(f"Algorithme non supporté: {model_params['algorithm']}")

    full_pipeline = Pipeline(steps=preprocessing_steps)
    log.info(f"✅ Pipeline modèle créé: {[step[0] for step in full_pipeline.steps]}")
    return full_pipeline


def train_model(
    pipeline: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> Pipeline:
    """
    Entraîne le modèle.

    Args:
        pipeline: Pipeline scikit-learn
        X_train: Features d'entraînement
        y_train: Target d'entraînement

    Returns:
        Pipeline entraîné
    """
    log.info("🚀 Début de l'entraînement du modèle...")
    log.info(f"   Dataset d'entraînement: X_train.shape={X_train.shape}, y_train.shape={y_train.shape}")

    try:
        pipeline.fit(X_train, y_train)
        log.info("✅ Entraînement terminé avec succès")
        return pipeline
    except Exception as e:
        log.error(f"Erreur lors de l'entraînement: {e}")
        raise


def evaluate_model(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """
    Évalue le modèle et retourne les métriques.

    Args:
        pipeline: Pipeline entraîné
        X_test: Features de test
        y_test: Target de test

    Returns:
        Dictionnaire des métriques
    """
    log.info("📊 Évaluation du modèle...")

    y_pred = pipeline.predict(X_test)

    # Calcul des métriques
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    # Matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    cm_list = cm.tolist()

    # Classification report
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": cm_list,
        "classification_report": report,
        "test_size": len(X_test),
    }

    log.info(f"✅ Métriques calculées:")
    log.info(f"   Accuracy:  {metrics['accuracy']:.4f}")
    log.info(f"   Precision: {metrics['precision']:.4f}")
    log.info(f"   Recall:    {metrics['recall']:.4f}")
    log.info(f"   F1-Score:  {metrics['f1']:.4f}")

    return metrics


def save_artifacts(
    pipeline: Pipeline,
    metrics: dict,
    model_params: dict,
    feature_columns: list,
    output_dir: Path,
) -> None:
    """
    Sauvegarde tous les artefacts (modèle, métriques, params, schéma).

    Args:
        pipeline: Pipeline entraîné
        metrics: Dictionnaire des métriques
        model_params: Paramètres du modèle
        feature_columns: Noms des features
        output_dir: Répertoire de sortie
    """
    log.info(f"💾 Sauvegarde des artefacts dans {output_dir}...")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sauvegarder le modèle
    model_path = output_dir / "model.joblib"
    joblib.dump(pipeline, model_path)
    log.info(f"   ✅ Modèle sauvegardé: {model_path}")

    # 2. Sauvegarder les métriques
    metrics_path = output_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    log.info(f"   ✅ Métriques sauvegardées: {metrics_path}")

    # 3. Sauvegarder les paramètres
    params_path = output_dir / "params.json"
    with open(params_path, "w") as f:
        json.dump(model_params, f, indent=2)
    log.info(f"   ✅ Paramètres sauvegardés: {params_path}")

    # 4. Sauvegarder le schéma (features)
    schema = {
        "features": feature_columns,
        "num_features": len(feature_columns),
        "random_state": RANDOM_STATE,
    }
    schema_path = output_dir / "schema.json"
    with open(schema_path, "w") as f:
        json.dump(schema, f, indent=2)
    log.info(f"   ✅ Schéma sauvegardé: {schema_path}")


def main(
    dataset_path: str = None,
    feature_columns: list = None,
    target_column: str = "Etat trafic",
):
    """
    Fonction principale pour entraîner le modèle v2.

    Args:
        dataset_path: Chemin vers le dataset (par défaut: data/processed/dataset_processed.csv)
        feature_columns: Colonnes de features (par défaut: cf. ci-dessous)
        target_column: Nom de la colonne cible
    """
    log.info("=" * 80)
    log.info("🎯 TRAINING DU MODÈLE V2 - DÉMARRAGE")
    log.info("=" * 80)

    # Configuration par défaut
    if dataset_path is None:
        dataset_path = DATA_DIR / "dataset_processed.csv"
    else:
        dataset_path = Path(dataset_path)

    if feature_columns is None:
        feature_columns = [
            "Identifiant arc",
            "heure",
            "jour_semaine",
            "is_weekend",
            "Taux d'occupation",
            "lat",
            "lon",
        ]

    try:
        # 1. Charger les données
        df = load_data(dataset_path)

        # 2. Préparer X et y
        X, y, features = prepare_features_and_target(df, feature_columns, target_column)

        # 3. Diviser en train/test
        log.info(f"🔀 Division train/test (test_size={TEST_SIZE}, random_state={RANDOM_STATE})...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        log.info(f"   ✅ X_train: {X_train.shape}, X_test: {X_test.shape}")

        # 4. Créer le pipeline de preprocessing
        preprocessing_pipeline = create_preprocessing_pipeline(features)

        # 5. Créer le pipeline complet
        full_pipeline = create_model_pipeline(preprocessing_pipeline, MODEL_PARAMS)

        # 6. Entraîner
        trained_pipeline = train_model(full_pipeline, X_train, y_train)

        # 7. Évaluer
        metrics = evaluate_model(trained_pipeline, X_test, y_test)

        # 8. Sauvegarder les artefacts
        save_artifacts(
            trained_pipeline,
            metrics,
            MODEL_PARAMS,
            features,
            ARTIFACTS_DIR,
        )

        log.info("=" * 80)
        log.info("✅ TRAINING V2 COMPLÉTÉ AVEC SUCCÈS")
        log.info("=" * 80)

        return trained_pipeline, metrics

    except Exception as e:
        log.error("=" * 80)
        log.error(f"❌ ERREUR LORS DU TRAINING V2: {e}")
        log.error("=" * 80)
        raise


if __name__ == "__main__":
    main()

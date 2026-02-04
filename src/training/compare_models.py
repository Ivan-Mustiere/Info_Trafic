"""
compare_models.py - Comparaison des modèles v1 vs v2.

Script pour charger les métriques de v1 et v2, générer un tableau comparatif
et fournir des recommandations de déploiement.
"""

import json
import sys
from pathlib import Path

import pandas as pd

# Ajouter le parent directory pour les imports
ROOT_DIR = Path(__file__).resolve().parents[2]  # src/training -> src -> racine
sys.path.insert(0, str(ROOT_DIR))

from utils.log_utils import logger

# Logger pour la comparaison
log = logger("Model_Comparison")

ARTIFACTS_DIR = ROOT_DIR / "artifacts"


def load_metrics(version: str) -> dict:
    """
    Charge les métriques d'une version de modèle.

    Args:
        version: "v1" ou "v2"

    Returns:
        Dictionnaire des métriques
    """
    metrics_path = ARTIFACTS_DIR / version / "metrics.json"

    if not metrics_path.exists():
        log.warning(f"⚠️  Fichier de métriques non trouvé pour {version}: {metrics_path}")
        return None

    try:
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        log.info(f"✅ Métriques de {version} chargées depuis {metrics_path}")
        return metrics
    except Exception as e:
        log.error(f"Erreur lors du chargement des métriques de {version}: {e}")
        return None


def load_params(version: str) -> dict:
    """
    Charge les paramètres d'une version de modèle.

    Args:
        version: "v1" ou "v2"

    Returns:
        Dictionnaire des paramètres
    """
    params_path = ARTIFACTS_DIR / version / "params.json"

    if not params_path.exists():
        log.warning(f"⚠️  Fichier de paramètres non trouvé pour {version}: {params_path}")
        return None

    try:
        with open(params_path, "r") as f:
            params = json.load(f)
        log.info(f"✅ Paramètres de {version} chargés")
        return params
    except Exception as e:
        log.error(f"Erreur lors du chargement des paramètres de {version}: {e}")
        return None


def create_comparison_table(metrics_v1: dict, metrics_v2: dict) -> pd.DataFrame:
    """
    Crée un tableau de comparaison des métriques.

    Args:
        metrics_v1: Métriques du modèle v1
        metrics_v2: Métriques du modèle v2

    Returns:
        DataFrame pandas
    """
    log.info("📊 Création du tableau de comparaison...")

    comparison_data = {
        "Métrique": ["Accuracy", "Precision", "Recall", "F1-Score"],
        "v1": [
            metrics_v1.get("accuracy", "N/A") if metrics_v1 else "N/A",
            metrics_v1.get("precision", "N/A") if metrics_v1 else "N/A",
            metrics_v1.get("recall", "N/A") if metrics_v1 else "N/A",
            metrics_v1.get("f1", "N/A") if metrics_v1 else "N/A",
        ],
        "v2": [
            metrics_v2.get("accuracy", "N/A"),
            metrics_v2.get("precision", "N/A"),
            metrics_v2.get("recall", "N/A"),
            metrics_v2.get("f1", "N/A"),
        ],
    }

    df_comparison = pd.DataFrame(comparison_data)

    # Ajouter colonne de différence si les deux versions existent
    if metrics_v1 and metrics_v2:
        differences = []
        for metric_key in ["accuracy", "precision", "recall", "f1"]:
            v1_val = metrics_v1.get(metric_key, 0)
            v2_val = metrics_v2.get(metric_key, 0)
            if isinstance(v1_val, (int, float)) and isinstance(v2_val, (int, float)):
                diff = v2_val - v1_val
                differences.append(f"{diff:+.4f}")
            else:
                differences.append("N/A")

        df_comparison["Δ (v2-v1)"] = differences

    return df_comparison


def get_recommendation(metrics_v1: dict, metrics_v2: dict) -> dict:
    """
    Génère une recommandation de déploiement basée sur la comparaison.

    Args:
        metrics_v1: Métriques du modèle v1
        metrics_v2: Métriques du modèle v2

    Returns:
        Dictionnaire avec recommandation et justification
    """
    log.info("🎯 Analyse des recommandations de déploiement...")

    if not metrics_v1:
        log.warning("v1 non disponible, recommandation basée sur v2 seul")
        return {
            "recommendation": "canary",
            "justification": "v1 non disponible. Utiliser une stratégie canary pour tester v2",
            "strategy": "canary",
            "confidence": "low",
        }

    if not metrics_v2:
        log.warning("v2 non disponible")
        return {
            "recommendation": "keep_v1",
            "justification": "v2 non disponible. Maintenir v1",
            "strategy": None,
            "confidence": "high",
        }

    # Comparaison des métriques principales
    f1_diff = metrics_v2["f1"] - metrics_v1["f1"]
    accuracy_diff = metrics_v2["accuracy"] - metrics_v1["accuracy"]

    # Seuils de décision
    IMPROVEMENT_THRESHOLD = 0.01  # 1% d'amélioration minimum
    DEGRADATION_THRESHOLD = -0.02  # Pas plus de 2% de dégradation tolérée

    if f1_diff > IMPROVEMENT_THRESHOLD and accuracy_diff > DEGRADATION_THRESHOLD:
        recommendation = {
            "recommendation": "promote_to_shadow",
            "justification": f"v2 améliore F1 de {f1_diff:.4f}. Commencer par shadow deployment.",
            "strategy": "shadow",
            "confidence": "high",
            "f1_improvement": f1_diff,
            "accuracy_change": accuracy_diff,
        }
    elif accuracy_diff > DEGRADATION_THRESHOLD and f1_diff > DEGRADATION_THRESHOLD:
        recommendation = {
            "recommendation": "test_canary",
            "justification": f"Légères variations. Tester avec canary (F1: {f1_diff:+.4f}, Accuracy: {accuracy_diff:+.4f}).",
            "strategy": "canary",
            "confidence": "medium",
            "f1_improvement": f1_diff,
            "accuracy_change": accuracy_diff,
        }
    else:
        recommendation = {
            "recommendation": "rollback",
            "justification": f"v2 dégrade les performances (F1: {f1_diff:+.4f}). Rollback recommandé.",
            "strategy": "rollback",
            "confidence": "high",
            "f1_improvement": f1_diff,
            "accuracy_change": accuracy_diff,
        }

    return recommendation


def main():
    """
    Fonction principale pour comparer les modèles v1 et v2.
    """
    log.info("=" * 80)
    log.info("📊 COMPARAISON DES MODÈLES V1 VS V2 - DÉMARRAGE")
    log.info("=" * 80)

    # Charger les métriques
    log.info("\n🔍 Chargement des métriques...")
    metrics_v1 = load_metrics("v1")
    metrics_v2 = load_metrics("v2")

    if not metrics_v2:
        log.error("Impossible de charger les métriques de v2. Arrêt.")
        return

    # Charger les paramètres
    log.info("\n🔍 Chargement des paramètres...")
    params_v1 = load_params("v1")
    params_v2 = load_params("v2")

    # Créer le tableau de comparaison
    log.info("\n" + "=" * 80)
    log.info("📋 TABLEAU COMPARATIF")
    log.info("=" * 80)

    df_comparison = create_comparison_table(metrics_v1, metrics_v2)
    print("\n" + df_comparison.to_string(index=False))

    # Afficher les paramètres
    if params_v1 or params_v2:
        log.info("\n" + "=" * 80)
        log.info("⚙️  PARAMÈTRES DES MODÈLES")
        log.info("=" * 80)

        if params_v1:
            log.info("\nv1 Paramètres:")
            for key, value in params_v1.items():
                log.info(f"  {key}: {value}")

        if params_v2:
            log.info("\nv2 Paramètres:")
            for key, value in params_v2.items():
                log.info(f"  {key}: {value}")

    # Recommandations de déploiement
    log.info("\n" + "=" * 80)
    log.info("🎯 RECOMMANDATIONS DE DÉPLOIEMENT")
    log.info("=" * 80)

    recommendation = get_recommendation(metrics_v1, metrics_v2)
    log.info(f"\nStratégie recommandée: {recommendation['recommendation']}")
    log.info(f"Justification: {recommendation['justification']}")
    log.info(f"Stratégie de déploiement: {recommendation['strategy']}")
    log.info(f"Confiance: {recommendation['confidence']}")

    if "f1_improvement" in recommendation:
        log.info(f"Amélioration F1: {recommendation['f1_improvement']:+.4f}")
        log.info(f"Changement Accuracy: {recommendation['accuracy_change']:+.4f}")

    # Sauvegarder le rapport de comparaison
    log.info("\n" + "=" * 80)
    log.info("💾 SAUVEGARDE DU RAPPORT")
    log.info("=" * 80)

    comparison_report = {
        "metrics_comparison": df_comparison.to_dict("records"),
        "recommendation": recommendation,
        "params_v1": params_v1,
        "params_v2": params_v2,
    }

    report_path = ARTIFACTS_DIR / "comparison_report.json"
    with open(report_path, "w") as f:
        json.dump(comparison_report, f, indent=2)
    log.info(f"✅ Rapport sauvegardé: {report_path}")

    log.info("\n" + "=" * 80)
    log.info("✅ COMPARAISON COMPLÉTÉE")
    log.info("=" * 80)

    return comparison_report


if __name__ == "__main__":
    main()

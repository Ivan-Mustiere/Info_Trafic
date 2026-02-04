#!/usr/bin/env python
"""
exemple_utilisation.py - Exemples d'utilisation des scripts de training et déploiement
"""

import sys
from pathlib import Path

# Ajouter le parent directory pour les imports
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.training.train_v2 import main as train_v2
from src.training.compare_models import main as compare_models
from src.training.deployment import ModelRegistry, DeploymentStrategy, ModelLoader
from src.utils.log_utils import logger

log = logger("Examples")


def exemple_1_entraiment_simple():
    """Exemple 1: Entraîner un modèle v2 simple"""
    log.info("\n" + "=" * 80)
    log.info("EXEMPLE 1: Entraînement simple du modèle v2")
    log.info("=" * 80)

    log.info("\n1. Entraîner v2...")
    try:
        model, metrics = train_v2()
        log.info(f"✅ Modèle entraîné avec F1={metrics['f1']:.4f}")
    except Exception as e:
        log.error(f"Erreur: {e}")


def exemple_2_comparaison():
    """Exemple 2: Comparer v1 et v2"""
    log.info("\n" + "=" * 80)
    log.info("EXEMPLE 2: Comparaison v1 vs v2")
    log.info("=" * 80)

    log.info("\n1. Charger les métriques...")
    metrics_v1 = ModelLoader.load_metrics("v1")
    metrics_v2 = ModelLoader.load_metrics("v2")

    log.info(f"v1 F1-Score: {metrics_v1['f1']:.4f}")
    log.info(f"v2 F1-Score: {metrics_v2['f1']:.4f}")

    improvement = metrics_v2["f1"] - metrics_v1["f1"]
    log.info(f"Amélioration: {improvement:+.4f}")

    log.info("\n2. Générer rapport de comparaison...")
    try:
        compare_models()
    except Exception as e:
        log.error(f"Erreur: {e}")


def exemple_3_shadow_deployment():
    """Exemple 3: Shadow deployment"""
    log.info("\n" + "=" * 80)
    log.info("EXEMPLE 3: Shadow Deployment")
    log.info("=" * 80)

    log.info("\n1. Initialiser la stratégie shadow...")
    strategy = DeploymentStrategy(current_version="v1", new_version="v2")

    log.info("\n2. Simuler une prédiction...")
    # Sample de données
    X_sample = [[12345, 10, 2, 0, 0.75, 48.8566, 2.3522]]

    log.info("   Exécution shadow (v1 + v2 parallèle)...")
    pred_v1, pred_v2 = strategy.shadow_deployment(X_sample)

    if pred_v1 and pred_v2:
        log.info(f"   v1 prédiction: {pred_v1[0]}")
        log.info(f"   v2 prédiction (shadow): {pred_v2[0]}")
        if pred_v1[0] == pred_v2[0]:
            log.info("   ✅ Prédictions concordantes")
        else:
            log.warning("   ⚠️ Divergence détectée!")


def exemple_4_canary_deployment():
    """Exemple 4: Canary deployment (10% trafic)"""
    log.info("\n" + "=" * 80)
    log.info("EXEMPLE 4: Canary Deployment")
    log.info("=" * 80)

    log.info("\n1. Initialiser la stratégie canary...")
    strategy = DeploymentStrategy(current_version="v1", new_version="v2")

    log.info("\n2. Simuler 10 prédictions avec canary (10% → v2)...")
    X_sample = [[12345, 10, 2, 0, 0.75, 48.8566, 2.3522]]

    v2_count = 0
    for i in range(10):
        result = strategy.canary_deployment(X_sample, canary_percentage=0.1)
        if result and result["canary"]:
            v2_count += 1
        log.info(f"   Prédiction {i+1}: {result['model_version']}")

    log.info(f"\n   Résumé: {v2_count}/10 vers v2 (attendu ~1)")


def exemple_5_model_registry():
    """Exemple 5: Gestion du registry"""
    log.info("\n" + "=" * 80)
    log.info("EXEMPLE 5: Model Registry")
    log.info("=" * 80)

    log.info("\n1. Charger le registry...")
    registry = ModelRegistry()

    log.info(f"   Production version: {registry.get_production_version()}")
    log.info(f"   Available versions: {registry.get_available_versions()}")

    log.info("\n2. Enregistrer v2...")
    registry.register_new_version("v2")
    log.info(f"   Versions disponibles: {registry.get_available_versions()}")

    log.info("\n3. Promouvoir v2 en production...")
    registry.promote_to_production("v2")
    log.info(f"   Production version: {registry.get_production_version()}")

    log.info("\n4. Sauvegarder le registry...")
    registry.save_registry()
    log.info("   ✅ Registry sauvegardé")


def exemple_6_full_pipeline():
    """Exemple 6: Pipeline complet"""
    log.info("\n" + "=" * 80)
    log.info("EXEMPLE 6: Full Pipeline (train + compare + deploy)")
    log.info("=" * 80)

    try:
        # 1. Train v2
        log.info("\n[1/4] Entraînement v2...")
        model, metrics = train_v2()
        log.info("✅ v2 entraîné")

        # 2. Compare v1 vs v2
        log.info("\n[2/4] Comparaison v1 vs v2...")
        compare_models()
        log.info("✅ Comparaison effectuée")

        # 3. Gestion du registry
        log.info("\n[3/4] Mise à jour du registry...")
        registry = ModelRegistry()
        registry.register_new_version("v2")
        log.info("✅ v2 enregistré")

        # 4. Shadow deployment
        log.info("\n[4/4] Shadow deployment...")
        strategy = DeploymentStrategy(current_version="v1", new_version="v2")
        X = [[12345, 10, 2, 0, 0.75, 48.8566, 2.3522]]
        pred_v1, pred_v2 = strategy.shadow_deployment(X)
        log.info("✅ Shadow deployment actif")

        log.info("\n" + "=" * 80)
        log.info("✅ PIPELINE COMPLET TERMINÉ")
        log.info("=" * 80)

    except Exception as e:
        log.error(f"Erreur dans le pipeline: {e}")


if __name__ == "__main__":
    log.info("=" * 80)
    log.info("EXEMPLES D'UTILISATION - Training et Déploiement")
    log.info("=" * 80)

    # Exemples à décommenter pour exécuter
    exemple_1_entraiment_simple()
    exemple_2_comparaison()
    exemple_3_shadow_deployment()
    exemple_4_canary_deployment()
    exemple_5_model_registry()
    exemple_6_full_pipeline()

    log.info("\n" + "=" * 80)
    log.info("✅ TOUS LES EXEMPLES COMPLÉTÉS")
    log.info("=" * 80)
    log.info("\nVérifier les logs dans: /app/logs/")
    log.info("Artefacts dans: artifacts/v1/, artifacts/v2/, artifacts/registry.json")

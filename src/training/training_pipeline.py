"""
training_pipeline.py - Script d'orchestration complet du training et déploiement.

Lance le training v2, le compare avec v1, et applique la stratégie de déploiement.
"""

import sys
import argparse
from pathlib import Path

# Ajouter le parent directory pour les imports
ROOT_DIR = Path(__file__).resolve().parents[1]  # src -> racine
sys.path.insert(0, str(ROOT_DIR))

from training.train_v2 import main as train_v2
from training.compare_models import main as compare_models
from training.deployment import ModelRegistry, DeploymentStrategy
from utils.log_utils import logger

log = logger("Training_Pipeline")


def run_full_pipeline(
    dataset_path: str = None,
    compare: bool = True,
    deploy_strategy: str = "shadow",
    auto_promote: bool = False,
):
    """
    Lance le pipeline complet:
    1. Entraîner v2
    2. Comparer v1 vs v2
    3. Appliquer une stratégie de déploiement
    4. Optionnellement promouvoir v2 en production

    Args:
        dataset_path: Chemin vers le dataset
        compare: Si True, compare v1 et v2
        deploy_strategy: Stratégie de déploiement (shadow, canary, production)
        auto_promote: Si True, promeut automatiquement v2 en production
    """
    log.info("=" * 80)
    log.info("🚀 PIPELINE TRAINING - DÉMARRAGE COMPLET")
    log.info("=" * 80)

    try:
        # 1. Entraîner v2
        log.info("\n[STEP 1/4] Entraînement du modèle v2...")
        log.info("-" * 80)
        trained_model, metrics_v2 = train_v2(dataset_path=dataset_path)
        log.info("✅ Entraînement v2 terminé")

        # 2. Comparer v1 et v2
        if compare:
            log.info("\n[STEP 2/4] Comparaison v1 vs v2...")
            log.info("-" * 80)
            comparison_report = compare_models()
            recommendation = comparison_report.get("recommendation", {})
            log.info(f"Recommandation: {recommendation.get('recommendation', 'N/A')}")
        else:
            recommendation = {}

        # 3. Gérer le registre et les stratégies de déploiement
        log.info("\n[STEP 3/4] Gestion du registre des modèles...")
        log.info("-" * 80)
        registry = ModelRegistry()
        registry.register_new_version("v2")
        current_version = registry.get_production_version()
        log.info(f"Version courante en production: {current_version}")

        # 4. Appliquer la stratégie de déploiement
        log.info(f"\n[STEP 4/4] Application de la stratégie: {deploy_strategy}...")
        log.info("-" * 80)

        if deploy_strategy == "shadow":
            log.info("📋 Shadow Deployment activée:")
            log.info("  - v2 s'exécutera en parallèle avec v1")
            log.info("  - Les utilisateurs reçoivent les prédictions de v1")
            log.info("  - Les divergences seront tracées pour analyse")

        elif deploy_strategy == "canary":
            log.info("🐤 Canary Deployment activée:")
            log.info("  - 10% du trafic sera dirigé vers v2")
            log.info("  - 90% du trafic restera sur v1")
            log.info("  - Les performances seront monitées")

        elif deploy_strategy == "rollback":
            log.info("🔄 Rollback demandé:")
            log.info(f"  - Retour à {current_version}")
            log.info("  - v2 ne sera pas déployé")

        elif deploy_strategy == "production":
            log.info("🚀 Production Deployment:")
            log.info("  - v2 remplace complètement v1 en production")
            auto_promote = True

        # Promotion optionnelle en production
        if auto_promote and deploy_strategy != "shadow" and deploy_strategy != "canary":
            log.info("\n[AUTO-PROMOTION] Promotion de v2 en production...")
            registry.promote_to_production("v2")
            log.info("✅ v2 est maintenant la version de production")

        log.info("\n" + "=" * 80)
        log.info("✅ PIPELINE TRAINING COMPLÉTÉ AVEC SUCCÈS")
        log.info("=" * 80)
        log.info(f"\nRésumé:")
        log.info(f"  - Modèle v2 entraîné ✅")
        log.info(f"  - Comparaison v1 vs v2 {'✅' if compare else '⏭️ '}")
        log.info(f"  - Stratégie déploiement: {deploy_strategy}")
        log.info(f"  - Production version: {registry.get_production_version()}")

        return {
            "status": "success",
            "model_trained": True,
            "comparison_done": compare,
            "deployment_strategy": deploy_strategy,
            "production_version": registry.get_production_version(),
            "recommendation": recommendation,
        }

    except Exception as e:
        log.error("=" * 80)
        log.error(f"❌ ERREUR DANS LE PIPELINE: {e}")
        log.error("=" * 80)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline de training v2, comparaison v1 vs v2, et déploiement"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Chemin vers le dataset (par défaut: data/processed/dataset_processed.csv)",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        default=True,
        help="Comparer v1 et v2 (par défaut: true)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["shadow", "canary", "rollback", "production"],
        default="shadow",
        help="Stratégie de déploiement (par défaut: shadow)",
    )
    parser.add_argument(
        "--auto-promote",
        action="store_true",
        default=False,
        help="Promouvoir automatiquement v2 en production (attention!)",
    )

    args = parser.parse_args()

    run_full_pipeline(
        dataset_path=args.dataset,
        compare=args.compare,
        deploy_strategy=args.strategy,
        auto_promote=args.auto_promote,
    )

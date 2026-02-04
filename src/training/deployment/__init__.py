"""
deployment_strategy.py - Gestion des stratégies de déploiement (shadow, canary, rollback).

Fournit des méthodes pour :
- Charger différentes versions de modèles
- Implémenter des stratégies de déploiement
- Tracer les performances en production
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import joblib

# Ajouter le parent directory pour les imports
ROOT_DIR = Path(__file__).resolve().parents[2]  # src/training -> src -> racine
sys.path.insert(0, str(ROOT_DIR))

from utils.log_utils import logger

log = logger("Deployment")

ARTIFACTS_DIR = ROOT_DIR / "artifacts"


class ModelLoader:
    """Charge les modèles depuis les artefacts."""

    @staticmethod
    def load_model(version: str):
        """
        Charge un modèle entraîné.

        Args:
            version: "v1" ou "v2"

        Returns:
            Model pipeline ou None si erreur
        """
        model_path = ARTIFACTS_DIR / version / "model.joblib"

        if not model_path.exists():
            log.error(f"Modèle {version} non trouvé: {model_path}")
            return None

        try:
            model = joblib.load(model_path)
            log.info(f"✅ Modèle {version} chargé depuis {model_path}")
            return model
        except Exception as e:
            log.error(f"Erreur lors du chargement du modèle {version}: {e}")
            return None

    @staticmethod
    def load_metrics(version: str) -> dict:
        """Charge les métriques d'une version."""
        metrics_path = ARTIFACTS_DIR / version / "metrics.json"

        if not metrics_path.exists():
            return None

        try:
            with open(metrics_path, "r") as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Erreur lors du chargement des métriques {version}: {e}")
            return None


class DeploymentStrategy:
    """
    Stratégies de déploiement pour les modèles.

    Trois stratégies supportées:
    - shadow: Le nouveau modèle s'exécute parallèlement sans affecter les utilisateurs
    - canary: Un petit % de trafic vers le nouveau modèle
    - rollback: Retour à la version précédente
    """

    def __init__(self, current_version: str = "v1", new_version: str = "v2"):
        """
        Initialise la stratégie de déploiement.

        Args:
            current_version: Version actuellement en production
            new_version: Version candidate pour le déploiement
        """
        self.current_version = current_version
        self.new_version = new_version
        self.current_model = ModelLoader.load_model(current_version)
        self.new_model = ModelLoader.load_model(new_version)
        self.deployment_log = []

        if self.current_model is None:
            log.error(f"Impossible de charger le modèle courant {current_version}")
        if self.new_model is None:
            log.error(f"Impossible de charger le nouveau modèle {new_version}")

    def shadow_deployment(self, X_sample) -> Tuple[dict, dict]:
        """
        Stratégie Shadow: Les deux modèles font des prédictions, mais seules
        celles de la version courante sont retournées à l'utilisateur.
        Les prédictions du nouveau modèle sont tracées pour comparaison.

        Args:
            X_sample: Données pour la prédiction

        Returns:
            (predictions_current, predictions_shadow)
        """
        log.info("🌑 SHADOW DEPLOYMENT: Exécution parallèle des modèles...")

        if self.current_model is None or self.new_model is None:
            log.error("Modèles non disponibles pour shadow deployment")
            return None, None

        try:
            # Prédictions modèle courant (servi à l'utilisateur)
            pred_current = self.current_model.predict(X_sample)
            log.debug(f"Prédiction {self.current_version}: {pred_current}")

            # Prédictions nouveau modèle (tracées en arrière-plan)
            pred_shadow = self.new_model.predict(X_sample)
            log.debug(f"Prédiction {self.new_version} (shadow): {pred_shadow}")

            # Tracer la différence
            if pred_current[0] != pred_shadow[0]:
                log.warning(
                    f"  ⚠️  Divergence détectée: {self.current_version}={pred_current[0]} "
                    f"vs {self.new_version}={pred_shadow[0]}"
                )
                self.deployment_log.append({
                    "strategy": "shadow",
                    "timestamp": datetime.now().isoformat(),
                    "divergence": True,
                    f"{self.current_version}": str(pred_current[0]),
                    f"{self.new_version}": str(pred_shadow[0]),
                })
            else:
                log.debug("  ✅ Prédictions concordantes")

            return pred_current, pred_shadow

        except Exception as e:
            log.error(f"Erreur lors de shadow deployment: {e}")
            return None, None

    def canary_deployment(self, X_sample, canary_percentage: float = 0.1) -> dict:
        """
        Stratégie Canary: Un petit % de trafic (par défaut 10%) est envoyé
        au nouveau modèle, le reste au modèle courant.

        Args:
            X_sample: Données pour la prédiction
            canary_percentage: % de trafic vers le nouveau modèle (0-1)

        Returns:
            Résultat de la prédiction + métadonnées sur le modèle utilisé
        """
        log.info(f"🐤 CANARY DEPLOYMENT: {canary_percentage*100}% trafic vers {self.new_version}...")

        if self.current_model is None or self.new_model is None:
            log.error("Modèles non disponibles pour canary deployment")
            return None

        try:
            import random

            # Décider quel modèle utiliser basé sur canary percentage
            use_new = random.random() < canary_percentage

            if use_new:
                if self.new_model is None:
                    log.error(f"Modèle {self.new_version} non disponible, fallback à {self.current_version}")
                    prediction = self.current_model.predict(X_sample)
                    model_used = self.current_version
                else:
                    prediction = self.new_model.predict(X_sample)
                    model_used = self.new_version
            else:
                prediction = self.current_model.predict(X_sample)
                model_used = self.current_version

            result = {
                "prediction": prediction[0],
                "model_version": model_used,
                "canary": use_new,
            }

            log.debug(f"  Modèle utilisé: {model_used} (canary={use_new})")
            return result

        except Exception as e:
            log.error(f"Erreur lors de canary deployment: {e}")
            return None

    def rollback(self) -> str:
        """
        Stratégie Rollback: Retour à la version précédente.

        Returns:
            Version à utiliser (version courante, car rollback = ne pas passer au nouveau modèle)
        """
        log.warning(f"🔄 ROLLBACK: Retour à {self.current_version}")

        self.deployment_log.append({
            "strategy": "rollback",
            "timestamp": datetime.now().isoformat(),
            "from": self.new_version,
            "to": self.current_version,
        })

        return self.current_version

    def get_deployment_log(self) -> list:
        """Retourne l'historique des déploiements."""
        return self.deployment_log

    def save_deployment_log(self, output_path: Path = None) -> None:
        """Sauvegarde le log de déploiement."""
        if output_path is None:
            output_path = ARTIFACTS_DIR / "deployment_log.json"

        with open(output_path, "w") as f:
            json.dump(self.deployment_log, f, indent=2)
        log.info(f"✅ Log de déploiement sauvegardé: {output_path}")


class ModelRegistry:
    """
    Registre des modèles - Gère les versions disponibles et la version courante
    en production.
    """

    def __init__(self, registry_path: Path = None):
        """
        Initialise le registre des modèles.

        Args:
            registry_path: Chemin vers le fichier registry.json
        """
        if registry_path is None:
            registry_path = ARTIFACTS_DIR / "registry.json"

        self.registry_path = registry_path
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        """Charge le registre depuis le fichier."""
        if not self.registry_path.exists():
            return {
                "production_version": "v1",
                "available_versions": ["v1"],
                "last_update": None,
            }

        try:
            with open(self.registry_path, "r") as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Erreur lors du chargement du registre: {e}")
            return {
                "production_version": "v1",
                "available_versions": ["v1"],
                "last_update": None,
            }

    def save_registry(self) -> None:
        """Sauvegarde le registre."""
        self.registry["last_update"] = datetime.now().isoformat()
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=2)
        log.info(f"✅ Registre sauvegardé: {self.registry_path}")

    def register_new_version(self, version: str) -> None:
        """
        Enregistre une nouvelle version.

        Args:
            version: Identifiant de la version (ex: "v2")
        """
        if version not in self.registry.get("available_versions", []):
            self.registry.setdefault("available_versions", []).append(version)
            log.info(f"✅ Version {version} enregistrée")
            self.save_registry()
        else:
            log.debug(f"Version {version} déjà enregistrée")

    def promote_to_production(self, version: str) -> None:
        """
        Promeut une version en production.

        Args:
            version: Version à promouvoir
        """
        self.registry["production_version"] = version
        log.info(f"✅ Version {version} promue en production")
        self.save_registry()

    def get_production_version(self) -> str:
        """Retourne la version actuellement en production."""
        return self.registry.get("production_version", "v1")

    def get_available_versions(self) -> list:
        """Retourne la liste des versions disponibles."""
        return self.registry.get("available_versions", ["v1"])

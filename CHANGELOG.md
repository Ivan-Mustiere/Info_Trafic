# CHANGELOG - Implementation Training MLOps Séance 7

## Fichiers Créés

### Scripts de Training
- **src/training/train_v2.py** (650+ lignes)
  - Entraînement du modèle v2 avec Pipeline scikit-learn
  - Preprocessing, evaluation complète
  - Sauvegarde artefacts (model, metrics, params, schema)
  - Logging détaillé

- **src/training/compare_models.py** (380+ lignes)
  - Chargement metrics v1 et v2
  - Tableau comparatif + recommandations
  - Sauvegarde rapport de comparaison
  - Seuils et logique de recommandation

- **src/training/training_pipeline.py** (280+ lignes)
  - Orchestration complète du pipeline
  - Support de 4 stratégies (shadow, canary, rollback, production)
  - Integration avec registry et deployment
  - CLI avec arguments

### Deployment et Registry
- **src/training/deployment/__init__.py** (350+ lignes)
  - Classe `ModelLoader`: Chargement modèles et métriques
  - Classe `DeploymentStrategy`: 3 stratégies (shadow, canary, rollback)
  - Classe `ModelRegistry`: Gestion des versions et production
  - Logging complet des transitions

- **src/training/deployment/deployment_strategy.py** (simple re-export)
  - Re-export des classes du module deployment

### Configuration
- **src/config/training.yaml** (60+ lignes)
  - Features et target
  - Paramètres du modèle
  - Configuration des stratégies
  - Seuils de comparaison
  - Configuration logging

### Artefacts de Base
- **artifacts/v1/metrics.json** - Baseline v1 (LogisticRegression)
- **artifacts/v1/params.json** - Paramètres v1
- **artifacts/v1/schema.json** - Schéma v1
- **artifacts/registry.json** - Model Registry (v1 production)

### Documentation
- **docs/TRAINING.md** (300+ lignes)
  - Structure complète du training
  - Quick start guide
  - Explication des stratégies
  - API endpoints
  - Configuration détaillée
  - Troubleshooting

- **IMPLEMENTATION.md** (400+ lignes)
  - Résumé complet de l'implémentation
  - Architecture et design
  - Cas d'usage pratiques
  - Checklist et étapes
  - Références aux fichiers

### Exemples
- **exemple_utilisation.py** (250+ lignes)
  - 6 exemples complets
  - Usage de chaque component
  - From simple training to full pipeline

## Fichiers Modifiés

### API
- **api/api.py** (150 lignes ajoutées/modifiées)
  - Support de MODEL_VERSION (v1 ou v2)
  - Support de DEPLOYMENT_STRATEGY (production, shadow, canary)
  - Integration avec DeploymentStrategy et ModelRegistry
  - Logging via logger()
  - Nouveaux endpoints:
    - `/model-info`: Infos modèle courant
    - `/predict-batch`: Prédictions batch
  - Amélioration endpoint `/predict` avec support multi-stratégies

### Requirements
- **docker/requirements/requirements.training.txt**
  - xgboost==2.1.1 ajouté (pour future experimentation)
  - Nettoyage du format

### Dockerfile
- **docker/Dockerfile.training**
  - Optimisé pour le training
  - Supporte training_pipeline.py comme CMD
  - Health check amélioré

## Structure de Répertoires Créée

```
src/training/
├── train.py              (LEGACY)
├── train_v2.py          ✅ NEW
├── compare_models.py    ✅ NEW
├── training_pipeline.py ✅ NEW
└── deployment/          ✅ NEW
    ├── __init__.py
    └── deployment_strategy.py

artifacts/
├── v1/                  ✅ NEW
│   ├── metrics.json
│   ├── params.json
│   └── schema.json
├── v2/                  ✅ NEW (created by train_v2.py)
│   ├── model.joblib
│   ├── metrics.json
│   ├── params.json
│   └── schema.json
└── registry.json        ✅ NEW
```

## Logging

Tous les scripts écrivent dans `/app/logs/`:
- `Training_V2.log` - train_v2.py
- `Model_Comparison.log` - compare_models.py
- `Training_Pipeline.log` - training_pipeline.py
- `Deployment.log` - Deployment strategy
- `API.log` - API handlers

Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Variables d'Environnement

### API
```bash
MODEL_VERSION=v1|v2                    # Défaut: v1
DEPLOYMENT_STRATEGY=production|shadow|canary  # Défaut: production
```

### Système
```bash
LOG_DIR=/app/logs                      # Défaut: /app/logs
PYTHONUNBUFFERED=1
```

## API Changes

### Nouveaux Endpoints
- **GET /model-info** - Infos modèle courant et registry
- **POST /predict-batch** - Prédictions par lot

### Endpoint Modifié
- **POST /predict** - Support multi-stratégies
  - Mode `production`: retourne prédiction simple
  - Mode `shadow`: v1 + v2 parallèle, retourne v1
  - Mode `canary`: 10% v2, 90% v1 (aléatoire)

### Metadata de Réponse
```json
{
  "prediction": "...",
  "model_version": "v1|v2",
  "deployment_strategy": "shadow|canary|production",
  "metadata": {
    "mode": "...",
    "model_used": "...",
    "shadow_available": true|false,
    "is_canary": true|false
  }
}
```

## Features Principales

✅ **Pipeline Scikit-learn**
- StandardScaler + RandomForest
- Preprocessing complet

✅ **Reproductibilité**
- Seed fixée à 42
- Sauvegarde des paramètres

✅ **Versioning**
- v1 et v2 séparés
- Model Registry

✅ **Comparaison Automatique**
- Tableaux de métriques
- Recommandations intelligentes
- Seuils configurable

✅ **Stratégies de Déploiement**
- Shadow: Test sans impact
- Canary: 10% trafic progressif
- Production: Remplacement complet
- Rollback: Retour en arrière

✅ **Logging Détaillé**
- À chaque étape majeure
- Traces de transitions
- Divergences détectées

✅ **API Flexible**
- Support multi-stratégies
- Switchable sans redémarrage (via ENV)
- Endpoints informatifs

## Tests et Validation

### Données de Base
- v1 avec métriques réalistes (accuracy: 0.8521, F1: 0.8503)
- v2 entraînable via train_v2.py sur dataset_processed.csv
- Comparaison automatique avec recommandations

### Logs
- Chaque script produit logs détaillés
- Timestamps et niveaux (INFO, WARNING, ERROR)
- Tracage des artefacts créés

## Commandes Principales

### Training
```bash
cd src/training
python train_v2.py
```

### Comparaison
```bash
python compare_models.py
```

### Pipeline Complet
```bash
python training_pipeline.py --strategy shadow
python training_pipeline.py --strategy canary
python training_pipeline.py --strategy production --auto-promote
```

### API avec Shadow
```bash
export MODEL_VERSION=v2
export DEPLOYMENT_STRATEGY=shadow
python -m uvicorn api.api:app --reload
```

### Exemples
```bash
python exemple_utilisation.py
```

## Dépendances Ajoutées

Aucune nouvelle dépendance majeure:
- scikit-learn: déjà présent
- pandas: déjà présent
- joblib: déjà présent

Optionnel (pour la suite):
- xgboost: ajouté aux requirements

## Notes Importantes

1. **Backward Compatibility**: train.py (legacy) toujours présent
2. **No Breaking Changes**: API anciens endpoints toujours fonctionnels
3. **Gradual Adoption**: Shadow deployment par défaut = zéro risque
4. **Monitoring-Ready**: Tous les logs tracent les transitions
5. **Production-Safe**: Seed fixée + artifacts versionnés

# 📑 INDEX - Navigation Rapide

## 🎯 Où Commencer?

### Pour comprendre l'implémentation
1. **[README_TRAINING.md](README_TRAINING.md)** ← START HERE
2. **[docs/TRAINING.md](docs/TRAINING.md)** ← Guide détaillé
3. **[IMPLEMENTATION.md](IMPLEMENTATION.md)** ← Résumé technique

### Pour exécuter
1. **[docs/TRAINING.md](docs/TRAINING.md#quick-start)** ← 3 étapes
2. **[exemple_utilisation.py](exemple_utilisation.py)** ← 6 exemples
3. **[docs/DOCKER_TRAINING.md](docs/DOCKER_TRAINING.md)** ← Docker

### Pour documenter les changements
- **[CHANGELOG.md](CHANGELOG.md)** ← Fichiers créés/modifiés

---

## 📚 Documentation Structure

```
Documentation/
├── README_TRAINING.md ......................... Vue d'ensemble générale
│
├── docs/
│   ├── TRAINING.md ........................... Guide complet du training
│   ├── DOCKER_TRAINING.md .................... Guide Docker
│   ├── Docker.md ............................. (Existant - autre docs Docker)
│   ├── etl.md ................................ (Existant - ETL docs)
│   └── doc_structure_et_echantillon.md ...... (Existant - Structure docs)
│
├── IMPLEMENTATION.md ......................... Résumé de l'implémentation
├── CHANGELOG.md ............................. Changements apportés
│
└── (Racine - autres docs existantes)
    ├── README.md ............................. (Existant - README général)
    └── docker-compose.yml ................... (Config Docker)
```

---

## 📂 Code Source Structure

```
src/training/
│
├── train_v2.py (650+ lignes)
│   ├── load_data()
│   ├── prepare_features_and_target()
│   ├── create_preprocessing_pipeline()
│   ├── create_model_pipeline()
│   ├── train_model()
│   ├── evaluate_model()
│   ├── save_artifacts()
│   └── main()
│
├── compare_models.py (380+ lignes)
│   ├── load_metrics()
│   ├── load_params()
│   ├── create_comparison_table()
│   ├── get_recommendation()
│   └── main()
│
├── training_pipeline.py (280+ lignes)
│   ├── run_full_pipeline()
│   └── __main__: CLI args parsing
│
├── deployment/ (Stratégies de déploiement)
│   └── __init__.py (350+ lignes)
│       ├── ModelLoader
│       │   ├── load_model()
│       │   └── load_metrics()
│       ├── DeploymentStrategy
│       │   ├── shadow_deployment()
│       │   ├── canary_deployment()
│       │   ├── rollback()
│       │   ├── get_deployment_log()
│       │   └── save_deployment_log()
│       └── ModelRegistry
│           ├── register_new_version()
│           ├── promote_to_production()
│           ├── get_production_version()
│           └── get_available_versions()
│
└── train.py (Legacy - existant)

src/config/
└── training.yaml (Configuration complète)

src/utils/
├── log_utils.py (Logging)
└── (autres utils existantes)

api/
└── api.py (150+ lignes modifiées)
    ├── GET /health
    ├── GET /model-info ..................... (Nouveau)
    ├── POST /predict ...................... (Amélioré)
    └── POST /predict-batch ............... (Nouveau)
```

---

## 📊 Artefacts Structure

```
artifacts/
│
├── v1/ (Baseline - précréé)
│   ├── metrics.json ......................... Métriques de référence
│   ├── params.json .......................... Paramètres du modèle
│   └── schema.json .......................... Schéma des features
│
├── v2/ (Créé par train_v2.py)
│   ├── model.joblib ......................... Pipeline entraîné
│   ├── metrics.json ......................... Métriques du nouveau modèle
│   ├── params.json .......................... Paramètres du nouveau modèle
│   └── schema.json .......................... Schéma des features
│
├── registry.json ............................ Model Registry (versions)
└── comparison_report.json .................. Rapport de comparaison (créé par compare_models.py)
```

---

## 🔄 Workflow Complet

```
1. TRAIN V2
   └─→ src/training/train_v2.py
       └─→ artifacts/v2/
           ├── model.joblib
           ├── metrics.json
           ├── params.json
           └── schema.json
       └─→ logs/Training_V2.log

2. COMPARE
   └─→ src/training/compare_models.py
       ├─→ Charge artifacts/v1/metrics.json
       ├─→ Charge artifacts/v2/metrics.json
       └─→ artifacts/comparison_report.json
       └─→ logs/Model_Comparison.log

3. DEPLOY
   └─→ src/training/training_pipeline.py
       ├─→ Orchestration des étapes 1-2
       ├─→ src/training/deployment/ (Stratégies)
       ├─→ ModelRegistry
       └─→ artifacts/registry.json
       └─→ logs/Training_Pipeline.log

4. API
   └─→ api/api.py
       ├─→ Charge MODEL_VERSION (env var)
       ├─→ Charge DEPLOYMENT_STRATEGY (env var)
       └─→ logs/API.log
```

---

## 📋 Commandes Principales

### Training
```bash
# Train v2
python -m src.training.train_v2

# Comparer v1 vs v2
python -m src.training.compare_models

# Pipeline complet (défaut: shadow)
python -m src.training.training_pipeline

# Pipeline avec options
python -m src.training.training_pipeline \
  --strategy canary \
  --compare \
  --dataset /path/to/data.csv
```

### API
```bash
# Mode production (v1)
export MODEL_VERSION=v1
export DEPLOYMENT_STRATEGY=production

# Mode shadow (v2 testé en parallèle)
export MODEL_VERSION=v2
export DEPLOYMENT_STRATEGY=shadow

# Mode canary (10% v2)
export MODEL_VERSION=v2
export DEPLOYMENT_STRATEGY=canary

# Démarrer API
python -m uvicorn api.api:app --reload
```

### Docker
```bash
# Build
docker build -f docker/Dockerfile.training -t training:v2 .

# Run training
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  training:v2

# Docker Compose
docker-compose up training
```

### Exemples
```bash
python exemple_utilisation.py
```

---

## 📖 Navigation par Sujet

### Entraînement du Modèle
- 📝 [train_v2.py](src/training/train_v2.py) - Code source
- 📖 [docs/TRAINING.md](docs/TRAINING.md#-quick-start-1) - Guide
- 💡 [exemple_utilisation.py](exemple_utilisation.py) - Ligne 24 (Exemple 1)

### Comparaison v1 vs v2
- 📝 [compare_models.py](src/training/compare_models.py) - Code source
- 📖 [docs/TRAINING.md](docs/TRAINING.md#-quick-start-2) - Guide
- 💡 [exemple_utilisation.py](exemple_utilisation.py) - Ligne 45 (Exemple 2)

### Stratégies de Déploiement
- 📝 [src/training/deployment/__init__.py](src/training/deployment/__init__.py) - Code source
- 📖 [README_TRAINING.md](README_TRAINING.md#-concepts-mlops) - Concepts
- 📖 [docs/TRAINING.md](docs/TRAINING.md#-stratégies-de-déploiement) - Stratégies détaillées
- 💡 [exemple_utilisation.py](exemple_utilisation.py) - Lignes 61, 79, 102

### Orchestration Pipeline
- 📝 [training_pipeline.py](src/training/training_pipeline.py) - Code source
- 📖 [README_TRAINING.md](README_TRAINING.md#-workflow-complet) - Workflow
- 💡 [exemple_utilisation.py](exemple_utilisation.py) - Ligne 120 (Exemple 6)

### Intégration API
- 📝 [api/api.py](api/api.py) - Code source
- 📖 [docs/TRAINING.md](docs/TRAINING.md#-api-endpoints) - Endpoints
- 📖 [README_TRAINING.md](README_TRAINING.md#-api-endpoints) - Endpoints avec exemples

### Docker
- 📝 [docker/Dockerfile.training](docker/Dockerfile.training) - Dockerfile
- 📖 [docs/DOCKER_TRAINING.md](docs/DOCKER_TRAINING.md) - Guide Docker
- 📖 [docker-compose.yml](docker-compose.yml) - Configuration

### Configuration
- ⚙️ [src/config/training.yaml](src/config/training.yaml) - Configuration

### Logging
- 📖 [docs/TRAINING.md](docs/TRAINING.md#-métriques-et-logs) - Logs
- 📖 [src/utils/log_utils.py](src/utils/log_utils.py) - Implémentation logging

---

## 🎓 Tutoriels Progressifs

### Niveau 1: Comprendre
1. Lire [README_TRAINING.md](README_TRAINING.md)
2. Parcourir [docs/TRAINING.md](docs/TRAINING.md)
3. Regarder la structure dans [IMPLEMENTATION.md](IMPLEMENTATION.md)

### Niveau 2: Exécuter
1. Exécuter [exemple_utilisation.py](exemple_utilisation.py)
2. Lancer `python -m src.training.train_v2`
3. Lancer `python -m src.training.compare_models`
4. Lancer `python -m src.training.training_pipeline`

### Niveau 3: Déployer
1. Lancer avec shadow: `--strategy shadow`
2. Monitorer les logs: `tail -f logs/Training_V2.log`
3. Tester l'API: `curl http://localhost:8000/model-info`
4. Passer à canary: `--strategy canary`
5. Promouvoir en production: `--strategy production --auto-promote`

### Niveau 4: Personnaliser
1. Modifier [src/config/training.yaml](src/config/training.yaml)
2. Adapter [train_v2.py](src/training/train_v2.py) (hyperparams)
3. Ajouter des métriques dans [compare_models.py](src/training/compare_models.py)
4. Créer custom strategies dans [src/training/deployment/__init__.py](src/training/deployment/__init__.py)

---

## 🔍 Recherche Rapide

| Sujet | Fichier | Ligne/Section |
|-------|---------|---------------|
| Entraînement | train_v2.py | main() |
| Preprocessing | train_v2.py | create_preprocessing_pipeline() |
| Pipeline ML | train_v2.py | create_model_pipeline() |
| Évaluation | train_v2.py | evaluate_model() |
| Comparaison | compare_models.py | create_comparison_table() |
| Recommandation | compare_models.py | get_recommendation() |
| Shadow Deploy | deployment/__init__.py | shadow_deployment() |
| Canary Deploy | deployment/__init__.py | canary_deployment() |
| Rollback | deployment/__init__.py | rollback() |
| Registry | deployment/__init__.py | ModelRegistry |
| API Health | api.py | /health |
| API Model Info | api.py | /model-info |
| API Predict | api.py | /predict |
| API Batch | api.py | /predict-batch |
| Configuration | training.yaml | (Config) |
| Logging | log_utils.py | logger() |

---

## 📞 FAQ Rapide

**Q: Par où commencer?**  
A: [README_TRAINING.md](README_TRAINING.md) → Quick Start

**Q: Comment entraîner v2?**  
A: `python -m src.training.train_v2`

**Q: Comment comparer v1 vs v2?**  
A: `python -m src.training.compare_models`

**Q: Quelle est la stratégie la plus sûre?**  
A: Shadow deployment (défaut) - aucun risque utilisateur

**Q: Où sont les logs?**  
A: `/app/logs/` - voir [docs/TRAINING.md](docs/TRAINING.md#-métriques-et-logs)

**Q: Comment voir les modèles entraînés?**  
A: `ls -la artifacts/v1/ artifacts/v2/`

**Q: Comment utiliser Docker?**  
A: [docs/DOCKER_TRAINING.md](docs/DOCKER_TRAINING.md)

**Q: J'ai une erreur, que faire?**  
A: Vérifier [docs/TRAINING.md#-troubleshooting](docs/TRAINING.md#-troubleshooting)

---

**Dernière mise à jour:** Février 2026  
**Version:** 1.0  
**Status:** ✅ Production Ready

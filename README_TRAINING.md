# 📚 Documentation Complète - Training MLOps Séance 7

## 🎯 Vue d'Ensemble

Cette implémentation complète le TP Séance 7 avec:

✅ **Script train_v2.py** - Entraînement reproductible avec Pipeline scikit-learn  
✅ **compare_models.py** - Comparaison v1 vs v2 avec recommandations  
✅ **Stratégies de déploiement** - Shadow, Canary, Production, Rollback  
✅ **Model Registry** - Gestion des versions  
✅ **API améliorée** - Support multi-stratégies  
✅ **Logging complet** - À tous les niveaux  
✅ **Artefacts versionnés** - Model, metrics, params, schema  

## 📖 Documentation

### Guide Principal
- **[docs/TRAINING.md](docs/TRAINING.md)** ⭐ START HERE
  - Structure du training
  - Quick start
  - Métriques et logs
  - Stratégies expliquées
  - Endpoints API
  - Troubleshooting

### Guides Complémentaires
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Résumé complet de l'implémentation
- **[CHANGELOG.md](CHANGELOG.md)** - Fichiers créés/modifiés
- **[docs/DOCKER_TRAINING.md](docs/DOCKER_TRAINING.md)** - Utilisation Docker
- **[exemple_utilisation.py](exemple_utilisation.py)** - 6 exemples concrets

## 🚀 Quick Start (3 étapes)

### 1️⃣ Entraîner v2

```bash
cd /app

# Option A: Script direct
cd src/training
python train_v2.py

# Option B: Depuis la racine
python -m src.training.train_v2
```

**Sortie attendue:**
```
artifacts/v2/
├── model.joblib      (Pipeline entraîné)
├── metrics.json      (Accuracy, Precision, Recall, F1)
├── params.json       (Paramètres)
└── schema.json       (Features)
```

### 2️⃣ Comparer v1 vs v2

```bash
python -m src.training.compare_models
```

**Résultat:**
```
Métrique    v1      v2      Δ(v2-v1)
Accuracy    0.8521  0.85XX  +0.00XX
Precision   0.8485  0.84XX  +0.00XX
Recall      0.8521  0.85XX  +0.00XX
F1-Score    0.8503  0.85XX  +0.00XX

Recommandation: promote_to_shadow
```

### 3️⃣ Pipeline Complet

```bash
# Shadow (aucun risque, défaut)
python -m src.training.training_pipeline --strategy shadow

# Ou avec canary (10% trafic)
python -m src.training.training_pipeline --strategy canary

# Ou production (remplace v1)
python -m src.training.training_pipeline --strategy production --auto-promote
```

## 📁 Structure des Fichiers Créés

```
src/training/
├── train_v2.py ........................ Entraînement v2 (650+ lignes)
├── compare_models.py .................. Comparaison v1/v2 (380+ lignes)
├── training_pipeline.py ............... Orchestration (280+ lignes)
└── deployment/
    └── __init__.py .................... Strategies & Registry (350+ lignes)

src/config/
└── training.yaml ...................... Configuration training

docs/
├── TRAINING.md ........................ Guide principal
└── DOCKER_TRAINING.md ................. Guide Docker

artifacts/
├── v1/ ................................ Baseline (métriques)
├── v2/ ................................ Nouveau modèle
└── registry.json ...................... Model Registry

(Racine)
├── IMPLEMENTATION.md .................. Résumé complet
├── CHANGELOG.md ....................... Fichiers modifiés
└── exemple_utilisation.py ............ 6 exemples
```

## 🎓 Concepts MLOps

### 1. Reproductibilité
```python
RANDOM_STATE = 42  # Même résultats à chaque run
```
- Seed fixée
- Paramètres sauvegardés
- Features documentées

### 2. Versioning
```
artifacts/v1/  ← Production baseline
artifacts/v2/  ← Nouveau candidat
artifacts/registry.json  ← Suivi des versions
```

### 3. Stratégies de Déploiement

#### Shadow (Défaut)
```
Client → API → v1 (retourné)  ✅
              + v2 (tracé en parallèle) 📊
```
✅ Zéro risque  
✅ Comparison réelle  
✅ Easy rollback  

#### Canary
```
Client → API → 90% v1 ✅
              + 10% v2 🐤
```
✅ Impact limité  
✅ Détection rapide d'erreurs  
✅ Progression progressive  

#### Production
```
Client → API → v2 remplace v1 🚀
```
✅ Remplacement complet  
⚠️ À utiliser après validation  

### 4. Monitoring
```
logs/Training_V2.log         ← Entraînement
logs/Model_Comparison.log    ← Comparaison
logs/Deployment.log          ← Transitions
logs/API.log                 ← Requêtes
```

## 🔧 Configuration

### training.yaml

```yaml
training:
  version: "v2"
  random_state: 42
  test_size: 0.2
  model:
    algorithm: "RandomForest"
    hyperparameters:
      n_estimators: 100
      max_depth: 10

deployment:
  default_strategy: "shadow"
  canary:
    percentage: 0.1
```

### Variables d'Environnement

```bash
# API
export MODEL_VERSION=v2              # v1 ou v2
export DEPLOYMENT_STRATEGY=shadow    # shadow, canary, production

# Système
export LOG_DIR=/app/logs
export PYTHONUNBUFFERED=1
```

## 📊 Métriques

### Metrics Sauvegardées

```json
{
  "accuracy": 0.8565,
  "precision": 0.8542,
  "recall": 0.8565,
  "f1": 0.8554,
  "confusion_matrix": [[...], [...], ...],
  "classification_report": {...},
  "test_size": 1500
}
```

### Targets

- Accuracy: > 0.85
- F1-Score: > 0.85
- Threshold d'amélioration: +1%

## 🌐 API Endpoints

### GET /health
```bash
curl http://localhost:8000/health
```

### GET /model-info
```bash
curl http://localhost:8000/model-info
# Response:
# {
#   "current_version": "v2",
#   "production_version": "v1",
#   "available_versions": ["v1", "v2"],
#   "deployment_strategy": "shadow",
#   "model_loaded": true
# }
```

### POST /predict
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "identifiant_arc": "12345",
    "heure": 10,
    "jour_semaine": 2,
    "is_weekend": 0,
    "taux_occupation": 0.75,
    "lat": 48.8566,
    "lon": 2.3522
  }'
```

### POST /predict-batch
```bash
curl -X POST http://localhost:8000/predict-batch \
  -H "Content-Type: application/json" \
  -d '[
    {...}, {...}
  ]'
```

## 🐳 Docker

### Build
```bash
docker build -f docker/Dockerfile.training -t training:v2 .
```

### Run Training
```bash
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  -e DEPLOYMENT_STRATEGY=shadow \
  training:v2
```

### Voir les détails
[docs/DOCKER_TRAINING.md](docs/DOCKER_TRAINING.md)

## 📈 Workflow Complet

```
1. Entraînement v2
   ↓
2. Comparaison v1 vs v2
   ↓
3. Recommandation automatique
   ├─→ shadow: v2 OK mais nouveau
   ├─→ canary: v2 meilleur, test progressif
   └─→ rollback: v2 dégradé
   ↓
4. Déploiement selon stratégie
   ├─→ Shadow: Pas d'impact
   ├─→ Canary: 10% trafic progressif
   └─→ Production: Remplacement v1
   ↓
5. Monitoring logs
   ├─→ Vérifier divergences (shadow)
   ├─→ Vérifier performances (canary)
   └─→ Valider en production
   ↓
6. Optionnel: Promotion v2 en production
```

## ✅ Checklist de Déploiement

- [ ] Entraîner v2: `python train_v2.py`
- [ ] Vérifier les logs: `cat logs/Training_V2.log`
- [ ] Comparer: `python compare_models.py`
- [ ] Vérifier le rapport: `cat artifacts/comparison_report.json`
- [ ] Tester en shadow: `--strategy shadow`
- [ ] Monitorer 24h
- [ ] Passer en canary: `--strategy canary`
- [ ] Vérifier les erreurs: `cat logs/API.log | grep ERROR`
- [ ] Promouvoir: `--strategy production --auto-promote`

## 🐛 Troubleshooting

### "Modèle v1 non trouvé"
```bash
# Les fichiers de baseline v1 sont pré-créés:
ls artifacts/v1/
```

### "Dataset non trouvé"
```bash
# Vérifier le chemin
ls data/processed/dataset_processed.csv

# Ou spécifier
python train_v2.py --dataset /path/to/dataset.csv
```

### "Erreur lors de l'API"
```bash
# Vérifier les logs
cat logs/API.log

# Vérifier le modèle
ls artifacts/v2/model.joblib
```

### Logs vides
```bash
# Vérifier les permissions
chmod 777 logs/

# Ou via Docker
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  training:latest \
  cat /app/logs/Training_V2.log
```

## 📚 Références

- **Scikit-learn Pipeline**: https://scikit-learn.org/stable/modules/pipeline.html
- **Deployment Strategies**: https://en.wikipedia.org/wiki/Deployment_strategy
- **Model Registry**: https://mlflow.org/docs/latest/model-registry.html
- **Logging Python**: https://docs.python.org/3/library/logging.html

## 💡 Points Clés

1. **Reproductibilité**: Seed 42 garanti
2. **Sécurité**: Shadow par défaut (zéro risque)
3. **Traçabilité**: Tous les modèles versionnés
4. **Automatisation**: Pipeline orchestré
5. **Monitoring**: Logs complets
6. **Flexibilité**: API supporte multi-stratégies
7. **Documentation**: Guides à tous les niveaux

## 🎯 Prochaines Étapes

1. Exécuter le training: `python train_v2.py`
2. Lire [docs/TRAINING.md](docs/TRAINING.md)
3. Tester les exemples: `python exemple_utilisation.py`
4. Lancer le pipeline: `python training_pipeline.py`
5. Monitorer les logs: `tail -f logs/Training_V2.log`
6. Tester l'API: `curl http://localhost:8000/model-info`

## 📞 Support

Pour toute question sur l'implémentation:
1. Vérifier [docs/TRAINING.md](docs/TRAINING.md)
2. Consulter [IMPLEMENTATION.md](IMPLEMENTATION.md)
3. Regarder [exemple_utilisation.py](exemple_utilisation.py)
4. Vérifier les logs dans `/app/logs/`

---

**Version:** 1.0  
**Date:** Février 2026  
**Status:** ✅ Production Ready

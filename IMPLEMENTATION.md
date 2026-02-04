# IMPLEMENTATION - Training MLOps Séance 7

## ✅ COMPLÈTE - Résumé de l'implémentation

### 1️⃣ **Scripts de Training**

#### [src/training/train_v2.py](src/training/train_v2.py)
- ✅ Charge un CSV/Parquet via `load_data()`
- ✅ Prépare X/y avec `prepare_features_and_target()`
- ✅ Pipeline scikit-learn: StandardScaler → RandomForest
- ✅ Seed fixée à 42 (reproductibilité)
- ✅ Évaluation complète: accuracy, precision, recall, f1, confusion_matrix
- ✅ Logging détaillé via `logger("Training_V2")`
- ✅ Sauvegarde des artefacts:
  - `artifacts/v2/model.joblib` (Pipeline entraîné)
  - `artifacts/v2/metrics.json` (Accuracy, precision, recall, f1, matrice)
  - `artifacts/v2/params.json` (Paramètres RandomForest)
  - `artifacts/v2/schema.json` (Liste des 7 features)

**Utilisation:**
```bash
cd src/training
python train_v2.py
```

#### [src/training/compare_models.py](src/training/compare_models.py)
- ✅ Charge `artifacts/v1/metrics.json` et `artifacts/v2/metrics.json`
- ✅ Génère un tableau comparatif Pandas
- ✅ Calcule les améliorations (Δ v2-v1)
- ✅ Produit une recommandation de déploiement:
  - Si F1 améliore de >1%: `promote_to_shadow`
  - Si variations légères: `test_canary`
  - Si dégradation: `rollback`
- ✅ Sauvegarde `artifacts/comparison_report.json`
- ✅ Logging complet dans `logs/Model_Comparison.log`

**Utilisation:**
```bash
python compare_models.py
```

### 2️⃣ **Stratégies de Déploiement**

#### [src/training/deployment/__init__.py](src/training/deployment/__init__.py)
Trois classes principales:

**ModelLoader**
```python
ModelLoader.load_model("v1")  # Charge le modèle
ModelLoader.load_metrics("v1")  # Charge les métriques
```

**DeploymentStrategy**
- `shadow_deployment(X)`: v1 + v2 parallèle, seul v1 retourné
- `canary_deployment(X, 0.1)`: 10% v2, 90% v1
- `rollback()`: Retour à v1
- `get_deployment_log()`: Historique

**ModelRegistry**
- `register_new_version("v2")`
- `promote_to_production("v2")`
- `get_production_version()`: v1 ou v2
- `get_available_versions()`: Liste des versions
- Sauvegarde dans `artifacts/registry.json`

**Logging:** `logs/Deployment.log`

### 3️⃣ **Pipeline d'Orchestration**

#### [src/training/training_pipeline.py](src/training/training_pipeline.py)
Lance le pipeline complet:

```bash
# Option 1: Shadow (défaut, aucun risque)
python training_pipeline.py --strategy shadow

# Option 2: Canary (10% trafic v2)
python training_pipeline.py --strategy canary

# Option 3: Production (replace v1)
python training_pipeline.py --strategy production --auto-promote

# Option 4: Rollback
python training_pipeline.py --strategy rollback
```

Étapes:
1. Entraîne v2
2. Compare v1 vs v2
3. Applique la stratégie
4. Met à jour le registre

**Logging:** `logs/Training_Pipeline.log`

### 4️⃣ **API Modifiée**

#### [api/api.py](api/api.py)
Configuration:
```python
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")  # v1 ou v2
DEPLOYMENT_STRATEGY = os.getenv("DEPLOYMENT_STRATEGY", "production")
```

**Endpoints:**

**GET /model-info**
```json
{
  "current_version": "v2",
  "production_version": "v1",
  "available_versions": ["v1", "v2"],
  "deployment_strategy": "shadow",
  "model_loaded": true
}
```

**POST /predict**
Supporte les 3 modes:
- `production`: Utilise MODEL_VERSION directement
- `shadow`: v1 + v2 parallèle → retourne v1
- `canary`: 10% v2 + 90% v1 (aléatoire)

```json
{
  "prediction": "Saturé",
  "model_version": "v1",
  "deployment_strategy": "shadow",
  "metadata": {
    "mode": "shadow",
    "shadow_available": true
  }
}
```

**POST /predict-batch**
Prédictions sur plusieurs records

**Logging:** `logs/API.log`

### 5️⃣ **Configuration et Artifacts**

#### [src/config/training.yaml](src/config/training.yaml)
- Features, target column
- Paramètres RandomForest
- Stratégies de déploiement
- Seuils de comparaison

#### Artifacts créés:
```
artifacts/
├── v1/  (Baseline)
│   ├── metrics.json       (accuracy: 0.8521, precision: 0.8485...)
│   ├── params.json        (LogisticRegression, max_iter: 5000)
│   └── schema.json        (7 features)
├── v2/  (Nouveau modèle)
│   ├── model.joblib       (Pipeline entraîné)
│   ├── metrics.json
│   ├── params.json        (RandomForest, n_estimators: 100...)
│   └── schema.json
├── registry.json          (production_version: "v1", available: ["v1", "v2"])
└── comparison_report.json (Rapport de comparaison)
```

#### [docker/requirements/requirements.training.txt](docker/requirements/requirements.training.txt)
```
pandas==2.2.2
scikit-learn==1.5.1
joblib==1.4.2
numpy==1.26.4
xgboost==2.1.1
```

### 6️⃣ **Documentation**

#### [docs/TRAINING.md](docs/TRAINING.md)
Guide complet avec:
- Quick start
- Métriques et logs
- Stratégies de déploiement expliquées
- API endpoints
- Configuration
- Troubleshooting
- Checklist de déploiement

## 🎯 **Cas d'Usage**

### Scénario 1: Entraîner et Tester v2 en Shadow
```bash
python training_pipeline.py --strategy shadow
```
✅ v2 entraîné et testé en parallèle  
✅ Aucun impact sur les utilisateurs  
✅ Logs tracent les divergences  
✅ Prêt pour canary si stable  

### Scénario 2: Progresser vers Production
```bash
# Day 1: Shadow (24h)
python training_pipeline.py --strategy shadow

# Day 2: Canary (1-2 jours, 10% trafic)
export MODEL_VERSION=v2
export DEPLOYMENT_STRATEGY=canary

# Day 3: Production full
python training_pipeline.py --strategy production --auto-promote
```

### Scénario 3: Rollback en Urgence
```bash
python training_pipeline.py --strategy rollback
# Registre revient à v1
```

## 📊 **Logging**

Tous les logs vont dans `/app/logs/`:
- `Training_V2.log` - Détails du training
- `Model_Comparison.log` - Comparaison v1/v2
- `Deployment.log` - Événements de déploiement
- `API.log` - Requêtes API + mode de déploiement

Chaque log inclut:
- 🕐 Timestamps
- 📊 Métriques
- 🔄 Transitions de version
- ⚠️ Divergences détectées
- ✅ Actions complétées

## 🔧 **Variables d'Environnement**

```bash
# Version du modèle à charger
export MODEL_VERSION=v2

# Stratégie de déploiement
export DEPLOYMENT_STRATEGY=shadow|canary|production

# Répertoire des logs
export LOG_DIR=/app/logs
```

## ✨ **Fonctionnalités Principales**

✅ **Reproductibilité:** Seed 42, sauvegarde des paramètres  
✅ **Versioning:** Modèles sauvegardés séparément (v1, v2)  
✅ **Comparaison automatique:** Tableaux et recommandations  
✅ **Déploiement sûr:** Shadow→Canary→Production  
✅ **Logging complet:** Traces à tous les niveaux  
✅ **Registry:** Suivi des versions en production  
✅ **API évolutive:** Supporte plusieurs stratégies  
✅ **Artefacts structurés:** Model, metrics, params, schema  

## 📁 **Fichiers Créés/Modifiés**

```
✅ src/training/train_v2.py                   (600 lignes)
✅ src/training/compare_models.py             (350 lignes)
✅ src/training/training_pipeline.py          (250 lignes)
✅ src/training/deployment/__init__.py        (350 lignes)
✅ src/training/deployment/deployment_strategy.py (simple re-export)
✅ src/config/training.yaml                   (Config)
✅ api/api.py                                  (Modifié - 150 lignes)
✅ docker/requirements/requirements.training.txt
✅ docker/Dockerfile.training                 (Optimisé)
✅ artifacts/v1/metrics.json                  (Baseline)
✅ artifacts/v1/params.json                   
✅ artifacts/v1/schema.json                   
✅ artifacts/registry.json                    (Model Registry)
✅ docs/TRAINING.md                           (Guide complet)
```

## 🚀 **Prêt pour l'exécution**

```bash
# 1. Préparation
cd /app

# 2. Entraînement v2
python -m src.training.train_v2

# 3. Comparaison
python -m src.training.compare_models

# 4. Pipeline complet avec shadow
python -m src.training.training_pipeline --strategy shadow

# 5. Vérifier les logs
cat logs/Training_V2.log
cat logs/Model_Comparison.log

# 6. Vérifier les artefacts
ls -la artifacts/v2/
cat artifacts/comparison_report.json
```

## 💡 **Notes Importantes**

- Le model v1 est créé avec des métriques de baseline
- RandomForest (v2) vs LogisticRegression (v1) pour comparer les algo
- Stratégie Shadow par défaut = **aucun risque**
- Tous les scripts utilisent des logs structurés
- Pipeline + Registry = versioning complet
- API supporte 3 modes sans changement de code

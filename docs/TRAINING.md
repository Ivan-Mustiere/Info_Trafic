# Training - Séance 7 MLOps

Guide complet pour le training du modèle v2, la comparaison v1 vs v2, et les stratégies de déploiement.

## 📋 Structure

```
src/training/
├── train.py                  # Script original v1 (legacy)
├── train_v2.py              # Script training v2 (nouveau)
├── compare_models.py        # Comparaison v1 vs v2
├── training_pipeline.py     # Orchestration complète
├── deployment/
│   └── __init__.py          # Strategies: shadow, canary, rollback
└── requirements/
    └── requirements.training.txt
```

## 🚀 Quick Start

### 1. Entraîner le modèle v2

```bash
cd /app/src/training

# Option 1: Script direct
python train_v2.py

# Option 2: Depuis le répertoire racine
python -m training.train_v2
```

**Sortie attendue:**
- `artifacts/v2/model.joblib` - Modèle entraîné
- `artifacts/v2/metrics.json` - Métriques (accuracy, precision, recall, f1)
- `artifacts/v2/params.json` - Paramètres du modèle
- `artifacts/v2/schema.json` - Liste des features

### 2. Comparer v1 et v2

```bash
python compare_models.py
```

**Sortie:**
- Tableau comparatif des métriques
- Recommandation de déploiement
- `artifacts/comparison_report.json`

### 3. Pipeline complet (train + compare + deploy)

```bash
# Option par défaut (shadow deployment)
python training_pipeline.py

# Avec canary deployment (10% trafic vers v2)
python training_pipeline.py --strategy canary

# Production (promouvoir v2 en tant que v1)
python training_pipeline.py --strategy production --auto-promote
```

## 📊 Métriques et Logs

### Fichiers de logs

- `logs/Training_V2.log` - Logs du training
- `logs/Model_Comparison.log` - Logs de la comparaison
- `logs/Deployment.log` - Logs de déploiement
- `logs/API.log` - Logs de l'API

### Métriques tracées

```json
{
  "accuracy": 0.8765,
  "precision": 0.8743,
  "recall": 0.8765,
  "f1": 0.8754,
  "confusion_matrix": [[...], [...], ...],
  "classification_report": {...},
  "test_size": 1500
}
```

## 🎯 Stratégies de Déploiement

### 1. Shadow Deployment (par défaut)

```
CLIENT -> API -> SHADOW DEPLOYMENT
                 ├── v1 (production)      ✅ Prédiction retournée
                 └── v2 (test)             📊 Tracée en parallèle
```

**Avantages:**
- Aucun risque pour les utilisateurs
- Comparison réelle avec le trafic de production
- Easy rollback

**Utilisation:**
```bash
python training_pipeline.py --strategy shadow
```

**Variable d'environnement:**
```bash
export MODEL_VERSION=v2
export DEPLOYMENT_STRATEGY=shadow
```

### 2. Canary Deployment (test progressif)

```
CLIENT -> API -> CANARY DEPLOYMENT
                 ├── 90% → v1 (production)
                 └── 10% → v2 (test)
```

**Avantages:**
- Impact réel mais limité
- Détection rapide des problèmes
- Increment progressif

**Utilisation:**
```bash
python training_pipeline.py --strategy canary
```

### 3. Production Deployment (remplacement complet)

```
CLIENT -> API -> PRODUCTION
                 └── v2 remplace v1
```

**Utilisation:**
```bash
python training_pipeline.py --strategy production --auto-promote
```

### 4. Rollback (retour en arrière)

```bash
python training_pipeline.py --strategy rollback
```

## 📈 API Endpoints

### GET /model-info
Informations sur le modèle courant

```bash
curl http://localhost:8000/model-info
```

**Réponse:**
```json
{
  "current_version": "v2",
  "production_version": "v1",
  "available_versions": ["v1", "v2"],
  "deployment_strategy": "shadow",
  "model_loaded": true
}
```

### POST /predict
Prédiction avec stratégie de déploiement

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

**Mode Shadow:**
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

**Mode Canary:**
```json
{
  "prediction": "Saturé",
  "model_version": "v2",
  "deployment_strategy": "canary",
  "metadata": {
    "mode": "canary",
    "model_used": "v2",
    "is_canary": true
  }
}
```

### POST /predict-batch
Prédictions en batch

```bash
curl -X POST http://localhost:8000/predict-batch \
  -H "Content-Type: application/json" \
  -d '[
    {"identifiant_arc": "12345", "heure": 10, ...},
    {"identifiant_arc": "67890", "heure": 11, ...}
  ]'
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
      min_samples_split: 5
      min_samples_leaf: 2

deployment:
  default_strategy: "shadow"
  canary:
    percentage: 0.1  # 10%
```

## 📦 Registre des Modèles

Le registre (`artifacts/registry.json`) trace:

```json
{
  "production_version": "v1",
  "available_versions": ["v1", "v2"],
  "last_update": "2026-02-04T10:30:00"
}
```

## ✅ Checklist de déploiement

- [ ] Entraîner v2: `python train_v2.py`
- [ ] Comparer v1 vs v2: `python compare_models.py`
- [ ] Vérifier les métriques dans `artifacts/comparison_report.json`
- [ ] Tester avec shadow deployment: `--strategy shadow`
- [ ] Monitorer les logs pendant 24h
- [ ] Passer à canary si stable: `--strategy canary`
- [ ] Vérifier les erreurs dans `logs/`
- [ ] Promouvoir en production si OK: `--strategy production --auto-promote`

## 🐛 Troubleshooting

### Erreur: "Modèle v1 non trouvé"

```bash
# Créer un modèle v1 de base
python -c "
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from pathlib import Path

model = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression())
])
Path('artifacts/v1').mkdir(parents=True, exist_ok=True)
joblib.dump(model, 'artifacts/v1/model.joblib')
print('✅ v1 créé')
"
```

### Erreur: "Dataset non trouvé"

```bash
# Vérifier le chemin
ls -la data/processed/dataset_processed.csv

# Ou spécifier le chemin
python train_v2.py --dataset /path/to/dataset.csv
```

### API ne charge pas le modèle

```bash
# Vérifier les permissions
ls -la artifacts/v2/model.joblib

# Vérifier le chemin des logs
cat logs/API.log
```

## 📚 Références

- **scikit-learn Pipeline**: https://scikit-learn.org/stable/modules/pipeline.html
- **Deployment Strategies**: https://en.wikipedia.org/wiki/Deployment_strategy
- **Model Registry**: https://mlflow.org/docs/latest/model-registry.html

## 📝 Notes

- La seed 42 est fixée pour la reproductibilité
- RandomForest avec 100 estimators et max_depth=10
- Stratégie Shadow par défaut (aucun risque utilisateur)
- Logging complet dans `/app/logs/`

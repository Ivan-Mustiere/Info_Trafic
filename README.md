# Projet Fil Rouge – Prédiction de Trafic Routier

## 🎯 Objectif
Prédire le niveau de trafic 30 minutes à l’avance sur un axe parisien donné, en exploitant les données open data des capteurs de comptage.

## 👥 Équipe
- Lead Data : Ismael
- MLOps : Ivan
- API : Mael
- RGPD/Sécurité : Merveille

## 📊 Données utilisées
- Source : [Comptage Routier Paris – Data.gouv](https://www.data.gouv.fr/fr/datasets/comptage-routier-donnees-trafic-issues-des-capteurs-permanents-1/)
- Format : CSV (open data)
- Variables : timestamp, id capteur, intensité trafic

## 🧠 KPI
- MAE entre trafic prédit et réel (volume horaire)

## 📦 Stack
- FastAPI, MLflow, Docker, GitHub Actions, GCP/AWS Free Tier


# Info_Trafic

mlops-filrouge-trafic/
├── data/                 # Jeux de données nettoyés, schémas, échantillons
├── etl/                  # Scripts d’ingestion, nettoyage, agrégation
├── training/             # Notebooks ou scripts de modélisation
├── serving/              # Code de l’API FastAPI (main.py, endpoints)
├── docker/               # Dockerfile, scripts de build
├── .github/workflows/    # Pipelines CI/CD (à venir)
├── docs/                 # README, RGPD, runbook, model card
└── README.md             # Description complète du projet

# Projet Fil Rouge – Prédiction de Trafic Routier

## 🎯 Objectif

Prédire le niveau de trafic 30 minutes à l’avance sur un axe parisien donné, en exploitant les données open data des capteurs permanents.

## 👥 Équipe

* MLOps : Ivan
* Lead Data : Ismael
* API : Mael
* RGPD/Sécurité : Merveille

## 📊 Données utilisées

* Source principale :
  Comptage Routier — Capteurs permanents (OpenData Paris)
  [opendata.paris.fr](https://opendata.paris.fr/explore/dataset/comptages-routiers-permanents/dataviz/?disjunctive.libelle&disjunctive.libelle_nd_amont&disjunctive.libelle_nd_aval&disjunctive.etat_trafic&sort=t_1h)
* Description : mesures en continu du trafic routier (intensité, timestamp, ID capteur).
* Format : CSV
* Champs principaux : `t_1h`, `id_nd`, `etat_trafic`, horodatage, intensité trafic.

## 🧠 KPI

MAE entre trafic prédit et réel (volume horaire).

## 📦 Stack

FastAPI, MLflow, Docker, GitHub Actions, GCP/AWS Free Tier.

---

# 🚦Info_Trafic – Structure du projet

```
mlops-filrouge-trafic/
├── data/                 # Jeux de données nettoyés, schémas, échantillons
├── etl/                  # Scripts d’ingestion, nettoyage, agrégation
├── training/             # Scripts de modélisation
├── serving/              # API FastAPI (main.py, endpoints)
├── docker/               # Dockerfile, scripts de build
├── .github/workflows/    # Pipelines CI/CD
├── docs/                 # README, RGPD, runbook, model card
├── logs/                 # Logs
└── README.md             # Description complète du projet
```

---

# ▶️ Exécuter le projet via Docker

## 1. Construire l’image

Depuis la racine du projet :

```
docker build -t mlops-trafic -f docker/Dockerfile .
```

## 2. Lancer le conteneur

```
docker run -p 8000:8000 mlops-trafic
```

L’API FastAPI sera disponible sur :

```
http://localhost:8000
```

Et la documentation interactive :

```
http://localhost:8000/docs
```
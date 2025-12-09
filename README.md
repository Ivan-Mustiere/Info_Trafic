# Projet Fil Rouge – Prédiction de Trafic Routier

## 🎯 Objectif

Prédire le niveau de trafic 1 heure à l’avance sur un axe parisien donné, en exploitant les données open data des capteurs permanents.

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

```text
project/
├─ app.py                        # Script principal / orchestrateur
├─ README.md                     # Documentation principale
├─ .gitignore                    # Fichiers et dossiers à ignorer par Git
├─ docker-compose.yml            # Orchestration des conteneurs Docker
├─ data/                         # Données : raw, processed, models, samples
├─ docker/                       # Dockerfiles et requirements spécifiques
│  ├─ Dockerfile.ingest
│  ├─ Dockerfile.etl
│  ├─ Dockerfile.training
│  ├─ Dockerfile.front
│  └─ requirements/
├─ src/                          # Code backend
│  ├─ ingest/
│  ├─ etl/
│  ├─ training/
│  └─ utils/
├─ frontend/                     # Interface utilisateur / dashboard
│  ├─ app_front.py
│  ├─ components/
│  └─ assets/
└─ docs/                         # Documentation supplémentaire
````


## 🐳 Les différents conteneurs Docker et leur rôle

Le projet est organisé en **plusieurs conteneurs Docker**, chacun ayant une responsabilité spécifique. Cela permet d’isoler les services, de faciliter le développement et de partager les données via des volumes.

| Conteneur    | Dockerfile            | Dossier copié                  | Volumes utilisés                             | Rôle                                                                                      |
| ------------ | --------------------- | ------------------------------ | -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **ingest**   | `Dockerfile.ingest`   | `src/ingest/` + `src/utils/`   | `/app/raw`, `/app/samples`                   | Collecte les données depuis MQTT ou API et les stocke dans `raw/`.                        |
| **etl**      | `Dockerfile.etl`      | `src/etl/` + `src/utils/`      | `/app/raw`, `/app/processed`, `/app/samples` | Nettoie, transforme et enrichit les données.                                              |
| **training** | `Dockerfile.training` | `src/training/` + `src/utils/` | `/app/processed`, `/app/models`              | Entraîne les modèles ML et les sauvegarde dans `models/`.                                 |
| **front**    | `Dockerfile.front`    | `frontend/` + `src/utils/`     | `/app/processed`, `/app/models`              | Affiche les données et résultats via l’interface utilisateur (Streamlit ou autre).        |
| **api**      | `Dockerfile.api`      | `app.py`              | `-`                                  | Expose FastAPI pour déclencher le pipeline (ingest, ETL, training) via des requêtes HTTP. |

---

### Points importants

* Chaque conteneur **est isolé** et a ses propres dépendances (`requirements.txt` spécifique).
* Les dossiers `raw/`, `processed/` et `models/` sont **mutualisés via des volumes**, permettant la communication entre conteneurs.
* Cela permet de **lancer uniquement un service** pour le développement ou le test, sans reconstruire tout le pipeline.
* Le front peut accéder aux données et modèles produits par les autres conteneurs en temps réel.
* L’API permet de **déclencher tout le pipeline** ou des parties spécifiques via des endpoints HTTP (`/ingest`, `/etl`, `/training`).

---

# ▶️ Exécuter le projet via Docker

## 1. Lancer tout le pipeline avec Docker Compose

Depuis la racine du projet, tu peux construire et démarrer **tous les services** (ingest, ETL, training, front, API) en une seule commande :

```bash
docker-compose up --build
```

* `--build` : reconstruit toutes les images avant de démarrer les conteneurs.
* Tous les conteneurs utilisent les volumes mutualisés (`data/raw`, `data/processed`, `data/models`).
* Le front (Streamlit) sera accessible sur le port défini (ex. `8501`).
* L’API FastAPI sera accessible sur `http://localhost:8000` avec la documentation interactive `http://localhost:8000/docs`.

Pour lancer en arrière-plan :

```bash
docker-compose up -d
```

---

## 2. Lancer un seul service

Si tu veux travailler sur **un service spécifique** sans démarrer tous les conteneurs :

```bash
docker-compose up --build etl
```

* Remplace `etl` par `ingest`, `training`, `front` ou `api` selon le service que tu veux lancer.
* Les autres conteneurs **ne seront pas démarrés**, mais les volumes nécessaires seront toujours accessibles.

---

## 3. Accéder au terminal d’un conteneur

Pour exécuter des commandes directement dans un conteneur en fonctionnement :

```bash
docker exec -it <nom_du_conteneur> /bin/bash
```

* Exemple pour ETL :

```bash
docker exec -it etl_container /bin/bash
```

* Tu peux ensuite naviguer dans le conteneur, lancer des scripts Python ou inspecter les fichiers montés dans `/app/raw`, `/app/processed`, etc.

---

## 4. Accéder à l’interface Front

* Streamlit :

```text
http://localhost:8501
```

* API FastAPI :

```text
http://localhost:8000
```

* Documentation interactive (Swagger) :

```text
http://localhost:8000/docs
```
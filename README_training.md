# Training Pipeline - Version 1

## Description
Ce script entraîne un modèle de machine learning en suivant les bonnes pratiques MLOps. Il utilise un fichier de données prétraitées (`processed.csv`) comme entrée et génère plusieurs artefacts, notamment le modèle entraîné, les métriques, les hyperparamètres et le schéma des features.

## Étapes du pipeline
1. **Chargement des données** :
   - Les données sont chargées depuis `data/processed.csv`.
   - Le fichier doit contenir une colonne cible nommée `Etat trafic`.

2. **Séparation des données** :
   - Les features (`X`) et la target (`y`) sont séparées.
   - Les données sont divisées en ensembles d'entraînement et de test (80/20) avec un `random_state` fixé pour garantir la reproductibilité.

3. **Entraînement du modèle** :
   - Le modèle par défaut est un `RandomForestClassifier`.
   - Vous pouvez changer le modèle en modifiant la variable `model_type` dans le script (par exemple, `LogisticRegression`).

4. **Évaluation du modèle** :
   - Les métriques calculées incluent :
     - `Accuracy`
     - `F1-score` (pondéré)

5. **Sauvegarde des artefacts** :
   - Modèle : `data/models/model.joblib`
   - Métriques : `artifacts/v1/metrics.json`
   - Hyperparamètres : `artifacts/v1/params.json`
   - Schéma des features : `artifacts/v1/schema.json`
   - Logs : `artifacts/v1/training.log`

## Prérequis
- Python 3.12 ou version ultérieure
- Bibliothèques Python nécessaires (voir `requirements.txt`) :
  - pandas
  - scikit-learn
  - joblib

## Instructions

### 1. Préparer l'environnement
- Assurez-vous que les dépendances sont installées :
  ```bash
  pip install -r requirements.txt
  ```

### 2. Vérifier les données
- Placez le fichier `processed.csv` dans le dossier `data/`.
- Assurez-vous que le fichier contient la colonne cible `Etat trafic`.

### 3. Lancer le script
- Exécutez le script avec la commande suivante :
  ```bash
  python train_v1.py
  ```

### 4. Vérifier les résultats
- Consultez les logs dans `artifacts/v1/training.log`.
- Vérifiez les artefacts générés :
  - Modèle : `data/models/model.joblib`
  - Métriques : `artifacts/v1/metrics.json`
  - Hyperparamètres : `artifacts/v1/params.json`
  - Schéma des features : `artifacts/v1/schema.json`

## Notes
- Si le dossier `data/models/` ou `artifacts/v1/` n'existe pas, le script les créera automatiquement.
- Pour toute modification du modèle ou des hyperparamètres, éditez directement le script `train_v1.py`.

## Contact
Pour toute question, contactez l'équipe de développement.

//
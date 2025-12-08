import pandas as pd
import os
from datetime import datetime
import logging

# ----- Configuration -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier du script

SAMPLE_CSV_PATH = os.path.join(BASE_DIR, "..", "data", "samples", "traffic_sample.csv")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "ingestion.log")

# Colonnes attendues
EXPECTED_COLUMNS = [
    "Identifiant arc",
    "Libelle",
    "Date et heure de comptage",
    "Débit horaire",
    "Taux d'occupation",
    "Etat trafic",
    "Identifiant noeud amont",
    "Libelle noeud amont",
    "Identifiant noeud aval",
    "Libelle noeud aval",
    "Etat arc",
    "Date debut dispo data",
    "Date fin dispo data",
    "geo_point_2d",
    "geo_shape"
]

# ----- Préparation logs -----
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def load_data(path):
    try:
        df = pd.read_csv(path, sep=';')  # point-virgule comme séparateur
        logging.info(f"Chargement réussi du fichier : {path}")
        print(f"Données chargées : {df.shape[0]} lignes, {df.shape[1]} colonnes")
        return df
    except Exception as e:
        logging.error(f"Erreur lors du chargement : {e}")
        raise

def validate_structure(df):
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    extra_cols = [col for col in df.columns if col not in EXPECTED_COLUMNS]

    if missing_cols:
        msg = f"Colonnes manquantes : {missing_cols}. Ingestion arrêtée."
        logging.error(msg)
        raise ValueError(msg)
    
    if extra_cols:
        msg = f"Colonnes supplémentaires détectées : {extra_cols}"
        logging.warning(msg)
        print(msg)

    logging.info("Structure des données validée.")

def main():
    logging.info("=== Début de l’ingestion ===")
    df = load_data(SAMPLE_CSV_PATH)
    validate_structure(df)
    logging.info("=== Fin de l’ingestion ===")
    print("Ingestion terminée avec succès.")

if __name__ == "__main__":
    main()

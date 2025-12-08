import os
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# =========================
# 1. CONFIG + LOGS
# =========================

BASE_DIR = Path(__file__).resolve().parent

SAMPLES_DIR = BASE_DIR / ".." / "data" / "samples"
RAW_DIR = BASE_DIR / ".." / "data" / "raw"
LOGS_DIR = BASE_DIR / ".." / "logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "ingestion.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Colonnes attendues (les tiennes)
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

# =========================
# 2. AWS CONFIG
# =========================

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def get_s3_client():
    """Initialise un client S3"""
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not S3_BUCKET_NAME:
        raise ValueError("Variables AWS manquantes dans .env")

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    return session.client("s3")


# =========================
# 3. LOGIQUE INGESTION DATA
# =========================

def load_data(path: Path) -> pd.DataFrame:
    """Charge le CSV local"""
    logging.info(f"Tentative de chargement : {path}")

    if not path.exists():
        raise FileNotFoundError(f"Fichier non trouvé : {path}")

    df = pd.read_csv(path, sep=';')
    logging.info(f"Données chargées : {df.shape[0]} lignes / {df.shape[1]} colonnes")
    print(f"Données chargées : {df.shape[0]} lignes / {df.shape[1]} colonnes")

    return df


def validate_structure(df: pd.DataFrame):
    """Vérifie les colonnes attendues"""
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]

    if missing:
        logging.error(f"Colonnes manquantes : {missing}")
        raise ValueError(f"Colonnes manquantes : {missing}")

    if extra:
        logging.warning(f"Colonnes supplémentaires détectées : {extra}")
        print(f"⚠️ Colonnes supplémentaires : {extra}")

    logging.info("Structure validée.")


def upload_to_s3(df: pd.DataFrame, s3_client):
    """Envoie le CSV vers S3 avec une organisation par date"""

    now = datetime.utcnow()
    date_prefix = now.strftime("%Y/%m/%d")
    file_name = f"traffic_raw_{now.strftime('%Y%m%d_%H%M%S')}.csv"

    local_tmp = RAW_DIR / file_name
    df.to_csv(local_tmp, index=False)

    s3_key = f"raw/traffic/{date_prefix}/{file_name}"

    try:
        s3_client.upload_file(str(local_tmp), S3_BUCKET_NAME, s3_key)
        logging.info(f"Upload S3 : s3://{S3_BUCKET_NAME}/{s3_key}")
    except ClientError as e:
        logging.error(f"Erreur upload S3 : {e}")
        raise

    return f"s3://{S3_BUCKET_NAME}/{s3_key}"


# =========================
# 4. MAIN
# =========================

def main():
    logging.info("=== Début ingestion ===")

    sample_file = SAMPLES_DIR / "traffic_sample.csv"

    try:
        s3_client = get_s3_client()
    except Exception as e:
        print(f"Erreur S3 : {e}")
        return

    try:
        df = load_data(sample_file)
        validate_structure(df)
        s3_path = upload_to_s3(df, s3_client)

        print(f"Ingestion terminée → {s3_path}")
        logging.info(f"Ingestion terminée. Stockage : {s3_path}")

    except Exception as e:
        logging.error(f"Ingestion échouée : {e}")
        print(f"Erreur ingestion : {e}")

    logging.info("=== Fin ingestion ===")


if __name__ == "__main__":
    main()

import os
from utils.log_utils import logger


SAMPLES_DIR = "/app/samples"
RAW_DIR = "/app/raw"

log = logger("Ingest")

def ingest_run(dataset_name="dossier.csv"):
    """
    - PROD    : télécharge le dataset depuis S3 vers raw/
    - PREPROD : vérifie qu'il existe au moins un fichier .csv dans samples/
    """
    env = os.environ.get("ENV", "preprod").lower()
    
    dest_path = os.path.join(RAW_DIR, dataset_name)

    if env == "prod":
        import boto3

        bucket_name = os.environ.get("DATA_BUCKET", "my-bucket")
        s3 = boto3.client("s3")

        try:
            os.makedirs(RAW_DIR, exist_ok=True)
            s3.download_file(bucket_name, dataset_name, dest_path)
            log.info(f"Dataset téléchargé depuis S3 : {bucket_name}/{dataset_name}")
        except Exception as e:
            log.error(f"Erreur téléchargement S3 : {e}")

    elif env == "preprod":
        if not os.path.isdir(SAMPLES_DIR):
            log.error(f"Dossier '{SAMPLES_DIR}' introuvable")
            return None

        csv_files = [f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith(".csv")]

        if csv_files:
            log.info(f"{len(csv_files)} fichier(s) CSV trouvé(s) dans samples/")
        else:
            log.warning("Aucun fichier CSV trouvé dans samples/")

    else:
        log.warning(f"ENV non reconnu : {env} (attendu : PROD ou PREPROD)")

    return dest_path


if __name__ == "__main__":
    ingest_run()

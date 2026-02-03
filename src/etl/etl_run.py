import os
import glob
from utils.log_utils import logger
from utils.file_utils import read_csv, write_csv
from etl.transformations.clean_csv import clean_dataframe
from etl.transformations.date_csv import date_csv

PROCESSED_DIR = "/app/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

container_name = os.getenv("CONTAINER_NAME", "default_logger")
log = logger(container_name)

def etl_run():
    env = os.environ.get("ENV", "preprod").lower()
    source_dir = "/app/raw" if env == "prod" else "/app/samples"

    csv_files = glob.glob(os.path.join(source_dir, "*.csv"))
    if not csv_files:
        log.error(f"Aucun fichier CSV trouvé dans {source_dir}")
        return
    elif len(csv_files) > 1:
        log.warning(f"Plusieurs CSV trouvés, traitement du premier : {csv_files[0]}")

    raw_path = csv_files[0]
    filename = os.path.basename(raw_path)
    processed_path = os.path.join(PROCESSED_DIR, filename)

    # Extract
    log.info(f"Lecture du fichier {raw_path}")
    df = read_csv(raw_path)

    # Transform
    df = clean_dataframe(df)
    log.info(f"Nettoyage terminé, {len(df)} lignes conservées")
    df = date_csv(df)
    log.info(f"Date transformation terminée, {len(df)} lignes conservées")

    log.info(f"ETL Transformation terminée, {len(df)} lignes conservées")

    # Load
    write_csv(df, processed_path)
    log.info(f"Fichier transformé sauvegardé dans {processed_path}")

if __name__ == "__main__":
    etl_run()
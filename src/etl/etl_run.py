import os
import glob
import pandas as pd
from utils.log_utils import logger

PROCESSED_DIR = "/app/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

log = logger("Etl")

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
    df = pd.read_csv(raw_path, sep=";")

    # Transform
    df.dropna(inplace=True)
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.strip()
    log.info(f"Transformation terminée, {len(df)} lignes conservées")

    # Load
    df.to_csv(processed_path, index=False, sep=";")
    log.info(f"Fichier transformé sauvegardé dans {processed_path}")

if __name__ == "__main__":
    etl_run()
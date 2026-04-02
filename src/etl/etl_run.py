import os
import glob
import time
from utils.log_utils import logger
from utils.file_utils import read_csv, write_csv
from etl.transformations.clean_dataframe import clean_dataframe
from etl.transformations.clean_columns import clean_columns
from etl.transformations.clean_date import clean_date

PROCESSED_DIR = "/app/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

container_name = os.getenv("CONTAINER_NAME", "default_logger")
log = logger(container_name)

def etl_run():
    start_time = time.time()
    
    try:
        env = os.environ.get("ENV", "preprod").lower()
        source_dir = "/app/raw" if env == "prod" else "/app/samples"
        log.info(f"Démarrage ETL en mode {env.upper()}, source: {source_dir}")

        csv_files = glob.glob(os.path.join(source_dir, "*.csv"))
        if not csv_files:
            log.error(f"❌ Aucun fichier CSV trouvé dans {source_dir}")
            raise FileNotFoundError(f"Aucun fichier CSV dans {source_dir}")
        elif len(csv_files) > 1:
            log.warning(f"⚠️ Plusieurs CSV trouvés ({len(csv_files)}), traitement du premier : {csv_files[0]}")

        raw_path = csv_files[0]
        processed_path = os.path.join(PROCESSED_DIR, "processed_data.csv")

        # Extract
        log.info(f"📂 Lecture du fichier {raw_path}")
        df = read_csv(raw_path)
        initial_rows = len(df)
        log.info(f"✅ {initial_rows} lignes chargées")
        
        if df.empty:
            raise ValueError("Le fichier chargé est vide")

        # Transform
        log.info("🔧 Début des transformations...")
        
        df = clean_dataframe(df)
        log.info(f"✅ Nettoyage terminé: {len(df)} lignes conservées ({initial_rows - len(df)} supprimées)")
        
        df = clean_columns(df)
        log.info(f"✅ Transformation des colonnes terminée: {len(df)} lignes, {len(df.columns)} colonnes")
        
        df = clean_date(df)
        log.info(f"✅ Transformation date/heure terminée: {len(df)} lignes conservées")
        
        if df.empty:
            raise ValueError("Aucune donnée restante après transformation")
        
        log.info(f"✅ ETL Transformation complète: {len(df)} lignes finales")
        log.info(f"Colonnes finales: {list(df.columns)}")

        # Load
        write_csv(df, processed_path)
        elapsed = time.time() - start_time
        log.info(f"✅ Fichier transformé sauvegardé dans {processed_path} (durée: {elapsed:.2f}s)")
        
    except FileNotFoundError as e:
        log.error(f"❌ Fichier non trouvé: {e}")
        raise
    except ValueError as e:
        log.error(f"❌ Erreur de validation: {e}")
        raise
    except Exception as e:
        log.error(f"❌ Erreur inattendue lors de l'ETL: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    etl_run()
# app.py
import argparse
import os
from utils.log_utils import logger

container_name = os.getenv("CONTAINER_NAME", "default_logger")

def ingest():
    from ingest.ingest_run import ingest_run
    log = logger(container_name)
    log.info("Lancement de l’ingestion...")
    ingest_run()
    log.info("Ingestion terminée !")
    log.info("===============================================")
def etl():
    from etl.etl_run import etl_run
    log = logger(container_name)
    log.info("Lancement de l’ETL...")
    etl_run()
    log.info("ETL terminé !")
    log.info("===============================================")
def training():
    log = logger(container_name)
    from training.train import main
    log.info("Lancement du training ML...")
    main()
    log.info("Training terminé !")
    log.info("===============================================")

def api():
    """
    Lancement de l'API FastAPI en local (hors Docker).
    Utile pour tester rapidement le serving du modèle.
    """
    import uvicorn

    log = logger("API")
    log.info("Démarrage de l'API FastAPI...")
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", choices=["ingest", "etl", "training", "api"], required=True)

    args = parser.parse_args()

    if args.mode == "ingest":
        ingest()

    elif args.mode == "etl":
        etl()

    elif args.mode == "training":
        training()

    elif args.mode == "api":
        api()

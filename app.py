# app.py
import argparse
from utils.log_utils import logger

def ingest():
    from ingest.ingest_run import ingest_run
    log = logger("Ingest")  # variable différente
    log.info("📥 Lancement de l’ingestion...")
    ingest_run()
    log.info("✅ Ingestion terminée !")

def etl():
    from etl.etl_run import etl_run
    log = logger("Etl")
    log.info("🔄 Lancement de l’ETL...")
    etl_run()
    log.info("✅ ETL terminé !")
def training():
    log = logger("Training")
    from training.train import main
    log.info("🤖 Lancement du training ML...")
    main()
    log.info("✅ Training terminé !")
def run_api():
    import threading
    from fastapi import FastAPI
    from pydantic import BaseModel
    import uvicorn

    app = FastAPI(

        title="API Info Trafic",

        description="API pour gérer ingestion, ETL et training",

        version="1.0"

    )

    class JobRequest(BaseModel):

        mode: str

    @app.get("/status", tags=["Info"])

    def status():

        return {"status": "API OK"}
    @app.post("/run-job", tags=["Jobs"])

    def run_job(request: JobRequest):

        mode = request.mode.lower()

        def target():

            if mode == "ingest":

                ingest()

            elif mode == "etl":

                etl()

            elif mode == "training":

                training()

            else:

                print(f"❌ Mode inconnu : {mode}")

        threading.Thread(target=target).start()

        return {"status": f"{mode} lancé en arrière-plan"}

    uvicorn.run(app, host="0.0.0.0", port=8000)

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

        run_api()
# app.py
import argparse
import time
from fastapi import FastAPI
from pydantic import BaseModel
import threading

# -----------------------
# Fonctions de chaque service
# -----------------------

def ingest():
    print("📥 Lancement de l’ingestion...")
    # Ici ton code pour récupérer les données depuis MQTT ou API
    time.sleep(2)
    print("✅ Ingestion terminée !")

def etl():
    print("🔄 Lancement de l’ETL...")
    # Ici ton code pour transformer les données
    time.sleep(3)
    print("✅ ETL terminé !")

def training():
    print("🤖 Lancement du training ML...")
    # Ici ton code pour entraîner ton modèle
    time.sleep(5)
    print("✅ Training terminé !")

# -----------------------
# API avec FastAPI
# -----------------------

app = FastAPI(
    title="API Info Trafic",
    description="API pour gérer ingestion, ETL et training",
    version="1.0"
)

class JobRequest(BaseModel):
    mode: str

@app.get("/status", tags=["Info"])
def status():
    """
    Vérifie le statut de l'API
    """
    return {"status": "API OK"}

@app.post("/run-job", tags=["Jobs"])
def run_job(request: JobRequest):
    """
    Lance un job (ingest, ETL ou training) en arrière-plan.
    """
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

    # Lancer le job dans un thread pour ne pas bloquer l’API
    threading.Thread(target=target).start()
    return {"status": f"{mode} lancé en arrière-plan"}

# -----------------------
# Point d’entrée
# -----------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Point d'entrée pour ingestion, ETL, training ou API")
    parser.add_argument(
        "--mode", 
        choices=["ingest", "etl", "training", "api"], 
        required=True, 
        help="Mode d'exécution : ingest, etl, training ou api"
    )
    args = parser.parse_args()

    if args.mode == "ingest":
        ingest()
    elif args.mode == "etl":
        etl()
    elif args.mode == "training":
        training()
    elif args.mode == "api":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

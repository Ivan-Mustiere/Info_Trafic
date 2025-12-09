from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def root():
    return {"status": "webcron OK"}

@app.post("/run/etl")
def run_etl():
    subprocess.Popen(["python", "etl/ingest_data.py"])
    return {"message": "ETL lancé"}

@app.post("/run/training")
def run_training():
    subprocess.Popen(["python", "training/train.py"])
    return {"message": "Training lancé"}

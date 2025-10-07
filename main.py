from fastapi import FastAPI
import pandas as pd

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FastAPI tourne dans Docker avec Pandas !"}

@app.get("/data")
def get_data():
    df = pd.DataFrame({
        "ville": ["Paris", "Lyon", "Marseille"],
        "temperature": [20, 24, 22]
    })
    return df.to_dict(orient="records")

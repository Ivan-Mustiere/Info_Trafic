from fastapi import FastAPI
from endpoints.predict import router

app = FastAPI(title="Fil Rouge – API IA Trafic")

# Endpoint de santé
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Inclure les endpoints
app.include_router(router, prefix="/api")
    
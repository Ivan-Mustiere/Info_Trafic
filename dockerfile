FROM python:3.9-slim

# Empêcher la création de .pyc et forcer le flush des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Dossier de travail
WORKDIR /app

# Installer juste les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier le code de l’application
COPY . /app

# Exposer le port de l'API FastAPI (si tu en as une)
EXPOSE 8000

# Lancer le serveur FastAPI (ou autre script principal)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

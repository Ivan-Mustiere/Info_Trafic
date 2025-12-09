FROM python:3.10-slim

WORKDIR /app

# Dépendances système si besoin
RUN apt-get update && apt-get install -y cron curl && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["bash"]

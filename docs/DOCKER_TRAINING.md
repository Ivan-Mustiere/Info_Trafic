# Docker - Training Pipeline

## Démarrer le Training en Container

### 1. Build de l'image

```bash
cd /app

# Build l'image training
docker build -f docker/Dockerfile.training -t training:v2 .
```

### 2. Executer le training en container

```bash
# Shadow deployment (défaut)
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  training:v2

# Canary deployment
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  -e DEPLOYMENT_STRATEGY=canary \
  training:v2 \
  python -m src.training.training_pipeline --strategy canary

# Production deployment
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  -e DEPLOYMENT_STRATEGY=production \
  training:v2 \
  python -m src.training.training_pipeline --strategy production --auto-promote
```

### 3. Vérifier les logs

```bash
# Depuis le host
tail -f logs/Training_V2.log
tail -f logs/Model_Comparison.log

# Depuis le container
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  training:v2 \
  cat logs/Training_V2.log
```

## Docker Compose (Optionnel)

Ajouter au docker-compose.yml:

```yaml
services:
  training:
    build:
      context: .
      dockerfile: docker/Dockerfile.training
    volumes:
      - ./logs:/app/logs
      - ./artifacts:/app/artifacts
      - ./data:/app/data
    environment:
      - DEPLOYMENT_STRATEGY=shadow
      - LOG_DIR=/app/logs
    command: >
      python -m src.training.training_pipeline
      --strategy shadow
      --compare
    healthcheck:
      test: ["CMD", "python", "-c", "import joblib; print('ok')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Utilisation:

```bash
# Démarrer le training
docker-compose up training

# Avec logs
docker-compose up training --log-driver local

# En background
docker-compose up -d training

# Voir les logs
docker-compose logs -f training

# Arrêter
docker-compose down
```

## Variables d'Environnement

```bash
MODEL_VERSION=v1|v2
DEPLOYMENT_STRATEGY=shadow|canary|production|rollback
LOG_DIR=/app/logs
PYTHONUNBUFFERED=1
```

## Health Check

```bash
# Test du container
docker exec <container_id> python -c "import joblib; print('ok')"

# Avec docker-compose
docker-compose ps
```

## Volumes Importants

```
/app/logs          ← Logs (à persister)
/app/artifacts     ← Modèles et métriques (À PERSISTER!)
/app/data          ← Dataset (input)
```

Exemple avec volumes nommés:

```bash
docker run --rm \
  -v training-logs:/app/logs \
  -v training-artifacts:/app/artifacts \
  -v $(pwd)/data:/app/data:ro \
  training:v2
```

## Workflow Complet en Docker

```bash
# 1. Build
docker build -f docker/Dockerfile.training -t training:latest .

# 2. Run training v2 en shadow
docker run --rm \
  --name training-v2-shadow \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  -e DEPLOYMENT_STRATEGY=shadow \
  training:latest

# 3. Vérifier les logs
docker logs training-v2-shadow

# 4. Verifier les artefacts créés
ls -la artifacts/v2/

# 5. Lancer l'API avec v2 en shadow
docker run --rm \
  --name api-shadow \
  -p 8000:8000 \
  -v $(pwd)/artifacts:/app/artifacts \
  -e MODEL_VERSION=v2 \
  -e DEPLOYMENT_STRATEGY=shadow \
  api:latest

# 6. Tester
curl http://localhost:8000/model-info

# 7. Après validation, passer à canary
docker run --rm \
  --name training-v2-canary \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  -e DEPLOYMENT_STRATEGY=canary \
  training:latest \
  python -m src.training.training_pipeline --strategy canary --compare

# 8. Finalement, production
docker run --rm \
  --name training-v2-prod \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  -e DEPLOYMENT_STRATEGY=production \
  training:latest \
  python -m src.training.training_pipeline \
    --strategy production \
    --auto-promote \
    --compare
```

## Troubleshooting

### Erreur: "Modèle v1 non trouvé"

```bash
# Créer un volume avec les artefacts baseline
docker run --rm \
  -v training-artifacts:/app/artifacts \
  -w /app/artifacts \
  alpine \
  ls -la

# Ou reconstruire v1
docker run --rm \
  -v $(pwd)/artifacts:/app/artifacts \
  training:latest \
  python -c "
import json
from pathlib import Path
Path('artifacts/v1').mkdir(parents=True, exist_ok=True)
# Créer metrics.json de baseline
json.dump({...}, open('artifacts/v1/metrics.json', 'w'))
"
```

### Logs non visibles

```bash
# Vérifier le montage
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  training:latest \
  ls -la /app/logs/

# Vérifier les permissions
chmod 777 logs/
```

### Container quitte immédiatement

```bash
# Voir les erreurs
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  training:latest \
  python -m src.training.train_v2

# Ou en mode interactif
docker run -it --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  training:latest \
  /bin/bash
```

## Performance

### Resource Limits

```bash
docker run --rm \
  --memory=2g \
  --cpus=2 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  training:latest
```

### Temps Estimé

- Training v2: 2-5 minutes (dépend de la taille du dataset)
- Comparaison: < 1 seconde
- Shadow deployment: Pas de temps supplémentaire
- Canary deployment: Pas de temps supplémentaire

## Scheduling (Cron-like)

```bash
# Script run_training.sh
#!/bin/bash
set -e

LOG_FILE="logs/training_$(date +%Y%m%d_%H%M%S).log"

docker run --rm \
  --log-driver local \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  -e DEPLOYMENT_STRATEGY=shadow \
  training:latest \
  python -m src.training.training_pipeline \
    --strategy shadow \
    --compare \
  | tee "$LOG_FILE"

echo "Training completed at $(date)" >> "$LOG_FILE"
```

Utilisation avec cron:

```bash
# Chaque jour à 2h du matin
0 2 * * * /app/scripts/run_training.sh
```

## Monitoring

### Healthcheck personnalisé

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "
    import json
    from pathlib import Path
    metrics = json.load(open('artifacts/v2/metrics.json'))
    assert metrics['accuracy'] > 0.7
    print('ok')
  "
```

### Logs avec ELK Stack (optionnel)

```bash
docker run --rm \
  --log-driver splunk \
  --log-opt splunk-token=<TOKEN> \
  --log-opt splunk-url=https://<HOST>:8088 \
  -v $(pwd)/artifacts:/app/artifacts \
  training:latest
```

## Résumé

✅ Image légère et optimisée  
✅ Volumes pour persistence  
✅ Support multi-stratégies  
✅ Logging complet  
✅ Health check intégré  
✅ Prêt pour production  

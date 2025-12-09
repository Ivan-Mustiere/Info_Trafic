import yaml

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

broker = config['ingest']['broker']
topics = config['ingest']['topics']

import json
import os
import pandas as pd

DEFAULT_CSV_SEP = ";"
DEFAULT_ENCODING = "utf-8"

def read_json(path):
    with open(path, "r", encoding=DEFAULT_ENCODING) as f:
        return json.load(f)

def write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=DEFAULT_ENCODING) as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_csv(path, sep=DEFAULT_CSV_SEP):
    return pd.read_csv(path, sep=sep)

def write_csv(df, path, sep=DEFAULT_CSV_SEP):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False, sep=sep)

import json
import os
import threading

# All JSON "tables" live in data/ by default; CH_DATA_DIR lets tests and demos use a copy.
DATA_DIR = os.getenv("CH_DATA_DIR", os.path.join(os.path.dirname(__file__), '..', 'data'))

# One lock for every read-modify-write on the JSON files (Flask serves requests in threads).
LOCK = threading.RLock()

def data_path(filename):
    return os.path.join(DATA_DIR, filename)

def load_json(filename, default):
    try:
        with open(data_path(filename), 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = data_path(filename) + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=4)
    os.replace(tmp, data_path(filename))

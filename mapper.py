# Datei: mapper.py
import json
import os

MAPPING_DIR = "mappings"

os.makedirs(MAPPING_DIR, exist_ok=True)

def list_all_track_mappings():
    return [f for f in os.listdir(MAPPING_DIR) if f.endswith(".json")]

def load_mapping(filename):
    path = os.path.join(MAPPING_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_mapping(filename, data):
    path = os.path.join(MAPPING_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Format:
# {
#   "track": "Dateiname.mp3",
#   "scenes": {
#       "Taverne": {"start": 60, "duration": 45},
#       "Wald": {"start": 120, "duration": 60}
#   }
# }

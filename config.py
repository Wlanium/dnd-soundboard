# config.py
import os
import sys
import shutil

# Basis-Verzeichnis: dort, wo die .exe liegt (auch bei PyInstaller --onefile korrekt)
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")

# Pfade, wie du sie willst:
ASSET_DIR = os.path.join(BASE_DIR, "assets")
ICON_DIR = os.path.join(ASSET_DIR, "icon")
HELP_DIR = os.path.join(ASSET_DIR, "hilfe")
MAPPING_DIR = os.path.join(BASE_DIR, "mappings")
FFMPEG_DIR = os.path.join(ASSET_DIR, "ffmpeg")

APP_TITLE = "D&D Soundboard"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

def ensure_dirs():
    """Erstellt nötige Ordner falls sie fehlen – aber NICHT aus _internal oder sonstwas."""
    for path in [ASSET_DIR, ICON_DIR, HELP_DIR, MAPPING_DIR, FFMPEG_DIR]:
        os.makedirs(path, exist_ok=True)

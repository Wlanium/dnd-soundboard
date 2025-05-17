import os
import json
import shutil
from PySide6.QtWidgets import QFileDialog, QMessageBox
from config import ASSET_DIR, MAPPING_DIR, ICON_DIR

def export_scenes(parent):
    """Exportiert alle Szenen, Tracks und Icons in ein ZIP-Archiv"""
    export_dir = QFileDialog.getExistingDirectory(parent, "Export-Verzeichnis wählen")
    if not export_dir:
        return
        
    # Sammle alle benötigten Dateien
    tracks_to_export = set()
    icons_to_export = set()
    mappings = {}
    
    # Durchsuche alle Mappings
    for filename in os.listdir(MAPPING_DIR):
        if not filename.endswith(".json"):
            continue
            
        with open(os.path.join(MAPPING_DIR, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            track = data.get("track")
            if track:
                tracks_to_export.add(track)
            mappings[filename] = data
            
            # Sammle Icons
            for scene in data.get("scenes", {}).values():
                icon = scene.get("icon")
                if icon:
                    icons_to_export.add(icon)
    
    # Erstelle Export-Struktur
    export_data = {
        "version": "1.0",
        "tracks": list(tracks_to_export),
        "mappings": mappings
    }
    
    # Speichere Export-Daten
    export_json = os.path.join(export_dir, "soundboard_export.json")
    with open(export_json, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=4)
    
    # Kopiere Tracks
    tracks_dir = os.path.join(export_dir, "tracks")
    os.makedirs(tracks_dir, exist_ok=True)
    for track in tracks_to_export:
        src = os.path.join(ASSET_DIR, track)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(tracks_dir, track))
    
    # Kopiere Icons
    icons_dir = os.path.join(export_dir, "icons")
    os.makedirs(icons_dir, exist_ok=True)
    for icon in icons_to_export:
        src = os.path.join(ICON_DIR, icon)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(icons_dir, icon))
    
    QMessageBox.information(parent, "Export erfolgreich", 
        f"Export abgeschlossen!\n\n"
        f"Verzeichnis: {export_dir}\n"
        f"Tracks: {len(tracks_to_export)}\n"
        f"Icons: {len(icons_to_export)}\n"
        f"Mappings: {len(mappings)}")

def import_scenes(parent):
    """Importiert Szenen aus einem Export-Verzeichnis"""
    import_dir = QFileDialog.getExistingDirectory(parent, "Import-Verzeichnis wählen")
    if not import_dir:
        return
        
    # Prüfe Export-Datei
    export_json = os.path.join(import_dir, "soundboard_export.json")
    if not os.path.exists(export_json):
        QMessageBox.critical(parent, "Fehler", "Keine gültige Export-Datei gefunden!")
        return
        
    try:
        with open(export_json, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
    except Exception as e:
        QMessageBox.critical(parent, "Fehler", f"Fehler beim Lesen der Export-Datei:\n{str(e)}")
        return
        
    # Prüfe Version
    if export_data.get("version") != "1.0":
        QMessageBox.critical(parent, "Fehler", "Nicht unterstützte Export-Version!")
        return
        
    # Kopiere Tracks
    tracks_dir = os.path.join(import_dir, "tracks")
    if os.path.exists(tracks_dir):
        for track in export_data.get("tracks", []):
            src = os.path.join(tracks_dir, track)
            if os.path.exists(src):
                dest = os.path.join(ASSET_DIR, track)
                if not os.path.exists(dest):
                    shutil.copy2(src, dest)
    
    # Kopiere Icons
    icons_dir = os.path.join(import_dir, "icons")
    if os.path.exists(icons_dir):
        for icon in os.listdir(icons_dir):
            src = os.path.join(icons_dir, icon)
            dest = os.path.join(ICON_DIR, icon)
            if not os.path.exists(dest):
                shutil.copy2(src, dest)
    
    # Importiere Mappings
    imported = 0
    for filename, data in export_data.get("mappings", {}).items():
        dest = os.path.join(MAPPING_DIR, filename)
        if not os.path.exists(dest):
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            imported += 1
    
    QMessageBox.information(parent, "Import erfolgreich",
        f"Import abgeschlossen!\n\n"
        f"Neue Mappings: {imported}\n"
        f"Tracks und Icons wurden nur kopiert, wenn sie noch nicht existierten.") 
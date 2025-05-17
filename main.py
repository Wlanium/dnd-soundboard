# Datei: main.py
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import os
from config import ensure_dirs

from config import ICON_DIR
from ui import SoundboardApp

def set_application_icon(app):
    """Setzt das App-Icon mit Fallback-Option"""
    # Haupticon versuchen
    icon_path = os.path.join(ICON_DIR, "app_icon.ico")
    
    # Fallback-Icon wenn Haupticon nicht existiert
    if not os.path.exists(icon_path):
        icon_path = os.path.join(ICON_DIR, "d&d.webp")
    
    # Icon setzen wenn vorhanden
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print("Warnung: Kein Icon gefunden!")

if __name__ == "__main__":
    ensure_dirs()
    app = QApplication([])
    app.setStyle("Fusion")

    # Icon setzen
    set_application_icon(app)

    window = SoundboardApp()
    window.show()

    app.exec()


# Die PySide6 GUI wird in "ui.py" ausgelagert.
# Audio-Logik und Mapping-Verwaltung folgen in separaten Modulen (audio.py, mapper.py etc.)

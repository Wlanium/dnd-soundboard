# Datei: main.py
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import os
from config import ensure_dirs

from config import ICON_DIR
from ui import SoundboardApp

if __name__ == "__main__":
    ensure_dirs()
    app = QApplication([])
    app.setStyle("Fusion")

    # Icon setzen
    icon_path = os.path.join(ICON_DIR, "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = SoundboardApp()
    window.show()

    app.exec()


# Die PySide6 GUI wird in "ui.py" ausgelagert.
# Audio-Logik und Mapping-Verwaltung folgen in separaten Modulen (audio.py, mapper.py etc.)

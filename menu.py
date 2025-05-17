# menu.py
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from track_manager import upload_track, delete_track
from scene_manager import create_scene, edit_scene, delete_scene
from help import HelpDialog
import shutil
import os
from config import FFMPEG_DIR
from yt_importer import YoutubeImportDialog, YoutubeBulkImportDialog

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_menu = QMenu("Datei", self)
        self.config_menu = QMenu("Konfig", self)
        self.help_menu = QMenu("Hilfe", self)

        self.addMenu(self.file_menu)
        self.addMenu(self.config_menu)

        self.file_menu.addAction("Track hochladen", lambda: upload_track(parent))
        self.file_menu.addAction("Track von YouTube holen", lambda: self.import_youtube_track(parent))
        self.file_menu.addAction("Bulk-YouTube-Import...", lambda: bulk_youtube_import(parent))
        self.file_menu.addAction("Track löschen", lambda: delete_track(parent))
        self.file_menu.addAction("Beenden", parent.close)

        self.config_menu.addAction("Szene erstellen", lambda: create_scene(parent))
        self.config_menu.addAction("Szene bearbeiten", lambda: edit_scene(parent))
        self.config_menu.addAction("Szene löschen", lambda: delete_scene(parent))

        self.help_menu.addAction("Anleitung anzeigen", lambda: HelpDialog(parent).exec())
        self.addMenu(self.help_menu)

    def import_youtube_track(self, parent):
        try:
            from yt_importer import YoutubeImportDialog
        except ImportError:
            QMessageBox.critical(parent, "Fehlender Code", "Modul 'yt_importer' nicht gefunden.")
            return

        # Prüfe FFmpeg-Installation
        required_files = ["ffmpeg.exe", "ffprobe.exe"]
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(FFMPEG_DIR, f))]
        
        if missing_files:
            QMessageBox.critical(parent, "FFmpeg fehlt", 
                f"Folgende FFmpeg-Dateien fehlen im assets/ffmpeg Ordner:\n"
                f"{', '.join(missing_files)}\n\n"
                "Bitte lade das komplette FFmpeg-Paket von https://ffmpeg.org/download.html herunter\n"
                "und entpacke alle Dateien in den assets/ffmpeg Ordner.")
            return

        try:
            YoutubeImportDialog("assets", parent).exec()
        except Exception as e:
            QMessageBox.critical(parent, "Fehler", f"Beim Import ist ein Fehler aufgetreten:\n{e}")

def bulk_youtube_import(parent):
    dlg = YoutubeBulkImportDialog(parent)
    dlg.exec()

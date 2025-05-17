# menu.py
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction
from track_manager import upload_track, delete_track
from scene_manager import create_scene, edit_scene, delete_scene
from help import HelpDialog
import shutil
import os
from config import FFMPEG_DIR
from yt_importer import YoutubeImportDialog, YoutubeBulkImportDialog
from scene_exporter import export_scenes, import_scenes
from streamdeck_config import StreamDeckConfigDialog

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
        self.file_menu.addSeparator()
        self.file_menu.addAction("Szenen exportieren...", lambda: export_scenes(parent))
        self.file_menu.addAction("Szenen importieren...", lambda: import_scenes(parent))
        self.file_menu.addSeparator()
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

def create_menu(parent):
    menubar = QMenuBar(parent)
    
    # Datei-Menü
    file_menu = menubar.addMenu("Datei")
    
    # Szenen-Menü
    scene_menu = menubar.addMenu("Szenen")
    
    # Track-Menü
    track_menu = menubar.addMenu("Tracks")
    
    # StreamDeck-Menü
    streamdeck_menu = menubar.addMenu("StreamDeck")
    
    # Datei-Menü Aktionen
    export_action = QAction("Szenen exportieren...", parent)
    export_action.triggered.connect(lambda: export_scenes(parent))
    file_menu.addAction(export_action)
    
    import_action = QAction("Szenen importieren...", parent)
    import_action.triggered.connect(lambda: import_scenes(parent))
    file_menu.addAction(import_action)
    
    file_menu.addSeparator()
    
    exit_action = QAction("Beenden", parent)
    exit_action.triggered.connect(parent.close)
    file_menu.addAction(exit_action)
    
    # Szenen-Menü Aktionen
    create_action = QAction("Neue Szene", parent)
    create_action.triggered.connect(lambda: create_scene(parent))
    scene_menu.addAction(create_action)
    
    edit_action = QAction("Szene bearbeiten", parent)
    edit_action.triggered.connect(lambda: edit_scene(parent))
    scene_menu.addAction(edit_action)
    
    delete_action = QAction("Szene löschen", parent)
    delete_action.triggered.connect(lambda: delete_scene(parent))
    scene_menu.addAction(delete_action)
    
    # Track-Menü Aktionen
    upload_action = QAction("Track hochladen", parent)
    upload_action.triggered.connect(lambda: upload_track(parent))
    track_menu.addAction(upload_action)
    
    delete_track_action = QAction("Track löschen", parent)
    delete_track_action.triggered.connect(lambda: delete_track(parent))
    track_menu.addAction(delete_track_action)
    
    # StreamDeck-Menü Aktionen
    config_action = QAction("StreamDeck konfigurieren...", parent)
    config_action.triggered.connect(lambda: StreamDeckConfigDialog(parent).exec())
    streamdeck_menu.addAction(config_action)
    
    # Hilfe-Menü
    help_menu = menubar.addMenu("Hilfe")
    help_action = QAction("Anleitung anzeigen", parent)
    help_action.triggered.connect(lambda: HelpDialog(parent).exec())
    help_menu.addAction(help_action)
    
    return menubar

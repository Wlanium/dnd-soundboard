import os
import json
import yt_dlp
import shutil
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from config import MAPPING_DIR

class YoutubeDownloadWorker(QThread):
    progress_changed = Signal(int)
    download_finished = Signal(bool, str, str)

    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.downloaded_file = None

    def run(self):
        try:
            def hook(d):
                if d['status'] == 'downloading':
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded_bytes = d.get('downloaded_bytes')
                    if total_bytes and downloaded_bytes:
                        percent = int(downloaded_bytes / total_bytes * 100)
                        self.progress_changed.emit(percent)
                elif d['status'] == 'finished':
                    self.progress_changed.emit(100)
                    self.downloaded_file = d.get('filename')

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [hook],
                'noplaylist': True,
                'verbose': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            # Fortschritt auf 100% setzen nach Konvertierung
            self.progress_changed.emit(100)

            # Original entfernen, falls MP3 erstellt wurde
            if self.downloaded_file:
                raw_path = self.downloaded_file
                mp3_path = os.path.splitext(raw_path)[0] + ".mp3"
                if os.path.exists(mp3_path) and os.path.exists(raw_path) and raw_path != mp3_path:
                    try:
                        os.remove(raw_path)
                    except Exception as e:
                        print(f"[WARN] Konnte Original nicht löschen: {e}")
                self.downloaded_file = mp3_path

            self.download_finished.emit(True, "Download abgeschlossen.", self.downloaded_file)
        except Exception as e:
            self.download_finished.emit(False, str(e), "")

class YoutubeImportDialog(QDialog):
    def __init__(self, asset_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube-Track importieren")
        self.setMinimumWidth(400)
        self.asset_dir = asset_dir

        layout = QVBoxLayout()

        layout.addWidget(QLabel("YouTube-Link:"))
        self.link_input = QLineEdit()
        layout.addWidget(self.link_input)

        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.import_btn = QPushButton("Download starten")
        self.import_btn.clicked.connect(self.start_download)
        layout.addWidget(self.import_btn)

        self.setLayout(layout)

    def start_download(self):
        url = self.link_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Fehler", "Bitte gib einen gültigen YouTube-Link ein.")
            return

        self.import_btn.setEnabled(False)
        self.worker = YoutubeDownloadWorker(url, self.asset_dir)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.download_finished.connect(self.on_download_finished)
        self.worker.start()

    def on_download_finished(self, success, message, filepath):
        self.import_btn.setEnabled(True)
        if success:
            filename = os.path.basename(filepath)
            json_path = os.path.join(MAPPING_DIR, os.path.splitext(filename)[0] + ".json")
            if not os.path.exists(json_path):
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump({"track": filename, "scenes": {}}, f, indent=4)

            QMessageBox.information(self, "Erfolg", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Fehler", f"Download fehlgeschlagen:\n{message}")
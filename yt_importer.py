import os
import json
import yt_dlp
import shutil
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from config import MAPPING_DIR, FFMPEG_DIR, ASSET_DIR

class YoutubeDownloadWorker(QThread):
    progress_changed = Signal(int)
    download_status = Signal(str)
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
                        self.download_status.emit("Download läuft...")
                elif d['status'] == 'finished':
                    self.progress_changed.emit(100)
                    self.download_status.emit("Konvertierung läuft, bitte warten...")
                    self.downloaded_file = d.get('filename')

            # FFmpeg-Pfad konfigurieren
            ffmpeg_path = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
            if not os.path.exists(ffmpeg_path):
                raise FileNotFoundError("FFmpeg nicht gefunden. Bitte FFmpeg im assets/ffmpeg Ordner installieren.")

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
                'verbose': True,
                'ffmpeg_location': FFMPEG_DIR  # FFmpeg-Pfad setzen
            }

            # Prüfe verfügbaren Speicherplatz
            free_space = shutil.disk_usage(self.output_path).free
            if free_space < 500 * 1024 * 1024:  # 500MB Minimum
                raise OSError("Nicht genug Speicherplatz. Mindestens 500MB erforderlich.")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            # Fortschritt auf 100% setzen nach Konvertierung
            self.progress_changed.emit(100)
            self.download_status.emit("Konvertierung läuft, bitte warten...")

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

            self.download_status.emit("Track erstellt!")
            self.download_finished.emit(True, "Download abgeschlossen.", self.downloaded_file)
        except Exception as e:
            self.download_status.emit("Fehler beim Download/Konvertieren!")
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

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

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
        self.worker.download_status.connect(self.set_status)
        self.worker.download_finished.connect(self.on_download_finished)
        self.worker.start()

    def set_status(self, text):
        self.status_label.setText(text)
        if "Konvertierung läuft" in text:
            self.progress.setRange(0, 0)
        elif "Track erstellt" in text or "Fehler" in text:
            self.progress.setRange(0, 100)

    def on_download_finished(self, success, message, filepath):
        self.import_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        if success:
            filename = os.path.basename(filepath)
            json_path = os.path.join(MAPPING_DIR, os.path.splitext(filename)[0] + ".json")
            if not os.path.exists(json_path):
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump({"track": filename, "scenes": {}}, f, indent=4)

            self.set_status("Track erstellt!")
            QMessageBox.information(self, "Erfolg", message)
            self.accept()
        else:
            self.set_status("Fehler beim Download/Konvertieren!")
            QMessageBox.critical(self, "Fehler", f"Download fehlgeschlagen:\n{message}")

class YoutubeBulkImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk-YouTube-Import")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Füge mehrere YouTube-Links ein (jeweils einer pro Zeile):"))

        self.links_edit = QTextEdit()
        self.links_edit.setPlaceholderText("https://youtube.com/...")
        layout.addWidget(self.links_edit)

        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.start_btn = QPushButton("Bulk-Import starten")
        self.start_btn.clicked.connect(self.start_bulk_import)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)
        self.worker = None

    def start_bulk_import(self):
        links = [l.strip() for l in self.links_edit.toPlainText().splitlines() if l.strip()]
        if not links:
            QMessageBox.warning(self, "Fehler", "Bitte gib mindestens einen YouTube-Link ein.")
            return
        self.start_btn.setEnabled(False)
        self.progress.setMaximum(len(links))
        self.progress.setValue(0)
        self.worker = YoutubeBulkWorker(links, self)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_bulk_finished)
        self.worker.start()

    def on_bulk_finished(self, results):
        self.start_btn.setEnabled(True)
        errors = [r for r in results if not r[0]]
        if not errors:
            QMessageBox.information(self, "Fertig", "Alle Dateien wurden erfolgreich importiert!")
        else:
            msg = "Folgende Links konnten nicht importiert werden:\n\n"
            for ok, link, err in errors:
                msg += f"{link}\nFehler: {err}\n\n"
            QMessageBox.warning(self, "Fehler beim Import", msg)
        self.accept()

class YoutubeBulkWorker(QThread):
    progress_changed = Signal(int)
    finished = Signal(list)  # Liste von (ok, link, err)

    def __init__(self, links, parent=None):
        super().__init__(parent)
        self.links = links
        self.results = []

    def run(self):
        for idx, link in enumerate(self.links, 1):
            try:
                # Reuse Einzelimport-Worker synchron
                worker = YoutubeDownloadWorker(link, ASSET_DIR)
                worker.run()  # synchron!
                self.results.append((True, link, None))
            except Exception as e:
                self.results.append((False, link, str(e)))
            self.progress_changed.emit(idx)
        self.finished.emit(self.results)
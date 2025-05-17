# track_manager.py

import os
import json
import shutil
from PySide6.QtWidgets import (
    QFileDialog, QMessageBox, QDialog, QVBoxLayout, QListWidget,
    QPushButton, QHBoxLayout, QLabel
)
from send2trash import send2trash
from config import ASSET_DIR, MAPPING_DIR
from mapper import load_mapping


def upload_track(parent):
    file_path, _ = QFileDialog.getOpenFileName(parent, "Track auswählen", ASSET_DIR, "Audio (*.mp3 *.mp4)")
    if not file_path:
        return None

    filename = os.path.basename(file_path)
    dest_path = os.path.join(ASSET_DIR, filename)

    if os.path.exists(dest_path):
        QMessageBox.information(parent, "Schon vorhanden", f"Die Datei '{filename}' ist bereits im Soundboard.")
        return None

    # Datei kopieren
    shutil.copy(file_path, dest_path)

    # Leeres Mapping erstellen, wenn nicht vorhanden
    #mapping_path = os.path.join(MAPPING_DIR, os.path.splitext(filename)[0] + ".json")
    json_path = os.path.join(MAPPING_DIR, os.path.splitext(filename)[0] + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"track": filename, "scenes": {}}, f, indent=4)

    return filename


def delete_track(parent):
    tracks = os.listdir(ASSET_DIR)
    if not tracks:
        QMessageBox.information(parent, "Info", "Keine Tracks vorhanden.")
        return

    dlg = TrackDeleteDialog(parent, tracks)
    dlg.exec()


class TrackDeleteDialog(QDialog):
    def __init__(self, parent, tracks):
        super().__init__(parent)
        self.setWindowTitle("Track löschen")
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wähle Track zum Löschen:"))

        self.list = QListWidget()
        self.list.addItems(tracks)
        layout.addWidget(self.list)

        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Löschen")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_selected)
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.list.currentItemChanged.connect(self.toggle_delete)

    def toggle_delete(self):
        self.delete_btn.setEnabled(self.list.currentItem() is not None)

    def delete_selected(self):
        selected_item = self.list.currentItem()
        if not selected_item:
            return

        filename = selected_item.text()
        base_name = os.path.splitext(filename)[0]
        track_path = os.path.join(ASSET_DIR, filename)
        json_path = os.path.join(MAPPING_DIR, base_name + ".json")

        # Prüfen auf Szenen
        if os.path.exists(json_path):
            data = load_mapping(base_name + ".json")
            scenes = data.get("scenes", {})
            if scenes:
                res = QMessageBox.question(
                    self,
                    "Szenen gefunden",
                    f"Der Track '{base_name}' enthält noch {len(scenes)} Szenen.\n"
                    "Möchtest du diese automatisch löschen und den Track entfernen?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if res != QMessageBox.Yes:
                    return

        # Datei in den Müll
        if os.path.exists(track_path):
            send2trash(track_path)
        if os.path.exists(json_path):
            send2trash(json_path)

        QMessageBox.information(self, "Erledigt", f"Track '{filename}' wurde inklusive aller Daten gelöscht.")
        self.accept()
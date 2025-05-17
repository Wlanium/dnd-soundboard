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
from PySide6.QtCore import Qt


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
    tracks = [f for f in os.listdir(ASSET_DIR) if f.lower().endswith('.mp3')]
    if not tracks:
        QMessageBox.information(parent, "Info", "Keine MP3-Tracks vorhanden.")
        return

    dlg = TrackDeleteDialog(parent, tracks)
    dlg.exec()


class TrackDeleteDialog(QDialog):
    def __init__(self, parent, tracks):
        super().__init__(parent)
        self.setWindowTitle("Track löschen")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)  # Höhe separat setzen

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wähle Track(s) zum Löschen:"))

        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.MultiSelection)  # Mehrfachauswahl erlauben
        layout.addWidget(self.list)

        # Prüfe für jeden Track, ob er noch in Szenen verwendet wird
        for track in tracks:
            base_name = os.path.splitext(track)[0]
            json_path = os.path.join(MAPPING_DIR, base_name + ".json")
            item_text = track
            item = self.list.addItem(item_text)
            used = False
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        scenes = data.get("scenes", {})
                        if scenes:
                            used = True
                except Exception:
                    pass
            if used:
                list_item = self.list.item(self.list.count()-1)
                list_item.setFlags(list_item.flags() & ~Qt.ItemIsEnabled)  # Nicht auswählbar
                list_item.setForeground(Qt.gray)
                list_item.setToolTip("Track wird noch in einer Szene verwendet und kann nicht gelöscht werden.")

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
        self.list.itemSelectionChanged.connect(self.toggle_delete)

    def toggle_delete(self):
        # Mindestens ein auswählbares Item muss selektiert sein
        items = self.list.selectedItems()
        self.delete_btn.setEnabled(any(item.flags() & Qt.ItemIsEnabled for item in items))

    def delete_selected(self):
        selected_items = [item for item in self.list.selectedItems() if item.flags() & Qt.ItemIsEnabled]
        if not selected_items:
            return
        deleted = []
        for selected_item in selected_items:
            filename = selected_item.text()
            base_name = os.path.splitext(filename)[0]
            track_path = os.path.join(ASSET_DIR, filename)
            json_path = os.path.join(MAPPING_DIR, base_name + ".json")
            # Datei in den Müll
            if os.path.exists(track_path):
                send2trash(track_path)
            if os.path.exists(json_path):
                send2trash(json_path)
            deleted.append(filename)
        QMessageBox.information(
            self,
            "Erledigt",
            f"{len(deleted)} Track(s) wurden inklusive aller Daten gelöscht:\n" + "\n".join(deleted)
        )
        self.accept()
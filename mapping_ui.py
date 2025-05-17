# mapping_ui.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QComboBox, QGridLayout, QButtonGroup, QToolButton, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize, Qt
import os
from config import MAPPING_DIR, ICON_DIR

class MappingDialog(QDialog):
    def __init__(self, default_name="", default_start=0.0, default_duration=60.0, default_icon=""):
        super().__init__()
        self.selected_icon = default_icon
        self.setWindowTitle("Szene hinzufügen")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Hilfsfunktion zur Zeitformatierung
        def format_seconds(seconds):
            if seconds >= 3600:
                return f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02}"
            elif seconds >= 60:
                return f"{int(seconds // 60):02}:{int(seconds % 60):02}"
            else:
                return str(seconds)

        # Track-Auswahl – endlich sichtbar!
        self.track_combo = QComboBox()
        self.track_map = {
            os.path.splitext(f)[0]: f for f in os.listdir(MAPPING_DIR)
            if f.endswith(".json")
        }
        self.track_combo.addItems(self.track_map.keys())
        layout.addWidget(QLabel("Track:"))
        layout.addWidget(self.track_combo)

        # Szenenname
        self.name_input = QLineEdit()
        self.name_input.setText(default_name)
        layout.addWidget(QLabel("Szenenname:"))
        layout.addWidget(self.name_input)

        # Startzeit
        self.start_input = QLineEdit()
        self.start_input.setText(format_seconds(default_start))
        self.start_input.setPlaceholderText("Sekunden oder hh:mm:ss")
        layout.addWidget(QLabel("Startzeit:"))
        layout.addWidget(self.start_input)

        # Dauer
        self.duration_input = QLineEdit()
        self.duration_input.setText(format_seconds(default_duration))
        self.duration_input.setPlaceholderText("Sekunden oder mm:ss")
        layout.addWidget(QLabel("Dauer:"))
        layout.addWidget(self.duration_input)

        # Icon-Auswahl
        icons = [
            f for f in os.listdir(ICON_DIR)
            if f.endswith((".png", ".webp"))
        ]
        self.icon_combo = QComboBox()
        self.icon_combo.addItems(["--- Kein Icon ---"] + icons)
        if default_icon:
            self.icon_combo.setCurrentText(default_icon)
        layout.addWidget(QLabel("Icon (optional):"))
        layout.addWidget(self.icon_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def set_selected_icon(self, btn):
        self.selected_icon = btn.icon_name

    def get_data(self):
        def parse_time_input(text):
            if ":" in text:
                parts = list(map(int, text.strip().split(":")))
                if len(parts) == 2:
                    minutes, seconds = parts
                    return minutes * 60 + seconds
                elif len(parts) == 3:
                    hours, minutes, seconds = parts
                    return hours * 3600 + minutes * 60 + seconds
                else:
                    raise ValueError("Ungültiges Zeitformat.")
            else:
                return float(text)

        selected_track_label = self.track_combo.currentText()
        mapping_file = self.track_map[selected_track_label]
        name = self.name_input.text()

        try:
            start = parse_time_input(self.start_input.text())
            duration = parse_time_input(self.duration_input.text())
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Ungültiges Zeitformat. Erlaubt sind Sekunden oder mm:ss bzw. hh:mm:ss.")
            raise

        icon = self.icon_combo.currentText()
        if icon == "--- Kein Icon ---":
            icon = ""

        return mapping_file, name, start, duration, icon

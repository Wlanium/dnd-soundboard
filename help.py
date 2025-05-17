# help.py

import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
from config import ASSET_DIR

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hilfe & Anleitung")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        info_label = QLabel("Benutzeranleitung für das D&D Soundboard")
        info_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(info_label)

        self.textbox = QTextEdit()
        self.textbox.setReadOnly(True)
        layout.addWidget(self.textbox)

        self.setLayout(layout)
        self.load_help_text()

    def load_help_text(self):
        help_path = os.path.join(ASSET_DIR, "hilfe/hilfe.md")
        if os.path.exists(help_path):
            with open(help_path, encoding="utf-8") as f:
                self.textbox.setPlainText(f.read())
        else:
            self.textbox.setPlainText("Keine Hilfe-Datei gefunden. Lege eine Datei 'hilfe.md' im assets-Verzeichnis an.")

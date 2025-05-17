from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
import json
import os
from config import MAPPING_DIR

class StreamDeckConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("StreamDeck Konfiguration")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # StreamDeck-Status
        status_group = QGroupBox("StreamDeck Status")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("StreamDeck nicht verbunden")
        self.status_label.setStyleSheet("color: red;")
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # StreamDeck-Auswahl
        device_group = QGroupBox("StreamDeck auswählen")
        device_layout = QVBoxLayout()
        self.device_combo = QComboBox()
        self.device_combo.addItem("Kein StreamDeck gefunden")
        device_layout.addWidget(self.device_combo)
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Einstellungen
        settings_group = QGroupBox("Einstellungen")
        settings_layout = QVBoxLayout()
        
        self.auto_connect = QCheckBox("Beim Start automatisch verbinden")
        self.auto_connect.setChecked(True)
        settings_layout.addWidget(self.auto_connect)
        
        self.show_icons = QCheckBox("Icons auf StreamDeck anzeigen")
        self.show_icons.setChecked(True)
        settings_layout.addWidget(self.show_icons)
        
        self.show_names = QCheckBox("Namen auf StreamDeck anzeigen")
        self.show_names.setChecked(True)
        settings_layout.addWidget(self.show_names)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("StreamDeck suchen")
        self.scan_btn.clicked.connect(self.scan_devices)
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.save_and_close)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_config()
        self.scan_devices()
        
    def load_config(self):
        """Lädt die gespeicherte Konfiguration"""
        config_file = os.path.join(MAPPING_DIR, "streamdeck_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.auto_connect.setChecked(config.get('auto_connect', True))
                    self.show_icons.setChecked(config.get('show_icons', True))
                    self.show_names.setChecked(config.get('show_names', True))
            except Exception:
                pass
                
    def save_config(self):
        """Speichert die Konfiguration"""
        config = {
            'auto_connect': self.auto_connect.isChecked(),
            'show_icons': self.show_icons.isChecked(),
            'show_names': self.show_names.isChecked(),
            'selected_device': self.device_combo.currentText()
        }
        
        config_file = os.path.join(MAPPING_DIR, "streamdeck_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
    def scan_devices(self):
        """Sucht nach verbundenen StreamDeck-Geräten"""
        try:
            from StreamDeck.DeviceManager import DeviceManager
            devices = DeviceManager().enumerate()
            
            self.device_combo.clear()
            if devices:
                for device in devices:
                    self.device_combo.addItem(f"{device.deck_type()} - {device.serial_number()}")
                self.status_label.setText("StreamDeck gefunden")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.device_combo.addItem("Kein StreamDeck gefunden")
                self.status_label.setText("StreamDeck nicht verbunden")
                self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            self.device_combo.clear()
            self.device_combo.addItem("Fehler beim Scannen")
            self.status_label.setText(f"Fehler: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            
    def save_and_close(self):
        """Speichert die Konfiguration und schließt den Dialog"""
        self.save_config()
        self.accept() 
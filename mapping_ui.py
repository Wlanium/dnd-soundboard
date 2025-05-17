# mapping_ui.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QComboBox, QGridLayout, QButtonGroup, QToolButton, QMessageBox, QWidget, QSizePolicy, QScrollArea, QFileDialog
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize, Qt
import os
import json
from config import MAPPING_DIR, ICON_DIR
from PIL import Image

def parse_time_input(text):
    """Konvertiert Zeit-String in Sekunden.
    Unterstützt: Sekunden, mm:ss, hh:mm:ss"""
    text = text.strip()
    
    # Wenn nur Zahlen, dann Sekunden
    if text.isdigit():
        return float(text)
    
    # Prüfe auf mm:ss oder hh:mm:ss Format
    if ":" in text:
        parts = text.split(":")
        if len(parts) == 2:  # mm:ss
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # hh:mm:ss
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
    
    raise ValueError("Ungültiges Zeitformat. Erlaubt sind: Sekunden, mm:ss, hh:mm:ss")

def format_seconds(seconds):
    """Formatiert Sekunden in lesbares Format"""
    seconds = int(seconds)
    if seconds >= 3600:
        return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"
    elif seconds >= 60:
        return f"{seconds // 60:02}:{seconds % 60:02}"
    else:
        return str(seconds)

class IconGridWidget(QWidget):
    def __init__(self, icons, default_icon="", parent=None):
        super().__init__(parent)
        self.selected_icon = default_icon
        self.icons = icons
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        grid = QGridLayout()
        grid.setSpacing(8)
        size = 48
        col_count = 5
        # Kein Icon Button
        btn_none = QToolButton()
        btn_none.setIcon(QIcon())
        btn_none.setIconSize(QSize(size, size))
        btn_none.setCheckable(True)
        btn_none.setChecked(default_icon == "")
        btn_none.setToolTip("Kein Icon")
        btn_none.icon_name = ""
        self.btn_group.addButton(btn_none)
        grid.addWidget(btn_none, 0, 0)
        # Icon Buttons
        row, col = 0, 1
        for icon in icons:
            try:
                icon_path = os.path.join(ICON_DIR, icon)
                if not os.path.isfile(icon_path):
                    continue
                pix = QPixmap(icon_path)
                if pix.isNull():
                    raise Exception(f"Icon {icon} konnte nicht geladen werden!")
                pix = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                btn = QToolButton()
                btn.setIcon(QIcon(pix))
                btn.setIconSize(QSize(size, size))
                btn.setCheckable(True)
                btn.setToolTip(icon)
                btn.icon_name = icon
                if icon == default_icon:
                    btn.setChecked(True)
                self.btn_group.addButton(btn)
                grid.addWidget(btn, row, col)
                col += 1
                if col >= col_count:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"[WARN] {e}")
        self.setLayout(grid)
        self.btn_group.buttonClicked.connect(self.on_icon_selected)
    def on_icon_selected(self, btn):
        self.selected_icon = btn.icon_name
    def get_selected_icon(self):
        return self.selected_icon

class IconUploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Icons hochladen")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wähle ein oder mehrere Bilddateien zum Hochladen aus. Sie werden automatisch als .webp gespeichert."))
        self.upload_btn = QPushButton("Icons auswählen und hochladen")
        self.upload_btn.clicked.connect(self.upload_icons)
        layout.addWidget(self.upload_btn)
        self.setLayout(layout)
        self.success = False
    def upload_icons(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Icons auswählen", "", "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not files:
            return
        errors = []
        for file in files:
            try:
                img = Image.open(file).convert("RGBA")
                # Optional: auf 512x512 skalieren und zentrieren
                size = 512
                bg = Image.new("RGBA", (size, size), (0,0,0,0))
                img.thumbnail((size, size), Image.LANCZOS)
                x = (size - img.width) // 2
                y = (size - img.height) // 2
                bg.paste(img, (x, y), img if img.mode == "RGBA" else None)
                name = os.path.splitext(os.path.basename(file))[0] + ".webp"
                bg.save(os.path.join(ICON_DIR, name), "WEBP")
            except Exception as e:
                errors.append(f"{file}: {e}")
        if errors:
            QMessageBox.warning(self, "Fehler", "Einige Icons konnten nicht konvertiert werden:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "Erfolg", "Alle Icons wurden erfolgreich hochgeladen und konvertiert!")
            self.success = True
        self.accept()

class MappingDialog(QDialog):
    def __init__(self, default_name="", default_start=0.0, default_duration=60.0, default_icon=""):
        super().__init__()
        self.selected_icon = default_icon
        self.setWindowTitle("Szene hinzufügen")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Track-Auswahl
        self.track_combo = QComboBox()
        self.track_map = {
            os.path.splitext(f)[0]: f for f in os.listdir(MAPPING_DIR)
            if f.endswith(".json")
        }
        self.track_combo.addItems(self.track_map.keys())
        self.track_combo.currentTextChanged.connect(self.on_track_changed)
        layout.addWidget(QLabel("Track:"))
        layout.addWidget(self.track_combo)

        # Szenenname
        self.name_input = QLineEdit()
        self.name_input.setText(default_name)
        layout.addWidget(QLabel("Szenenname:"))
        layout.addWidget(self.name_input)

        # Zeitformat-Hinweis
        time_hint = QLabel("Zeitformat: Sekunden (z.B. 45) oder mm:ss (z.B. 1:30) oder hh:mm:ss (z.B. 1:30:00)")
        time_hint.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(time_hint)

        # Startzeit (ohne Min-Button)
        self.start_input = QLineEdit()
        self.start_input.setText(format_seconds(default_start))
        self.start_input.setPlaceholderText("Sekunden oder mm:ss oder hh:mm:ss")
        layout.addWidget(QLabel("Startzeit:"))
        layout.addWidget(self.start_input)

        # Dauer (ohne Max-Button)
        self.duration_input = QLineEdit()
        self.duration_input.setText(format_seconds(default_duration))
        self.duration_input.setPlaceholderText("Sekunden oder mm:ss")
        layout.addWidget(QLabel("Dauer:"))
        layout.addWidget(self.duration_input)

        # Icon-Auswahl als Grid + Upload-Button
        layout.addWidget(QLabel("Icon (optional):"))
        icon_row = QHBoxLayout()
        layout.addLayout(icon_row)
        self.setLayout(layout)  # Layout VOR refresh_icon_grid setzen!
        self.refresh_icon_grid(default_icon)
        icon_row.addWidget(self.icon_scroll)
        upload_btn = QToolButton()
        upload_btn.setIcon(QIcon.fromTheme("document-open"))
        upload_btn.setText("+")
        upload_btn.setToolTip("Icons hochladen")
        upload_btn.setFixedSize(32,32)
        upload_btn.clicked.connect(self.open_icon_upload)
        icon_row.addWidget(upload_btn)

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
        
        # Initial Track-Länge laden
        self.on_track_changed(self.track_combo.currentText())

    def on_track_changed(self, track_name):
        """Lädt die Track-Länge wenn sich der Track ändert"""
        if not track_name:
            return
            
        mapping_file = os.path.join(MAPPING_DIR, self.track_map[track_name])
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.track_duration = data.get('duration', 0)
        except Exception as e:
            print(f"Fehler beim Laden der Track-Länge: {e}")
            self.track_duration = 0

    def refresh_icon_grid(self, default_icon=None):
        icons = [
            f for f in os.listdir(ICON_DIR)
            if f.endswith(".webp")
        ]
        # Entferne alte ScrollArea aus Layout
        if hasattr(self, 'icon_scroll') and self.icon_scroll is not None:
            parent_layout = self.icon_scroll.parentWidget().layout() if self.icon_scroll.parentWidget() else None
            if parent_layout:
                parent_layout.removeWidget(self.icon_scroll)
            self.icon_scroll.deleteLater()
            self.icon_scroll = None
        self.icon_grid = IconGridWidget(icons, default_icon or self.selected_icon)
        self.icon_scroll = QScrollArea()
        self.icon_scroll.setWidgetResizable(True)
        self.icon_scroll.setWidget(self.icon_grid)
        self.icon_scroll.setFixedHeight(80)
        # Füge neue ScrollArea ins Layout ein
        # Suche das icon_row Layout
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                # Entferne alle alten Widgets aus icon_row
                while item.count():
                    w = item.takeAt(0).widget()
                    if w:
                        w.setParent(None)
                item.addWidget(self.icon_scroll)
                # Upload-Button wieder hinzufügen
                upload_btn = QToolButton()
                upload_btn.setIcon(QIcon.fromTheme("document-open"))
                upload_btn.setText("+")
                upload_btn.setToolTip("Icons hochladen")
                upload_btn.setFixedSize(32,32)
                upload_btn.clicked.connect(self.open_icon_upload)
                item.addWidget(upload_btn)
                break
        self.icon_scroll.update()
        self.icon_grid.update()
        self.update()

    def open_icon_upload(self):
        dlg = IconUploadDialog(self)
        if dlg.exec() and dlg.success:
            self.refresh_icon_grid()
            self.layout().update()

    def get_data(self):
        selected_track_label = self.track_combo.currentText()
        mapping_file = self.track_map[selected_track_label]
        name = self.name_input.text()

        try:
            start = parse_time_input(self.start_input.text())
            duration = parse_time_input(self.duration_input.text())
        except ValueError as e:
            QMessageBox.warning(self, "Fehler", str(e))
            raise

        icon = self.icon_grid.get_selected_icon()
        return mapping_file, name, start, duration, icon

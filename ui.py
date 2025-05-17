import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QMenu, QPushButton, QLabel, QHBoxLayout, QGridLayout, QSizePolicy,
    QInputDialog, QMainWindow, QScrollArea, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon, QKeySequence, QAction
from PySide6.QtCore import Qt, QTimer, QSize
from audio import play_loop_segment, stop_playback
from mapper import load_mapping, list_all_track_mappings
from menu import MenuBar, create_menu
from config import ASSET_DIR, APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, ICON_DIR
from hotkey_manager import HotkeyManager
from scene_manager import create_scene, edit_scene, delete_scene
from track_manager import upload_track, delete_track
from streamdeck_manager import StreamDeckManager

def get_scene_button_style(is_active=False):
    return f"""
        QPushButton {{
            text-align: center;
            padding-top: 10px;
            padding-bottom: 5px;
            border: 2px solid {"#FFD700" if is_active else "#444"};
            border-radius: 10px;
            background-color: {"#4b4b4b" if is_active else "#3c3c3c"};
            color: white;
        }}
        QPushButton:hover {{
            background-color: #606060;
            border: 2px solid {"#FFD700" if is_active else "#777"};
        }}
    """

def make_context_menu(button, mapping_file, scene_name, main_window):
    def contextMenuEvent(event):
        menu = QMenu()
        
        # Aktuelle Szene ist aktiv
        is_active = (main_window.current_scene_name == scene_name and main_window.current_playing)
        
        # Play/Pause Aktion
        if is_active:
            if main_window.is_paused:
                action_play = menu.addAction("Weiter")
            else:
                action_play = menu.addAction("Pause")
        else:
            action_play = menu.addAction("Abspielen")
        
        menu.addSeparator()
        action_edit = menu.addAction("Szene bearbeiten")
        action_delete = menu.addAction("Szene löschen")
        
        # Hotkey-Menü
        hotkey_menu = menu.addMenu("Hotkey")
        current_key = main_window.hotkey_manager.hotkeys.get(mapping_file, {}).get(scene_name, "")
        if current_key:
            hotkey_menu.addAction(f"Aktuell: {current_key}")
            hotkey_menu.addAction("Entfernen", lambda: main_window.remove_hotkey(mapping_file, scene_name))
        hotkey_menu.addAction("Neuer Hotkey...", lambda: main_window.set_hotkey(mapping_file, scene_name))
        
        action = menu.exec(event.globalPos())
        if action == action_play:
            if is_active:
                main_window.pause_playback()
            else:
                data = load_mapping(mapping_file)
                scene = data["scenes"][scene_name]
                main_window.play_scene(data["track"], scene, scene_name)
        elif action == action_edit:
            from scene_manager import edit_specific_scene
            edit_specific_scene(main_window, mapping_file, scene_name)
            main_window.load_all_scenes()
        elif action == action_delete:
            from scene_manager import delete_specific_scene
            delete_specific_scene(main_window, mapping_file, scene_name)
            main_window.load_all_scenes()
    button.contextMenuEvent = contextMenuEvent

class SoundboardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D&D Soundboard")
        self.setMinimumSize(800, 600)
        
        # StreamDeck-Manager initialisieren
        self.streamdeck = StreamDeckManager()
        self.streamdeck.button_pressed.connect(self.trigger_scene_by_id)
        
        # UI aufbauen
        self.setup_ui()
        
        # StreamDeck verbinden wenn auto_connect aktiviert
        if self.streamdeck.config.get('auto_connect', True):
            success, message = self.streamdeck.connect_device()
            if not success:
                QMessageBox.warning(self, "StreamDeck", message)
                
    def setup_ui(self):
        # Menü erstellen
        self.setMenuBar(create_menu(self))
        
        # Hauptwidget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Szenen-Container
        self.scenes_container = QWidget()
        self.scenes_layout = QGridLayout()
        self.scenes_layout.setSpacing(16)
        self.scenes_container.setLayout(self.scenes_layout)
        
        # ScrollArea für Szenen
        scroll = QScrollArea()
        scroll.setWidget(self.scenes_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Status-Bar
        self.statusBar().showMessage("Bereit")
        
        self.current_track = None
        self.current_scene_name = None
        self.current_start = 0
        self.current_duration = 0
        self.current_playing = False
        self.is_paused = False
        self.elapsed = 0

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_time)

        # Hotkey-Manager initialisieren
        self.hotkey_manager = HotkeyManager(self)
        self.hotkey_manager.scene_triggered.connect(self.trigger_scene_by_hotkey)

        self.load_all_scenes()

        # Steuerungs-Buttons
        control_layout = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_playback)
        self.stop_btn = QPushButton("Stopp")
        self.stop_btn.clicked.connect(self.stop_playback)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)

    def trigger_scene_by_hotkey(self, mapping_file, scene_name):
        """Wird aufgerufen, wenn ein Hotkey gedrückt wird"""
        data = load_mapping(mapping_file)
        if scene_name in data.get("scenes", {}):
            scene = data["scenes"][scene_name]
            self.play_scene(data["track"], scene, scene_name)

    def set_hotkey(self, mapping_file, scene_name):
        """Öffnet Dialog zum Setzen eines Hotkeys"""
        current = self.hotkey_manager.hotkeys.get(mapping_file, {}).get(scene_name, "")
        key, ok = QInputDialog.getText(
            self, "Hotkey setzen",
            "Drücke die gewünschte Tastenkombination:",
            text=current
        )
        if ok and key:
            self.hotkey_manager.set_hotkey(mapping_file, scene_name, key)

    def remove_hotkey(self, mapping_file, scene_name):
        """Entfernt einen Hotkey"""
        self.hotkey_manager.remove_hotkey(mapping_file, scene_name)

    def load_all_scenes(self):
        # GridLayout leeren
        for i in reversed(range(self.scenes_layout.count())):
            item = self.scenes_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            self.scenes_layout.removeItem(item)

        mappings = list_all_track_mappings()
        row = 0
        col = 0
        max_cols = 2  # Anzahl der Spalten
        for file in mappings:
            data = load_mapping(file)
            track = data.get("track")
            scenes = data.get("scenes", {})
            for name, scene in scenes.items():
                duration = scene.get("duration", 0)
                icon_name = scene.get("icon")

                # Hotkey-Info zum Button-Text hinzufügen
                hotkey = self.hotkey_manager.hotkeys.get(file, {}).get(name, "")
                btn_text = f"{name}\n({duration}s)"
                if hotkey:
                    btn_text += f"\n[{hotkey}]"

                btn = QPushButton(btn_text)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                if icon_name:
                    icon_path = os.path.join(ICON_DIR, icon_name)
                    if os.path.exists(icon_path):
                        btn.setIcon(QIcon(QPixmap(icon_path)))
                        btn.resizeEvent = lambda event, b=btn: b.setIconSize(
                            QSize(int(b.width() * 0.6), int(b.height() * 0.6))
                        )

                is_active = (self.current_scene_name == name and self.current_playing)
                btn.setStyleSheet(get_scene_button_style(is_active))
                make_context_menu(btn, file, name, self)

                btn.clicked.connect(lambda _, s=scene, t=track, n=name: self.play_scene(t, s, n))
                self.scenes_layout.addWidget(btn, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def play_scene(self, track, scene, name):
        # Wenn die gleiche Szene bereits läuft, nur Pause/Weiter
        if self.current_scene_name == name and self.current_playing:
            self.pause_playback()
            return

        # Neue Szene starten
        self.current_track = track
        self.current_scene_name = name
        self.current_start = scene['start']
        self.current_duration = scene['duration']
        self.elapsed = 0
        self.is_paused = False
        self.current_playing = True
        self.timer.start()
        self.update_time()
        path = os.path.join(ASSET_DIR, track)
        play_loop_segment(path, self.current_start, self.current_duration)
        self.load_all_scenes()

    def pause_playback(self):
        from pygame import mixer
        if self.current_playing:
            if not self.is_paused:
                mixer.music.pause()
                self.is_paused = True
            else:
                mixer.music.unpause()
                self.is_paused = False
            self.load_all_scenes()  # Aktualisiere UI nach Pause/Weiter

    def stop_playback(self):
        stop_playback()
        self.current_playing = False
        self.is_paused = False
        self.timer.stop()
        self.update_time()
        self.statusBar().clearMessage()  # Anzeige leeren
        self.load_all_scenes()

    def update_time(self):
        if self.current_playing and not self.is_paused:
            self.elapsed += 1
            total = int(self.current_duration)
            text = f'Szene: "{self.current_scene_name}" — Laufzeit: {self.elapsed}s / {total}s'
            self.statusBar().showMessage(text)

    def create_scene_button(self, scene_id, name, icon_path=None):
        """Erstellt einen Button für eine Szene"""
        btn = QPushButton(name)
        btn.setProperty("scene_id", scene_id)
        
        if icon_path:
            btn.setIcon(QIcon(icon_path))
            
        # Kontextmenü für StreamDeck-Mapping
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(
            lambda pos, b=btn: self.show_scene_context_menu(pos, b)
        )
        
        return btn
        
    def show_scene_context_menu(self, pos, button):
        """Zeigt das Kontextmenü für eine Szene"""
        menu = QMenu()
        
        # StreamDeck-Mapping
        if self.streamdeck.device:
            map_action = QAction("Auf StreamDeck mappen...", self)
            map_action.triggered.connect(lambda: self.map_to_streamdeck(button))
            menu.addAction(map_action)
            
            # Wenn bereits gemappt, Option zum Entfernen anzeigen
            for key, mapping in self.streamdeck.button_mappings.items():
                if mapping.get('scene_id') == button.property("scene_id"):
                    unmap_action = QAction(f"StreamDeck-Mapping entfernen (Button {key})", self)
                    unmap_action.triggered.connect(lambda k=key: self.unmap_from_streamdeck(k))
                    menu.addAction(unmap_action)
                    break
                    
        menu.exec_(button.mapToGlobal(pos))
        
    def map_to_streamdeck(self, button):
        """Mapped eine Szene auf einen StreamDeck-Button"""
        if not self.streamdeck.device:
            QMessageBox.warning(self, "StreamDeck", "Kein StreamDeck verbunden")
            return
            
        # Button auswählen
        key, ok = QInputDialog.getInt(
            self,
            "StreamDeck Button",
            "Button-Nummer (0-14):",
            0, 0, 14
        )
        
        if ok:
            scene_id = button.property("scene_id")
            name = button.text()
            icon = button.icon().pixmap(72, 72).toImage()
            
            # Icon speichern
            icon_path = f"scene_{scene_id}.png"
            icon.save(os.path.join(ICON_DIR, icon_path))
            
            # Mapping erstellen
            self.streamdeck.map_button(key, scene_id, name, icon_path)
            
    def unmap_from_streamdeck(self, key):
        """Entfernt ein StreamDeck-Mapping"""
        self.streamdeck.unmap_button(key)
        
    def trigger_scene_by_id(self, scene_id):
        """Löst eine Szene per ID aus"""
        for i in range(self.scenes_layout.count()):
            btn = self.scenes_layout.itemAt(i).widget()
            if btn.property("scene_id") == scene_id:
                btn.click()
                break
                
    def closeEvent(self, event):
        """Wird beim Schließen der App aufgerufen"""
        self.streamdeck.disconnect_device()
        event.accept()

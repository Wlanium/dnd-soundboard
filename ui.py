import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QMenu, QPushButton, QLabel, QHBoxLayout, QGridLayout, QSizePolicy
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QTimer, QSize
from audio import play_loop_segment, stop_playback
from mapper import load_mapping, list_all_track_mappings
from menu import MenuBar
from config import ASSET_DIR, APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, ICON_DIR

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

class SoundboardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.menu_bar = MenuBar(self)
        self.layout.setMenuBar(self.menu_bar)

        self.scene_grid = QGridLayout()
        self.layout.addLayout(self.scene_grid)

        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.time_label)

        control_layout = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_playback)
        self.stop_btn = QPushButton("Stopp")
        self.stop_btn.clicked.connect(self.stop_playback)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        self.layout.addLayout(control_layout)

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

        self.load_all_scenes()

    def load_all_scenes(self):
        for i in reversed(range(self.scene_grid.count())):
            widget = self.scene_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        mappings = list_all_track_mappings()
        row = 0
        col = 0
        for file in mappings:
            data = load_mapping(file)
            track = data.get("track")
            scenes = data.get("scenes", {})
            for name, scene in scenes.items():
                duration = scene.get("duration", 0)
                icon_name = scene.get("icon")

                btn = QPushButton(f"{name}\n({duration}s)")
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
                self.scene_grid.addWidget(btn, row, col)
                col += 1
                if col >= 3:
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
        self.pause_btn.setText("Pause")
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
                self.pause_btn.setText("Weiter")
            else:
                mixer.music.unpause()
                self.is_paused = False
                self.pause_btn.setText("Pause")
            self.load_all_scenes()  # Aktualisiere UI nach Pause/Weiter

    def stop_playback(self):
        stop_playback()
        self.current_playing = False
        self.is_paused = False
        self.pause_btn.setText("Pause")
        self.timer.stop()
        self.time_label.setText("")
        self.load_all_scenes()

    def update_time(self):
        if self.current_playing and not self.is_paused:
            self.elapsed += 1
            total = int(self.current_duration)
            text = f'Szene: "{self.current_scene_name}" — Laufzeit: {self.elapsed}s / {total}s'
            self.time_label.setText(text)

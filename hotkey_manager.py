from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeySequence, QShortcut
import json
import os
from config import MAPPING_DIR

class HotkeyManager(QObject):
    scene_triggered = Signal(str, str)  # mapping_file, scene_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.hotkeys = {}  # mapping_file -> {scene_name -> key}
        self.shortcuts = {}  # mapping_file -> {scene_name -> QShortcut}
        self.load_hotkeys()
        
    def load_hotkeys(self):
        """Lädt Hotkeys aus der JSON-Datei"""
        hotkey_file = os.path.join(MAPPING_DIR, "hotkeys.json")
        if os.path.exists(hotkey_file):
            try:
                with open(hotkey_file, 'r', encoding='utf-8') as f:
                    self.hotkeys = json.load(f)
            except Exception:
                self.hotkeys = {}
        self.update_shortcuts()
        
    def save_hotkeys(self):
        """Speichert Hotkeys in der JSON-Datei"""
        hotkey_file = os.path.join(MAPPING_DIR, "hotkeys.json")
        with open(hotkey_file, 'w', encoding='utf-8') as f:
            json.dump(self.hotkeys, f, indent=4)
            
    def update_shortcuts(self):
        """Aktualisiert alle Shortcuts basierend auf den gespeicherten Hotkeys"""
        # Alte Shortcuts entfernen
        for shortcuts in self.shortcuts.values():
            for shortcut in shortcuts.values():
                shortcut.deleteLater()
        self.shortcuts.clear()
        
        # Neue Shortcuts erstellen
        for mapping_file, scenes in self.hotkeys.items():
            self.shortcuts[mapping_file] = {}
            for scene_name, key in scenes.items():
                if key:  # Nur wenn ein Hotkey gesetzt ist
                    shortcut = QShortcut(QKeySequence(key), self.parent)
                    shortcut.activated.connect(
                        lambda m=mapping_file, s=scene_name: self.scene_triggered.emit(m, s)
                    )
                    self.shortcuts[mapping_file][scene_name] = shortcut
                    
    def set_hotkey(self, mapping_file, scene_name, key):
        """Setzt einen neuen Hotkey für eine Szene"""
        if mapping_file not in self.hotkeys:
            self.hotkeys[mapping_file] = {}
        self.hotkeys[mapping_file][scene_name] = key
        self.save_hotkeys()
        self.update_shortcuts()
        
    def remove_hotkey(self, mapping_file, scene_name):
        """Entfernt einen Hotkey für eine Szene"""
        if mapping_file in self.hotkeys:
            if scene_name in self.hotkeys[mapping_file]:
                del self.hotkeys[mapping_file][scene_name]
                self.save_hotkeys()
                self.update_shortcuts()

# TODO: MIDI-Support
class MidiManager(QObject):
    scene_triggered = Signal(str, str)  # mapping_file, scene_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.midi_mappings = {}  # mapping_file -> {scene_name -> midi_note}
        self.load_midi_mappings()
        
    def load_midi_mappings(self):
        """Lädt MIDI-Mappings aus der JSON-Datei"""
        midi_file = os.path.join(MAPPING_DIR, "midi.json")
        if os.path.exists(midi_file):
            try:
                with open(midi_file, 'r', encoding='utf-8') as f:
                    self.midi_mappings = json.load(f)
            except Exception:
                self.midi_mappings = {}
                
    def save_midi_mappings(self):
        """Speichert MIDI-Mappings in der JSON-Datei"""
        midi_file = os.path.join(MAPPING_DIR, "midi.json")
        with open(midi_file, 'w', encoding='utf-8') as f:
            json.dump(self.midi_mappings, f, indent=4)
            
    def set_midi_mapping(self, mapping_file, scene_name, midi_note):
        """Setzt eine neue MIDI-Note für eine Szene"""
        if mapping_file not in self.midi_mappings:
            self.midi_mappings[mapping_file] = {}
        self.midi_mappings[mapping_file][scene_name] = midi_note
        self.save_midi_mappings()
        
    def remove_midi_mapping(self, mapping_file, scene_name):
        """Entfernt eine MIDI-Note für eine Szene"""
        if mapping_file in self.midi_mappings:
            if scene_name in self.midi_mappings[mapping_file]:
                del self.midi_mappings[mapping_file][scene_name]
                self.save_midi_mappings()

# TODO: StreamDeck-Support
class StreamDeckManager(QObject):
    scene_triggered = Signal(str, str)  # mapping_file, scene_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.streamdeck_mappings = {}  # mapping_file -> {scene_name -> button_id}
        self.load_streamdeck_mappings()
        
    def load_streamdeck_mappings(self):
        """Lädt StreamDeck-Mappings aus der JSON-Datei"""
        streamdeck_file = os.path.join(MAPPING_DIR, "streamdeck.json")
        if os.path.exists(streamdeck_file):
            try:
                with open(streamdeck_file, 'r', encoding='utf-8') as f:
                    self.streamdeck_mappings = json.load(f)
            except Exception:
                self.streamdeck_mappings = {}
                
    def save_streamdeck_mappings(self):
        """Speichert StreamDeck-Mappings in der JSON-Datei"""
        streamdeck_file = os.path.join(MAPPING_DIR, "streamdeck.json")
        with open(streamdeck_file, 'w', encoding='utf-8') as f:
            json.dump(self.streamdeck_mappings, f, indent=4)
            
    def set_streamdeck_mapping(self, mapping_file, scene_name, button_id):
        """Setzt eine neue StreamDeck-Taste für eine Szene"""
        if mapping_file not in self.streamdeck_mappings:
            self.streamdeck_mappings[mapping_file] = {}
        self.streamdeck_mappings[mapping_file][scene_name] = button_id
        self.save_streamdeck_mappings()
        
    def remove_streamdeck_mapping(self, mapping_file, scene_name):
        """Entfernt eine StreamDeck-Taste für eine Szene"""
        if mapping_file in self.streamdeck_mappings:
            if scene_name in self.streamdeck_mappings[mapping_file]:
                del self.streamdeck_mappings[mapping_file][scene_name]
                self.save_streamdeck_mappings() 
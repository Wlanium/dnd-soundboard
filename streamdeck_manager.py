from PySide6.QtCore import QObject, Signal
import json
import os
from PIL import Image
import io
from config import MAPPING_DIR, ICON_DIR
from StreamDeck.DeviceManager import DeviceManager

class StreamDeckManager(QObject):
    button_pressed = Signal(str)  # Signal wenn ein StreamDeck-Button gedrückt wird
    
    def __init__(self):
        super().__init__()
        self.device = None
        self.config = self.load_config()
        self.button_mappings = {}  # Speichert die Button-Mappings
        
    def load_config(self):
        """Lädt die StreamDeck-Konfiguration"""
        config_file = os.path.join(MAPPING_DIR, "streamdeck_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'auto_connect': True,
            'show_icons': True,
            'show_names': True,
            'selected_device': None
        }
        
    def connect_device(self):
        """Verbindet mit dem StreamDeck-Gerät"""
        try:
            devices = DeviceManager().enumerate()
            
            if not devices:
                return False, "Kein StreamDeck gefunden"
                
            # Wenn ein Gerät ausgewählt ist, suche es
            if self.config.get('selected_device'):
                for device in devices:
                    if f"{device.deck_type()} - {device.serial_number()}" == self.config['selected_device']:
                        self.device = device
                        break
            else:
                # Sonst nimm das erste verfügbare Gerät
                self.device = devices[0]
                
            if not self.device:
                return False, "Ausgewähltes StreamDeck nicht gefunden"
                
            # Gerät initialisieren
            self.device.open()
            self.device.reset()
            
            # Button-Callback registrieren
            self.device.set_key_callback(self._on_button_pressed)
            
            # Layout laden
            self.load_layout()
            
            return True, "StreamDeck verbunden"
            
        except Exception as e:
            return False, f"Fehler: {str(e)}"
            
    def disconnect_device(self):
        """Trennt die Verbindung zum StreamDeck"""
        if self.device:
            try:
                self.device.reset()
                self.device.close()
                self.device = None
            except Exception:
                pass
                
    def load_layout(self):
        """Lädt das Button-Layout"""
        if not self.device:
            return
            
        # Layout-Datei laden
        layout_file = os.path.join(MAPPING_DIR, "streamdeck_layout.json")
        if os.path.exists(layout_file):
            try:
                with open(layout_file, 'r', encoding='utf-8') as f:
                    self.button_mappings = json.load(f)
            except Exception:
                self.button_mappings = {}
                
        # Buttons aktualisieren
        self.update_buttons()
        
    def save_layout(self):
        """Speichert das Button-Layout"""
        layout_file = os.path.join(MAPPING_DIR, "streamdeck_layout.json")
        with open(layout_file, 'w', encoding='utf-8') as f:
            json.dump(self.button_mappings, f, indent=4)
            
    def update_buttons(self):
        """Aktualisiert alle StreamDeck-Buttons"""
        if not self.device:
            return
            
        for key, mapping in self.button_mappings.items():
            self._update_button(int(key), mapping)
            
    def _update_button(self, key, mapping):
        """Aktualisiert einen einzelnen StreamDeck-Button"""
        if not self.device:
            return
            
        try:
            # Icon laden
            icon_path = os.path.join(ICON_DIR, mapping.get('icon', 'default.png'))
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                # Fallback-Icon erstellen
                image = Image.new('RGB', (72, 72), 'black')
                
            # Icon auf StreamDeck-Größe skalieren
            image = image.resize((72, 72))
            
            # Text hinzufügen wenn aktiviert
            if self.config.get('show_names', True):
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(image)
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                except:
                    font = ImageFont.load_default()
                draw.text((5, 5), mapping.get('name', ''), 'white', font=font)
                
            # Bild auf StreamDeck setzen
            self.device.set_key_image(key, image)
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren von Button {key}: {str(e)}")
            
    def _on_button_pressed(self, deck, key, state):
        """Callback für StreamDeck-Button-Drücke"""
        if state:  # Nur bei Button-Druck, nicht bei Loslassen
            if str(key) in self.button_mappings:
                scene_id = self.button_mappings[str(key)].get('scene_id')
                if scene_id:
                    self.button_pressed.emit(scene_id)
                    
    def map_button(self, key, scene_id, name, icon):
        """Mapped einen StreamDeck-Button auf eine Szene"""
        self.button_mappings[str(key)] = {
            'scene_id': scene_id,
            'name': name,
            'icon': icon
        }
        self._update_button(key, self.button_mappings[str(key)])
        self.save_layout()
        
    def unmap_button(self, key):
        """Entfernt das Mapping eines StreamDeck-Buttons"""
        if str(key) in self.button_mappings:
            del self.button_mappings[str(key)]
            if self.device:
                self.device.set_key_image(key, None)
            self.save_layout() 
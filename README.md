# D&D Soundboard

Ein modernes Soundboard für D&D und andere Rollenspiele, mit Unterstützung für Hotkeys, MIDI-Controller und StreamDeck.

## Features

- 🎵 Einzel- und Bulk-Import von YouTube-Tracks
- 🎨 Moderne Icon-Galerie mit Upload-Funktion
- ⏱️ Flexible Zeitformate (Sekunden, mm:ss, hh:mm:ss)
- 🎹 Hotkey-Support für schnellen Zugriff
- 🎛️ MIDI-Controller-Unterstützung (optional)
- 🎮 StreamDeck-Integration (optional)
- 📦 Export/Import von kompletten Szenen-Setups
- 🎨 Modernes, anpassbares UI

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- Windows 10/11
- Für MIDI-Support: [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Für StreamDeck: [Elgato StreamDeck Software](https://www.elgato.com/de/downloads)

### Schnellstart

1. Doppelklick auf `setup.bat`
   - Das Skript prüft Python
   - Erstellt virtuelle Umgebung
   - Installiert alle Abhängigkeiten

2. Nach der Installation:
   ```powershell
   .\venv\Scripts\activate
   python main.py
   ```

### Manuelle Installation

1. Virtuelle Umgebung erstellen:
   ```powershell
   python -m venv venv
   ```

2. Umgebung aktivieren:
   ```powershell
   .\venv\Scripts\activate
   ```

3. Abhängigkeiten installieren:
   ```powershell
   pip install -r requirements.txt
   ```

## Verwendung

### Tracks importieren

- **Lokale Dateien:** Menü -> Datei -> Track hochladen
- **YouTube:** Menü -> Datei -> Track von YouTube holen
- **Bulk-Import:** Menü -> Datei -> Bulk-YouTube-Import

### Szenen verwalten

- **Erstellen:** Menü -> Konfig -> Szene erstellen
- **Bearbeiten:** Rechtsklick auf Szene -> Szene bearbeiten
- **Löschen:** Rechtsklick auf Szene -> Szene löschen

### Hotkeys

- Rechtsklick auf Szene -> Hotkey -> Neuer Hotkey
- Hotkeys werden auf den Buttons angezeigt
- Automatisch gespeichert

### MIDI/StreamDeck (optional)

1. MIDI-Support aktivieren:
   - Visual C++ Redistributable installieren
   - MIDI-Gerät anschließen
   - In den Einstellungen aktivieren

2. StreamDeck-Support:
   - StreamDeck-Software installieren
   - Gerät per USB anschließen
   - In den Einstellungen aktivieren

### Export/Import

- **Export:** Menü -> Datei -> Szenen exportieren
- **Import:** Menü -> Datei -> Szenen importieren

## Ordnerstruktur

```
soundboard/
├── assets/          # Audio-Dateien
│   ├── ffmpeg/     # FFmpeg-Binaries
│   ├── hilfe/      # Hilfedateien
│   └── icon/       # Icons für Szenen
├── mappings/       # JSON-Mappings
├── venv/          # Virtuelle Umgebung
├── main.py        # Hauptprogramm
├── requirements.txt # Abhängigkeiten
└── setup.bat      # Installationsskript
```

## Fehlerbehebung

1. **Python nicht gefunden:**
   - Python 3.8+ installieren
   - PATH-Variable prüfen

2. **MIDI funktioniert nicht:**
   - Visual C++ Redistributable installieren
   - MIDI-Gerät als Eingabegerät prüfen

3. **StreamDeck nicht erkannt:**
   - StreamDeck-Software installieren
   - USB-Verbindung prüfen
   - Als Administrator starten

## Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details. 
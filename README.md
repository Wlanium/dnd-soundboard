# D&D Soundboard

Ein Soundboard für D&D und TTRPG-Sessions mit YouTube-Import und Szenenverwaltung.

## Installation

1. Python 3.8 oder höher installieren
2. Repository klonen:
```bash
git clone https://github.com/DEIN_USERNAME/dnd-soundboard.git
cd dnd-soundboard
```

3. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

4. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

5. FFmpeg einrichten:
   - FFmpeg von https://ffmpeg.org/download.html herunterladen (Windows Build)
   - Ordner `assets/ffmpeg` erstellen
   - Alle Dateien aus dem `bin`-Ordner des FFmpeg-Downloads in `assets/ffmpeg` kopieren
   - Benötigte Dateien: `ffmpeg.exe`, `ffprobe.exe` und alle DLL-Dateien

## Verwendung

1. Programm starten:
```bash
python main.py
```

2. Tracks können über:
   - "Track hochladen" (MP3-Dateien)
   - "Track von YouTube holen" (YouTube-Links)
   hinzugefügt werden

3. Szenen können über "Konfig" -> "Szene erstellen" angelegt werden

## Build

Für eine eigenständige .exe:
```bash
pyinstaller --onefile --windowed --icon=assets/icon/app_icon.ico main.py
```

Die fertige .exe findest du dann im `dist`-Ordner. 
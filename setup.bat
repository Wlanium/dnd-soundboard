@echo off
echo D&D Soundboard Setup
echo ===================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo Python ist nicht installiert! Bitte installiere Python 3.8 oder höher.
    pause
    exit /b 1
)

REM Prüfe ob venv existiert
if not exist venv (
    echo Erstelle virtuelle Umgebung...
    python -m venv venv
    if errorlevel 1 (
        echo Fehler beim Erstellen der virtuellen Umgebung!
        pause
        exit /b 1
    )
)

REM Aktiviere venv
echo Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Fehler beim Aktivieren der virtuellen Umgebung!
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrade pip...
python -m pip install --upgrade pip

REM Installiere Requirements
echo Installiere Abhängigkeiten...
pip install -r requirements.txt
if errorlevel 1 (
    echo Fehler beim Installieren der Abhängigkeiten!
    pause
    exit /b 1
)

echo.
echo Installation abgeschlossen!
echo.
echo Um das Soundboard zu starten:
echo 1. Virtuelle Umgebung aktivieren: .\venv\Scripts\activate
echo 2. Soundboard starten: python main.py
echo.
pause 
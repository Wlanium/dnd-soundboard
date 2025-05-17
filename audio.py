# Datei: audio.py
import pygame
import threading
import os
import atexit

pygame.mixer.init()

_current_timer = None
_current_file = None

def cleanup():
    """Aufräumen beim Programmende"""
    global _current_timer
    if _current_timer:
        _current_timer.cancel()
        _current_timer = None
    pygame.mixer.music.stop()
    pygame.mixer.quit()

# Registriere cleanup für Programmende
atexit.register(cleanup)

def stop_playback():
    """Stoppt die aktuelle Wiedergabe und räumt auf"""
    global _current_timer, _current_file
    if _current_timer:
        _current_timer.cancel()
        _current_timer = None
    if _current_file:
        _current_file = None
    pygame.mixer.music.stop()
    try:
        pygame.mixer.music.unload()  # Datei entladen, damit sie freigegeben wird
    except Exception:
        pass

def play_loop_segment(file_path, start_sec, duration_sec):
    """Spielt einen Audioabschnitt in Schleife ab"""
    global _current_timer, _current_file

    # Prüfe ob Datei existiert
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audiodatei nicht gefunden: {file_path}")

    # Prüfe ob Datei lesbar ist
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Keine Leserechte für: {file_path}")

    def loop():
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(start=start_sec)
            global _current_timer
            _current_timer = threading.Timer(duration_sec, loop)
            _current_timer.daemon = True  # Timer wird beendet wenn Hauptprogramm endet
            _current_timer.start()
        except Exception as e:
            print(f"Fehler beim Abspielen: {e}")
            stop_playback()

    stop_playback()  # Stoppe vorherige Wiedergabe
    _current_file = file_path
    loop()

# Beispielnutzung:
# play_loop_segment("assets/ambient.mp3", start_sec=60, duration_sec=30)

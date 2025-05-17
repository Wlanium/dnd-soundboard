# Datei: audio.py
import pygame
import threading
import os

pygame.mixer.init()

_current_timer = None

def stop_playback():
    global _current_timer
    if _current_timer:
        _current_timer.cancel()
        _current_timer = None
    pygame.mixer.music.stop()

def play_loop_segment(file_path, start_sec, duration_sec):
    global _current_timer

    def loop():
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(start=start_sec)
        global _current_timer
        _current_timer = threading.Timer(duration_sec, loop)
        _current_timer.start()

    stop_playback()
    loop()

# Beispielnutzung:
# play_loop_segment("assets/ambient.mp3", start_sec=60, duration_sec=30)

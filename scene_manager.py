# scene_manager.py

import os
from PySide6.QtWidgets import QMessageBox, QInputDialog
from mapper import load_mapping, save_mapping
from mapping_ui import MappingDialog
from config import MAPPING_DIR

def create_scene(parent):
    dlg = MappingDialog()
    if dlg.exec():
        mapping_file, name, start, duration, icon = dlg.get_data()
        data = load_mapping(mapping_file)
        data["scenes"][name] = {
            "start": start,
            "duration": duration,
            "icon": icon
        }
        save_mapping(mapping_file, data)
        QMessageBox.information(parent, "Szene erstellt", f"Szene '{name}' wurde hinzugefügt.")
    if hasattr(parent, "load_all_scenes"):
        parent.load_all_scenes()


def edit_scene(parent):
    scene_map = {}
    for filename in os.listdir(MAPPING_DIR):
        if filename.endswith(".json"):
            data = load_mapping(filename)
            for scene_name in data.get("scenes", {}):
                key = f"{scene_name} (aus {data.get('track', filename.replace('.json',''))})"
                scene_map[key] = (filename, scene_name)

    if not scene_map:
        QMessageBox.warning(parent, "Fehler", "Keine Szenen gefunden.")
        return

    scene_label, ok = QInputDialog.getItem(parent, "Szene bearbeiten", "Wähle Szene:", list(scene_map.keys()), 0, False)
    if not ok:
        return

    mapping_file, scene_name = scene_map[scene_label]
    data = load_mapping(mapping_file)
    scene_data = data["scenes"][scene_name]

    dlg = MappingDialog(
        default_name=scene_name,
        default_start=scene_data.get("start", 0.0),
        default_duration=scene_data.get("duration", 60.0),
        default_icon=scene_data.get("icon", "")
    )
    dlg.track_combo.setCurrentText(mapping_file.replace(".json", ""))
    dlg.track_combo.setEnabled(False)

    if dlg.exec():
        _, new_name, start, duration, icon = dlg.get_data()
        if new_name != scene_name:
            del data["scenes"][scene_name]
        data["scenes"][new_name] = {
            "start": start,
            "duration": duration,
            "icon": icon or scene_data.get("icon")
        }
        save_mapping(mapping_file, data)
        QMessageBox.information(parent, "Szene bearbeitet", f"Szene '{new_name}' wurde aktualisiert.")
    main_window = parent
    while main_window.parent():
        main_window = main_window.parent()

    if hasattr(main_window, "load_all_scenes"):
        main_window.load_all_scenes()


def delete_scene(parent):
    scene_map = {}
    for filename in os.listdir(MAPPING_DIR):
        if filename.endswith(".json"):
            data = load_mapping(filename)
            for scene_name in data.get("scenes", {}):
                key = f"{scene_name} (aus {data.get('track', filename.replace('.json',''))})"
                scene_map[key] = (filename, scene_name)

    if not scene_map:
        QMessageBox.information(parent, "Keine Szenen", "Keine Szenen gefunden.")
        return

    scene_label, ok = QInputDialog.getItem(parent, "Szene löschen", "Wähle Szene:", list(scene_map.keys()), 0, False)
    if not ok:
        return

    mapping_file, scene_name = scene_map[scene_label]
    data = load_mapping(mapping_file)
    if scene_name in data.get("scenes", {}):
        del data["scenes"][scene_name]
        save_mapping(mapping_file, data)
        QMessageBox.information(parent, "Szene gelöscht", f"Szene '{scene_name}' wurde gelöscht.")
    if hasattr(parent, "load_all_scenes"):
        parent.load_all_scenes()

def edit_specific_scene(parent, mapping_file, scene_name):
    data = load_mapping(mapping_file)
    old = data["scenes"][scene_name]
    dlg = MappingDialog(
        default_name=scene_name,
        default_start=old.get("start", 0.0),
        default_duration=old.get("duration", 60.0),
        default_icon=old.get("icon", "")
    )
    dlg.track_combo.setCurrentText(mapping_file.replace(".json", ""))
    dlg.track_combo.setEnabled(False)

    if dlg.exec():
        _, new_name, start, duration, icon = dlg.get_data()
        if new_name != scene_name:
            del data["scenes"][scene_name]
        data["scenes"][new_name] = {
            "start": start,
            "duration": duration,
            "icon": icon or old.get("icon")
        }
        save_mapping(mapping_file, data)
        QMessageBox.information(parent, "Szene bearbeitet", f"Szene '{new_name}' wurde aktualisiert.")


def delete_specific_scene(parent, mapping_file, scene_name):
    data = load_mapping(mapping_file)
    if scene_name in data.get("scenes", {}):
        del data["scenes"][scene_name]
        save_mapping(mapping_file, data)
        QMessageBox.information(parent, "Szene gelöscht", f"Szene '{scene_name}' wurde gelöscht.")


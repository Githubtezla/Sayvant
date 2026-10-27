"""Unterschiede zwischen Start aus dem Quellcode und der gepackten Sayvant.exe."""
from __future__ import annotations

import sys
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))
# Ordner mit Sayvant.exe bzw. dem Projektordner beim Start aus dem Quellcode
ROOT_DIR = Path(sys.executable).parent if FROZEN else Path(__file__).resolve().parent.parent


def settings_background_command(parent_pid: int) -> list[str]:
    """Befehl, der das Einstellungsfenster als eigenen Prozess versteckt vorstartet.

    Die App blendet es per IPC ein; es endet mit dem Prozess parent_pid."""
    extra = ["--background", "--parent", str(parent_pid)]
    if FROZEN:
        return [sys.executable, "--settings", *extra]
    return [sys.executable, "-m", "sayvant.settings_app", *extra]


def autostart_target() -> tuple[str, str]:
    """(Programm, Argumente) für die Autostart-Verknüpfung."""
    if FROZEN:
        return sys.executable, ""
    return str(Path(sys.executable).with_name("pythonw.exe")), "-m sayvant"

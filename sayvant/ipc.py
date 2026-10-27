"""Lokale Verbindung zwischen der App im Infobereich und dem Einstellungsfenster.

Die App lauscht auf 127.0.0.1 (zufälliger Port) und schreibt Port und Token nach
%APPDATA%\\Sayvant\\ipc.json. Jede Anfrage ist eine JSON-Zeile mit Token.
Das vorgestartete Einstellungsfenster lauscht genauso, mit ui_ipc.json.
"""
from __future__ import annotations

import json
import logging
import os
import secrets
import socket
import threading
from pathlib import Path
from typing import Callable

from . import config

log = logging.getLogger(__name__)
IPC_FILE = config.APP_DIR / "ipc.json"
UI_IPC_FILE = config.APP_DIR / "ui_ipc.json"


def _read_line(sock: socket.socket) -> bytes:
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(65536)
        if not chunk:
            break
        data += chunk
    return data


class Server:
    def __init__(self, handler: Callable[[str, dict], dict], file: Path = IPC_FILE) -> None:
        self.handler = handler
        self.file = file
        self.token = secrets.token_hex(16)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(8)
        self.port = self.sock.getsockname()[1]
        file.write_text(json.dumps({"port": self.port, "token": self.token, "pid": os.getpid()}), encoding="utf-8")
        threading.Thread(target=self._loop, daemon=True, name="ipc").start()

    def _loop(self) -> None:
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            threading.Thread(target=self._serve, args=(conn,), daemon=True).start()

    def _serve(self, conn: socket.socket) -> None:
        with conn:
            conn.settimeout(5)
            try:
                req = json.loads(_read_line(conn) or b"{}")
            except (OSError, ValueError):
                return
            if not secrets.compare_digest(str(req.get("token", "")), self.token):
                resp = {"ok": False, "error": "Token ungültig"}
            else:
                try:
                    resp = self.handler(str(req.get("cmd", "")), req.get("args") or {})
                except Exception as e:  # noqa: BLE001
                    log.exception("IPC-Befehl %s fehlgeschlagen", req.get("cmd"))
                    resp = {"ok": False, "error": str(e)}
            try:
                conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
            except OSError:
                pass

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass
        try:
            if json.loads(self.file.read_text(encoding="utf-8")).get("token") == self.token:
                self.file.unlink()
        except (OSError, ValueError):
            pass


def call(cmd: str, timeout: float = 2.0, file: Path = IPC_FILE, **args) -> dict | None:
    """Schickt einen Befehl an die laufende App (oder mit UI_IPC_FILE an das Fenster). None, wenn sie nicht läuft."""
    try:
        info = json.loads(file.read_text(encoding="utf-8"))
        with socket.create_connection(("127.0.0.1", int(info["port"])), timeout=timeout) as s:
            s.sendall(json.dumps({"token": info["token"], "cmd": cmd, "args": args}).encode("utf-8") + b"\n")
            return json.loads(_read_line(s) or b"null")
    except (OSError, ValueError, KeyError):
        return None

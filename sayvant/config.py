"""Einstellungen von Sayvant: Standardwerte, Laden und Speichern.

Die Einstellungen liegen als JSON in %APPDATA%\\Sayvant\\settings.json.
API-Schlüssel stehen dort nie, sie liegen in der Windows-Anmeldeinformationsverwaltung
(siehe keystore.py).
"""
from __future__ import annotations

import copy
import json
import logging
import os
import uuid
from pathlib import Path

log = logging.getLogger(__name__)

APP_NAME = "Sayvant"
APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
SETTINGS_FILE = APP_DIR / "settings.json"
HISTORY_DB = APP_DIR / "history.db"
LOG_FILE = APP_DIR / "sayvant.log"
UI_LOG_FILE = APP_DIR / "ui.log"
PROMPT_FILE = APP_DIR / "cleanup_prompt.txt"
SOUND_DIR = APP_DIR / "sounds"

LANGUAGES = {
    "auto": "Automatisch",
    "de": "Deutsch",
    "en": "Englisch",
    "es": "Spanisch",
    "fr": "Französisch",
    "it": "Italienisch",
    "nl": "Niederländisch",
    "pl": "Polnisch",
    "pt": "Portugiesisch",
}


def new_id() -> str:
    return uuid.uuid4().hex[:8]


DEFAULTS: dict = {
    # Sprache der Oberfläche: auto (wie Windows) | de | en
    "ui_language": "auto",
    # Farbschema des Fensters: auto (wie Windows) | light | dark
    "appearance": "auto",
    # Design: creme | modern | graphite
    "design": "creme",
    # Sprache des Diktats
    "language": "auto",
    # local | api
    "engine": "local",
    "local": {
        "model": "nemo-parakeet-tdt-0.6b-v3",
        "quantization": "int8",
        # cpu | directml
        "provider": "cpu",
    },
    "api": {
        "profile": "openai",
        "fallback_local": True,
        "timeout": 60,
        # kind: transcriptions = POST /audio/transcriptions (Whisper-Stil)
        #       chat_audio     = POST /chat/completions mit input_audio (OpenRouter)
        "profiles": [
            {
                "id": "openai",
                "name": "OpenAI",
                "kind": "transcriptions",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o-mini-transcribe",
            },
            {
                "id": "groq",
                "name": "Groq",
                "kind": "transcriptions",
                "base_url": "https://api.groq.com/openai/v1",
                "model": "whisper-large-v3-turbo",
            },
            OPENROUTER_PROFILE := {
                "id": "openrouter",
                "name": "OpenRouter",
                "kind": "chat_audio",
                "base_url": "https://openrouter.ai/api/v1",
                "model": "google/gemini-3.5-flash-lite",
            },
            {
                "id": "eigener",
                "name": "Eigener Server",
                "kind": "transcriptions",
                "base_url": "http://localhost:8000/v1",
                "model": "Systran/faster-whisper-large-v3",
            },
        ],
    },
    "cleanup": {
        # off | claude (Anthropic) | openai | openrouter | custom (eigener Endpunkt)
        "mode": "off",
        # light | medium
        "level": "light",
        # none | formal | casual | lowercase | excited
        "style": "none",
        "claude_model": "claude-haiku-5-5",
        "openrouter_model": "anthropic/claude-haiku-5.5",
        "openai_model": "gpt-6-luna",
        "custom_base_url": "http://localhost:11434/v1",
        "custom_model": "qwen3:4b",
        "use_window_context": True,
        "timeout": 20,
    },
    "hotkeys": {
        # Halten zum Sprechen, Loslassen fügt ein
        "hold": "ctrl_r",
        # Während des Haltens zusätzlich drücken: freihändig weiter
        "handsfree_key": "space",
        # Eigener Umschalter (leer = aus), z. B. "ctrl+alt+d" oder "f9"
        "toggle": "",
        "cancel": "esc",
        # off | x1 | x2 | middle
        "mouse_button": "x2",
        # auto (halten = sprechen, klicken = freihändig) | hold | toggle
        "mouse_mode": "auto",
        "min_hold_ms": 300,
    },
    "paste": {
        # clipboard | type
        "method": "clipboard",
        # Diktat bleibt nach dem Einfügen in der Zwischenablage (zum erneuten Einfügen)
        "keep_in_clipboard": True,
        # Nur wenn keep_in_clipboard aus ist: vorherigen Inhalt zurückholen
        "restore_clipboard": True,
        "keep_out_of_history": True,
        "trailing_space": True,
    },
    "audio": {
        "device": "",
        "sounds": True,
        "max_seconds": 600,
    },
    "dictionary": {
        "terms": [],
        "replacements": {},
    },
    "snippets": {},
    "history": {
        "enabled": True,
        "keep_days": 30,
    },
    "overlay": {
        "enabled": True,
    },
    "autostart": False,
    # Bereits ausgeführte Anpassungen älterer settings.json
    "migrations": [],
}

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
# Projektseite: Quellcode, neue Versionen, Fehler melden
REPO_URL = "https://github.com/Githubtezla/Sayvant"


def key_name(profile: dict) -> str:
    """Name des Schlüssels in der Anmeldeinformationsverwaltung.

    OpenRouter teilt sich einen Schlüssel zwischen Erkennung und Nachbearbeitung.
    """
    url = profile.get("base_url", "")
    if "openrouter.ai" in url:
        return "openrouter"
    if "api.openai.com" in url:
        return "openai"
    return "api:" + profile["id"]


def _migrate(cfg: dict) -> bool:
    done = cfg.setdefault("migrations", [])
    changed = False
    for p in cfg["api"]["profiles"]:
        if "kind" not in p:
            p["kind"] = "transcriptions"
            changed = True
    if "openrouter-profil" not in done:
        if not any(p["id"] == "openrouter" for p in cfg["api"]["profiles"]):
            cfg["api"]["profiles"].insert(min(2, len(cfg["api"]["profiles"])), copy.deepcopy(OPENROUTER_PROFILE))
        done.append("openrouter-profil")
        changed = True
    if "cleanup-anbieter-v2" not in done:
        # Früher hieß der eigene Endpunkt "openai" und nutzte openai_base_url/openai_model
        c = cfg["cleanup"]
        if "openai_base_url" in c:
            c["custom_base_url"] = c.pop("openai_base_url")
            old_model = c.get("openai_model", "")
            if old_model and not old_model.startswith("gpt-"):
                c["custom_model"] = old_model
            c["openai_model"] = DEFAULTS["cleanup"]["openai_model"]
            if c.get("mode") == "openai":
                c["mode"] = "custom"
        done.append("cleanup-anbieter-v2")
        changed = True
    return changed


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict) and key not in ("replacements",):
            out[key] = _merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load() -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            cfg = _merge(DEFAULTS, data)
            if _migrate(cfg):
                save(cfg)
            return cfg
        except Exception:
            log.exception("settings.json unlesbar, nehme Standardwerte")
            backup = SETTINGS_FILE.with_suffix(".json.defekt")
            try:
                SETTINGS_FILE.replace(backup)
            except OSError:
                pass
    cfg = copy.deepcopy(DEFAULTS)
    _migrate(cfg)
    save(cfg)
    return cfg


def save(cfg: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(SETTINGS_FILE)


def api_profile(cfg: dict, profile_id: str | None = None) -> dict | None:
    pid = profile_id or cfg["api"]["profile"]
    for p in cfg["api"]["profiles"]:
        if p["id"] == pid:
            return p
    return cfg["api"]["profiles"][0] if cfg["api"]["profiles"] else None

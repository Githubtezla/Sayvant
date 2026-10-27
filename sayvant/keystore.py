"""API-Schlüssel in der Windows-Anmeldeinformationsverwaltung (über keyring).

Namen:
  api:<profil-id>  Schlüssel eines Transkriptions-Endpunkts
  claude           Anthropic-API-Schlüssel für die Nachbearbeitung
  llm              Schlüssel für einen OpenAI-kompatiblen Chat-Endpunkt
"""
from __future__ import annotations

import logging

import keyring
from keyring.errors import PasswordDeleteError

log = logging.getLogger(__name__)
SERVICE = "Sayvant"


def get_key(name: str) -> str:
    try:
        return keyring.get_password(SERVICE, name) or ""
    except Exception:
        log.exception("Schlüssel %s nicht lesbar", name)
        return ""


def set_key(name: str, value: str) -> None:
    value = (value or "").strip()
    try:
        if value:
            keyring.set_password(SERVICE, name, value)
        else:
            try:
                keyring.delete_password(SERVICE, name)
            except PasswordDeleteError:
                pass
    except Exception:
        log.exception("Schlüssel %s nicht speicherbar", name)
        raise


def has_key(name: str) -> bool:
    return bool(get_key(name))

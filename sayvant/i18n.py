"""Sprache der Oberfläche: Deutsch oder Englisch, standardmäßig nach der Windows-Sprache.

Quelltexte sind deutsch. _("Text") liefert die Übersetzung der aktiven Sprache,
Platzhalter wie {name} werden mit Schlüsselwörtern gefüllt: _("Hallo {name}", name="X").
Fehlt eine Übersetzung, bleibt der deutsche Text stehen.
"""
from __future__ import annotations

import ctypes

UI_LANGUAGES = {"auto": "Wie Windows", "de": "Deutsch", "en": "English"}
_lang = "de"


def windows_language() -> str:
    try:
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "de" if (lid & 0x3FF) == 0x07 else "en"  # LANG_GERMAN
    except Exception:
        return "en"


def resolve(setting: str) -> str:
    return setting if setting in ("de", "en") else windows_language()


def set_language(setting: str) -> str:
    global _lang
    _lang = resolve(setting)
    return _lang


def language() -> str:
    return _lang


def _(text: str, **kw) -> str:
    out = EN.get(text, text) if _lang == "en" else text
    return out.format(**kw) if kw else out


EN: dict[str, str] = {
    # Infobereich und Anzeige
    "Bereit": "Ready",
    "Lade Modell …": "Loading model …",
    "Modell fehlt": "Model missing",
    "Aufnahme läuft": "Recording",
    "Verarbeite …": "Processing …",
    "Bereit · {engine}": "Ready · {engine}",
    "Nichts gehört": "Nothing heard",
    "Nichts erkannt": "Nothing recognized",
    "Abgebrochen": "Cancelled",
    "Mikrofon: {error}": "Microphone: {error}",
    "Fehler: {error}": "Error: {error}",
    "Sayvant: {status}\n{engine}\nHalten: {hotkey}": "Sayvant: {status}\n{engine}\nHold: {hotkey}",
    "Erkennung": "Recognition",
    "Lokal: {name}": "Local: {name}",
    "API: {name}": "API: {name}",
    "Nachbearbeitung": "Cleanup",
    "Letztes Diktat erneut einfügen": "Paste last dictation again",
    "Verlauf …": "History …",
    "Einstellungen …": "Settings …",
    "Protokoll öffnen": "Open log",
    "Sayvant auf GitHub": "Sayvant on GitHub",
    "Beenden": "Quit",
    "Autostart ließ sich nicht ändern, siehe Protokoll.": "Could not change autostart, see log.",
    "Lade das Erkennungsmodell, beim ersten Mal einige hundert MB. Das kann einige Minuten dauern.":
        "Downloading the speech model, a few hundred MB the first time. This can take a few minutes.",
    "Modell geladen. Sayvant ist bereit.": "Model loaded. Sayvant is ready.",
    "Modell nicht ladbar: {error}": "Could not load model: {error}",
    "Einstellungsfenster ließ sich nicht öffnen, siehe Protokoll.": "Could not open settings, see log.",
    "Sayvant läuft bereits (Symbol im Infobereich).": "Sayvant is already running (icon in the notification area).",
    "Willkommen bei Sayvant. Halte {hotkey} gedrückt und sprich.": "Welcome to Sayvant. Hold {hotkey} and speak.",
    # Erkennung
    "Parakeet v3 (schnell, 25 Sprachen)": "Parakeet v3 (fast, 25 languages)",
    "Canary 1B v2 (genauer, feste Sprache)": "Canary 1B v2 (more accurate, fixed language)",
    "Whisper large-v3-turbo (99 Sprachen, langsamer)": "Whisper large-v3-turbo (99 languages, slower)",
    "Kein API-Profil eingerichtet": "No API profile configured",
    "{name} nicht erreichbar: {error}": "{name} not reachable: {error}",
    "{name}: Schlüssel ungültig oder fehlt ({code})": "{name}: key invalid or missing ({code})",
    "{name}: Guthaben aufgebraucht ({code})": "{name}: out of credits ({code})",
    "{name} antwortet {code}: {text}": "{name} returned {code}: {text}",
    "{name}: unerwartete Antwort": "{name}: unexpected response",
    "Verbindung in Ordnung ({count} Modelle).": "Connection OK ({count} models).",
    "Modell {model} nicht in der Liste.": "Model {model} is not in the list.",
    "Erreichbar, aber Schlüssel ungültig oder fehlt ({code}).": "Reachable, but key invalid or missing ({code}).",
    "Antwort {code}: {text}": "Response {code}: {text}",
    "Nicht erreichbar: {error}": "Not reachable: {error}",
    "Kein Schlüssel eingetragen.": "No key entered.",
    "Schlüssel gültig": "Key valid",
    ", Restguthaben {amount} USD": ", remaining credit {amount} USD",
    ", aber Modell {model} gibt es nicht.": ", but model {model} does not exist.",
    ", aber {model} nimmt kein Audio an.": ", but {model} does not accept audio.",
    ", Modell {model} verfügbar.": ", model {model} available.",
    "Schlüssel ungültig.": "Key invalid.",
    "{name} nicht erreichbar.": "{name} not reachable.",
    "Schlüssel gültig, Modell {model} verfügbar.": "Key valid, model {model} available.",
    "Schlüssel gültig, aber Modell nicht gefunden.": "Key valid, but model not found.",
    "Fehler {code}.": "Error {code}.",
    # Nachbearbeitung
    "Aus": "Off",
    "Eigener Endpunkt": "Custom endpoint",
    "Leicht": "Light",
    "Mittel": "Medium",
    "Kein": "None",
    "Förmlich": "Formal",
    "Locker": "Casual",
    "Kleinschreibung": "Lowercase",
    "Begeistert": "Excited",
    "Kein API-Schlüssel für {name} hinterlegt": "No API key stored for {name}",
    "{name}: Schlüssel ungültig": "{name}: key invalid",
    "{name}: Ratenlimit erreicht": "{name}: rate limit reached",
    "{name}: Fehler {code}": "{name}: error {code}",
    "Claude hat die Nachbearbeitung abgelehnt": "Claude declined the cleanup",
    "Nachbearbeitung verworfen": "Cleanup discarded",
    # Einstellungsfenster (Python-Seite)
    "Kurzbefehl: {error}": "Shortcut: {error}",
    "Unbekannte Taste: {key}": "Unknown key: {key}",
    "Mindestens ein Kurzbefehl oder eine Maustaste muss belegt sein.": "At least one shortcut or mouse button must be assigned.",
    "Mindestens ein API-Profil wird gebraucht.": "At least one API profile is required.",
    "Schlüssel nicht speicherbar: {error}": "Could not store key: {error}",
    "Sayvant läuft nicht.": "Sayvant is not running.",
    "Transkription (/audio/transcriptions)": "Transcription (/audio/transcriptions)",
    "Chat mit Audio (z. B. OpenRouter)": "Chat with audio (e.g. OpenRouter)",
    "Aus (Maus)": "Off",
    "Maustaste 4 (Zurück)": "Mouse button 4 (Back)",
    "Maustaste 5 (Vorwärts)": "Mouse button 5 (Forward)",
    "Mittlere Maustaste": "Middle mouse button",
    "Automatisch": "Automatic",
    "Deutsch": "German",
    "Englisch": "English",
    "Spanisch": "Spanish",
    "Französisch": "French",
    "Italienisch": "Italian",
    "Niederländisch": "Dutch",
    "Polnisch": "Polish",
    "Portugiesisch": "Portuguese",
    "Wie Windows": "Same as Windows",
}

"""Wörterbuch-Ersetzungen, Textbausteine und Hilfen zum Parsen der Listen."""
from __future__ import annotations

import re

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    return _SPACES.sub(" ", _PUNCT.sub(" ", text.lower())).strip()


def apply_replacements(text: str, replacements: dict[str, str]) -> str:
    """Ersetzt ganze Wörter oder Wortfolgen, ohne Rücksicht auf Groß- und Kleinschreibung."""
    for wrong, right in sorted(replacements.items(), key=lambda kv: -len(kv[0])):
        wrong = wrong.strip()
        if not wrong:
            continue
        pattern = r"(?<!\w)" + re.escape(wrong) + r"(?!\w)"
        text = re.sub(pattern, lambda _m, r=right: r, text, flags=re.IGNORECASE)
    return text


def match_snippet(text: str, snippets: dict[str, str]) -> str | None:
    """Liefert den Baustein, wenn die ganze Aufnahme genau einem Auslöser entspricht."""
    norm = normalize(text)
    if not norm:
        return None
    for trigger, value in snippets.items():
        if normalize(trigger) == norm:
            return value
    return None


def finalize(text: str, trailing_space: bool) -> str:
    text = text.strip()
    if text and trailing_space and not text.endswith("\n"):
        text += " "
    return text


# Listen für die Einstellungsoberfläche: eine Zeile pro Eintrag, "links => rechts"

def parse_pairs(raw: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in raw.splitlines():
        if "=>" not in line:
            continue
        left, right = line.split("=>", 1)
        left = left.strip()
        if left:
            out[left] = right.strip().replace("\\n", "\n")
    return out


def format_pairs(pairs: dict[str, str]) -> str:
    return "\n".join(f"{k} => {v.replace(chr(10), chr(92) + 'n')}" for k, v in pairs.items())


def parse_terms(raw: str) -> list[str]:
    seen: list[str] = []
    for line in raw.replace(",", "\n").splitlines():
        t = line.strip()
        if t and t not in seen:
            seen.append(t)
    return seen

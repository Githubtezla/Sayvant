"""Globale Tastatur- und Maus-Shortcuts über Low-Level-Hooks (pynput).

Schreibweise der Tastenkombinationen: Tokens mit "+" verbunden, z. B. "ctrl_r",
"ctrl+alt+d", "f9", "win+shift+space". "ctrl", "shift", "alt", "win" ohne Seite
stehen für links oder rechts.

Die Logik läuft im Hook-Thread und muss schnell bleiben. Sie meldet nur Ereignisse
an den Controller (siehe app.py), der die eigentliche Arbeit in anderen Threads macht.
"""
from __future__ import annotations

import ctypes
import logging
import threading
from typing import Callable

from pynput import keyboard, mouse

from . import i18n
from .i18n import _

log = logging.getLogger(__name__)

WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP = 0x100, 0x101, 0x104, 0x105
WM_MBUTTONDOWN, WM_MBUTTONUP = 0x207, 0x208
WM_XBUTTONDOWN, WM_XBUTTONUP = 0x20B, 0x20C
LLKHF_INJECTED = 0x10
LLMHF_INJECTED = 0x01

MODIFIERS = {
    "ctrl_l": 0xA2, "ctrl_r": 0xA3, "shift_l": 0xA0, "shift_r": 0xA1,
    "alt_l": 0xA4, "alt_r": 0xA5, "win_l": 0x5B, "win_r": 0x5C,
}
GENERIC = {
    "ctrl": (0xA2, 0xA3, 0x11),
    "shift": (0xA0, 0xA1, 0x10),
    "alt": (0xA4, 0xA5, 0x12),
    "win": (0x5B, 0x5C),
}
KEYS = {
    "space": 0x20, "esc": 0x1B, "tab": 0x09, "enter": 0x0D, "backspace": 0x08,
    "capslock": 0x14, "scrolllock": 0x91, "pause": 0x13, "insert": 0x2D, "delete": 0x2E,
    "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
    "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "printscreen": 0x2C, "menu": 0x5D, "numlock": 0x90,
}
for _i in range(1, 25):
    KEYS[f"f{_i}"] = 0x6F + _i
for _c in "abcdefghijklmnopqrstuvwxyz0123456789":
    KEYS[_c] = ord(_c.upper())
for _i in range(10):
    KEYS[f"num{_i}"] = 0x60 + _i

VK_TO_NAME = {v: k for k, v in {**KEYS, **MODIFIERS}.items()}
VK_TO_NAME.update({0x11: "ctrl", 0x10: "shift", 0x12: "alt"})
MODIFIER_VKS = set(MODIFIERS.values()) | {0x10, 0x11, 0x12}
_ORDER = ["ctrl", "ctrl_l", "ctrl_r", "alt", "alt_l", "alt_r", "shift", "shift_l", "shift_r", "win", "win_l", "win_r"]

MOUSE_BUTTONS = {"off": "Aus (Maus)", "x1": "Maustaste 4 (Zurück)", "x2": "Maustaste 5 (Vorwärts)", "middle": "Mittlere Maustaste"}

_user32 = ctypes.windll.user32


def token_vks(token: str) -> tuple[int, ...]:
    token = token.strip().lower()
    if token in GENERIC:
        return GENERIC[token]
    if token in MODIFIERS:
        return (MODIFIERS[token],)
    if token in KEYS:
        return (KEYS[token],)
    raise ValueError(_("Unbekannte Taste: {key}", key=token))


def parse_combo(text: str) -> list[tuple[int, ...]]:
    """'ctrl+alt+d' -> [(ctrl-vks), (alt-vks), (D)]. Leer -> []."""
    text = (text or "").strip()
    if not text:
        return []
    return [token_vks(t) for t in text.split("+") if t.strip()]


def validate_combo(text: str) -> str | None:
    try:
        parse_combo(text)
        return None
    except ValueError as e:
        return str(e)


def combo_name(vks: set[int]) -> str:
    names = sorted({VK_TO_NAME.get(v, f"vk{v}") for v in vks}, key=lambda n: (_ORDER.index(n) if n in _ORDER else 99, n))
    return "+".join(n for n in names if not n.startswith("vk"))


KEY_LABELS = {
    "de": {
        "ctrl": "Strg", "ctrl_l": "Strg links", "ctrl_r": "Strg rechts", "shift": "Umschalt",
        "shift_l": "Umschalt links", "shift_r": "Umschalt rechts", "alt": "Alt", "alt_l": "Alt",
        "alt_r": "AltGr", "win": "Win", "win_l": "Win", "win_r": "Win rechts", "space": "Leertaste",
        "esc": "Esc", "capslock": "Feststelltaste", "enter": "Eingabe", "menu": "Menütaste",
    },
    "en": {
        "ctrl": "Ctrl", "ctrl_l": "Left Ctrl", "ctrl_r": "Right Ctrl", "shift": "Shift",
        "shift_l": "Left Shift", "shift_r": "Right Shift", "alt": "Alt", "alt_l": "Alt",
        "alt_r": "AltGr", "win": "Win", "win_l": "Win", "win_r": "Right Win", "space": "Space",
        "esc": "Esc", "capslock": "Caps Lock", "enter": "Enter", "menu": "Menu",
    },
}


def pretty(text: str) -> str:
    label = KEY_LABELS[i18n.language()]
    if not text:
        return "-"
    return " + ".join(label.get(t, t.upper()) for t in text.split("+"))


def physically_down(combo: list[tuple[int, ...]]) -> bool:
    return all(any(_user32.GetAsyncKeyState(v) & 0x8000 for v in alts) for alts in combo)


class HotkeyManager:
    """Erkennt Shortcuts und ruft emit(ereignis, quelle) auf.

    Ereignisse: hold_start, hold_end, promote, toggle, stop, cancel, abort
    get_state() liefert den Zustand des Controllers: idle | hold | handsfree
    """

    def __init__(self, emit: Callable[[str, str], None], get_state: Callable[[], str]) -> None:
        self.emit = emit
        self.get_state = get_state
        self.pressed: set[int] = set()
        self._suppressed: set[int] = set()
        self._kb: keyboard.Listener | None = None
        self._ms: mouse.Listener | None = None
        self._capture: Callable[[str], None] | None = None
        self._capture_keys: set[int] = set()
        self._capture_down: set[int] = set()
        self.hold: list[tuple[int, ...]] = []
        self.toggle: list[tuple[int, ...]] = []
        self.handsfree_vk: int | None = None
        self.cancel_vk: int | None = None
        self.mouse_button = "off"
        self.mouse_mode = "auto"
        self.hold_source = ""
        self._lock = threading.Lock()

    # Konfiguration

    def configure(self, hk: dict) -> list[str]:
        errors = []

        def combo(key: str) -> list[tuple[int, ...]]:
            try:
                return parse_combo(hk.get(key, ""))
            except ValueError as e:
                errors.append(f"{key}: {e}")
                return []

        def single(key: str) -> int | None:
            c = combo(key)
            return c[0][0] if c else None

        self.hold = combo("hold")
        self.toggle = combo("toggle")
        self.handsfree_vk = single("handsfree_key")
        self.cancel_vk = single("cancel")
        self.mouse_button = hk.get("mouse_button", "off")
        self.mouse_mode = hk.get("mouse_mode", "auto")
        self._hold_vks = {v for alts in self.hold for v in alts}
        self._toggle_vks = {v for alts in self.toggle for v in alts}
        # Bei reinen Modifikator-Kombinationen kann der Controller den echten Tastenzustand prüfen
        self.hold_watchable = bool(self.hold) and self._hold_vks <= MODIFIER_VKS
        return errors

    # Start und Stopp

    def start(self) -> None:
        self._kb = keyboard.Listener(win32_event_filter=self._kb_filter)
        self._ms = mouse.Listener(win32_event_filter=self._ms_filter)
        self._kb.start()
        self._ms.start()

    def stop(self) -> None:
        for listener in (self._kb, self._ms):
            if listener is not None:
                listener.stop()

    def capture(self, callback: Callable[[str], None]) -> None:
        """Nimmt die nächste Tastenkombination auf (für die Einstellungen)."""
        with self._lock:
            self._capture_keys = set()
            self._capture_down = set()
            self._capture = callback

    def cancel_capture(self) -> None:
        with self._lock:
            self._capture = None

    # Hilfen

    def _satisfied(self, combo: list[tuple[int, ...]]) -> bool:
        return bool(combo) and all(any(v in self.pressed for v in alts) for alts in combo)

    # Tastatur

    def _kb_filter(self, msg, data):
        suppress = False
        try:
            suppress = self._kb_logic(msg, data)
        except Exception:
            log.exception("Fehler im Tastatur-Hook")
        if suppress:
            self._kb.suppress_event()
        return False

    def _kb_logic(self, msg, data) -> bool:
        if data.flags & LLKHF_INJECTED:
            return False
        vk = data.vkCode
        down = msg in (WM_KEYDOWN, WM_SYSKEYDOWN)
        repeat = down and vk in self.pressed
        if down:
            self.pressed.add(vk)
        else:
            self.pressed.discard(vk)

        if self._capture is not None:
            return self._capture_logic(vk, down)

        # Unterdrückte Tasten auch beim Wiederholen und Loslassen unterdrücken
        if vk in self._suppressed:
            if not down:
                self._suppressed.discard(vk)
            return True
        if repeat:
            return False

        state = self.get_state()
        if down:
            if state in ("hold", "handsfree") and vk == self.cancel_vk:
                self.emit("cancel", "kb")
                return self._sup(vk)
            if self.toggle and vk in self._toggle_vks and self._satisfied(self.toggle):
                self.emit("toggle", "kb")
                return self._sup(vk) if vk not in MODIFIER_VKS else False
            if self.hold and vk in self._hold_vks and self._satisfied(self.hold):
                if state == "idle":
                    self.hold_source = "kb"
                    self.emit("hold_start", "kb")
                elif state == "handsfree":
                    self.emit("stop", "kb")
                return self._sup(vk) if vk not in MODIFIER_VKS else False
            if state == "hold" and self.hold_source == "kb":
                if vk == self.handsfree_vk:
                    self.emit("promote", "kb")
                    return self._sup(vk)
                if vk not in MODIFIER_VKS:
                    # Normale Tastenkombination wie Strg+C: Aufnahme verwerfen
                    self.emit("abort", "kb")
        else:
            if state == "hold" and self.hold_source == "kb" and vk in self._hold_vks:
                self.emit("hold_end", "kb")
        return False

    def _sup(self, vk: int) -> bool:
        self._suppressed.add(vk)
        return True

    def _capture_logic(self, vk: int, down: bool) -> bool:
        if down:
            self._capture_keys.add(vk)
            self._capture_down.add(vk)
        else:
            self._capture_down.discard(vk)
            if not self._capture_down and self._capture_keys:
                keys = self._capture_keys
                cb, self._capture = self._capture, None
                name = "" if keys == {0x1B} else combo_name(keys)
                cb(name)
        return True

    # Maus

    def _ms_filter(self, msg, data):
        suppress = False
        try:
            suppress = self._ms_logic(msg, data)
        except Exception:
            log.exception("Fehler im Maus-Hook")
        if suppress:
            self._ms.suppress_event()
        return False

    def _ms_logic(self, msg, data) -> bool:
        if self.mouse_button == "off" or data.flags & LLMHF_INJECTED:
            return False
        if msg in (WM_XBUTTONDOWN, WM_XBUTTONUP):
            button = "x1" if (data.mouseData >> 16) & 0xFFFF == 1 else "x2"
            down = msg == WM_XBUTTONDOWN
        elif msg in (WM_MBUTTONDOWN, WM_MBUTTONUP):
            button = "middle"
            down = msg == WM_MBUTTONDOWN
        else:
            return False
        if button != self.mouse_button:
            return False
        state = self.get_state()
        if self.mouse_mode == "toggle":
            if down:
                self.emit("toggle", "mouse")
        else:
            if down:
                if state == "idle":
                    self.hold_source = "mouse"
                    self.emit("hold_start", "mouse")
                elif state == "handsfree":
                    self.emit("stop", "mouse")
            elif state == "hold" and self.hold_source == "mouse":
                self.emit("hold_end", "mouse")
        return True

"""Text an der Cursorposition einfügen: über die Zwischenablage (Strg+V) oder als Tastatureingabe.

Die Zwischenablage wird vorher gesichert und danach wiederhergestellt. Der eingefügte
Text wird so markiert, dass er nicht im Windows-Zwischenablageverlauf (Win+V) landet.
"""
from __future__ import annotations

import ctypes
import logging
import threading
import time
from ctypes import wintypes

from pynput.keyboard import Controller, Key

log = logging.getLogger(__name__)

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL
user32.GetClipboardData.argtypes = [wintypes.UINT]
user32.GetClipboardData.restype = wintypes.HANDLE
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE
user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
user32.RegisterClipboardFormatW.restype = wintypes.UINT
user32.CountClipboardFormats.argtypes = []
user32.CountClipboardFormats.restype = ctypes.c_int
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalSize.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalSize.restype = ctypes.c_size_t
kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalFree.restype = wintypes.HGLOBAL

CF_UNICODETEXT = 13
CF_DIB = 8
CF_HDROP = 15
CF_DIBV5 = 17
GMEM_MOVEABLE = 0x0002

# Formate, die gesichert werden (Text, Bilder, Dateien, Rich Text, HTML)
_SAVE_NAMES = ("HTML Format", "Rich Text Format", "PNG", "Preferred DropEffect")

_keyboard = Controller()
_lock = threading.Lock()


def _open() -> bool:
    for _ in range(25):
        if user32.OpenClipboard(None):
            return True
        time.sleep(0.02)
    log.warning("Zwischenablage blockiert")
    return False


def _alloc(data: bytes) -> int:
    h = kernel32.GlobalAlloc(GMEM_MOVEABLE, max(len(data), 1))
    if not h:
        raise OSError("GlobalAlloc fehlgeschlagen")
    p = kernel32.GlobalLock(h)
    ctypes.memmove(p, data, len(data))
    kernel32.GlobalUnlock(h)
    return h


def _put(fmt: int, data: bytes) -> None:
    h = _alloc(data)
    if not user32.SetClipboardData(fmt, h):
        kernel32.GlobalFree(h)


def _get_bytes(fmt: int) -> bytes | None:
    h = user32.GetClipboardData(fmt)
    if not h:
        return None
    p = kernel32.GlobalLock(h)
    if not p:
        return None
    try:
        return ctypes.string_at(p, kernel32.GlobalSize(h))
    finally:
        kernel32.GlobalUnlock(h)


def _mark_private() -> None:
    """Hält den Inhalt aus Zwischenablageverlauf und Cloud-Abgleich heraus."""
    zero = (0).to_bytes(4, "little")
    _put(user32.RegisterClipboardFormatW("ExcludeClipboardContentFromMonitorProcessing"), zero)
    _put(user32.RegisterClipboardFormatW("CanIncludeInClipboardHistory"), zero)
    _put(user32.RegisterClipboardFormatW("CanUploadToCloudClipboard"), zero)


def snapshot() -> list[tuple[int, bytes]] | None:
    """Sichert die gängigen Formate. None heißt: nicht lesbar, nicht anfassen."""
    if not _open():
        return None
    try:
        saved: list[tuple[int, bytes]] = []
        formats = [CF_UNICODETEXT, CF_HDROP]
        formats.append(CF_DIBV5 if user32.IsClipboardFormatAvailable(CF_DIBV5) else CF_DIB)
        formats += [user32.RegisterClipboardFormatW(n) for n in _SAVE_NAMES]
        for fmt in formats:
            if fmt and user32.IsClipboardFormatAvailable(fmt):
                data = _get_bytes(fmt)
                if data is not None:
                    saved.append((fmt, data))
        return saved
    finally:
        user32.CloseClipboard()


def restore(saved: list[tuple[int, bytes]]) -> None:
    if not _open():
        return
    try:
        user32.EmptyClipboard()
        for fmt, data in saved:
            _put(fmt, data)
        if saved:
            _mark_private()
    finally:
        user32.CloseClipboard()


def set_text(text: str, private: bool = True) -> bool:
    if not _open():
        return False
    try:
        user32.EmptyClipboard()
        _put(CF_UNICODETEXT, (text + "\0").encode("utf-16-le"))
        if private:
            _mark_private()
        return True
    finally:
        user32.CloseClipboard()


def get_text() -> str:
    if not _open():
        return ""
    try:
        data = _get_bytes(CF_UNICODETEXT)
        if not data:
            return ""
        return data.decode("utf-16-le", errors="ignore").split("\0", 1)[0]
    finally:
        user32.CloseClipboard()


def _send_paste() -> None:
    _keyboard.press(Key.ctrl_l)
    try:
        _keyboard.press("v")
        _keyboard.release("v")
    finally:
        _keyboard.release(Key.ctrl_l)


def insert(text: str, method: str = "clipboard", restore_clipboard: bool = True, private: bool = True,
           keep_in_clipboard: bool = False) -> None:
    """Fügt text ein. keep_in_clipboard lässt das Diktat danach in der Zwischenablage."""
    if not text:
        return
    with _lock:
        if method == "type":
            _keyboard.type(text)
            if keep_in_clipboard:
                set_text(text.rstrip(" "), private)
            return
        saved = snapshot() if restore_clipboard and not keep_in_clipboard else None
        if not set_text(text, private):
            raise OSError("Zwischenablage nicht beschreibbar")
        time.sleep(0.03)
        _send_paste()
        if saved is not None:
            # Manche Programme lesen die Zwischenablage verzögert
            time.sleep(0.45)
            if get_text() == text:
                restore(saved)


def copy(text: str) -> None:
    """Normales Kopieren aus dem Verlauf (bleibt in der Zwischenablage)."""
    set_text(text, private=False)

"""Anzeige-Pille unten am Bildschirm.

Ein eigenes Layered Window mit Alpha je Pixel: weiche Kanten, Schatten, Ein- und
Ausblenden, fließende Breitenänderung zwischen den Zuständen. Gezeichnet wird mit
Pillow in dreifacher Auflösung und dann verkleinert (Kantenglättung).

Das Fenster nimmt nie den Fokus. Alle Methoden nur aus dem Tk-Hauptthread aufrufen;
Tk verteilt dort auch die Fensternachrichten (Klicks).
"""
from __future__ import annotations

import ctypes
import logging
import math
import time
from ctypes import wintypes

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

log = logging.getLogger(__name__)

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT), ("style", wintypes.UINT), ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON), ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR), ("hIconSm", wintypes.HICON),
    ]


class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [("BlendOp", ctypes.c_ubyte), ("BlendFlags", ctypes.c_ubyte),
                ("SourceConstantAlpha", ctypes.c_ubyte), ("AlphaFormat", ctypes.c_ubyte)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]


user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
user32.RegisterClassExW.restype = wintypes.ATOM
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID,
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.UpdateLayeredWindow.argtypes = [
    wintypes.HWND, wintypes.HDC, ctypes.POINTER(wintypes.POINT), ctypes.POINTER(wintypes.SIZE), wintypes.HDC,
    ctypes.POINTER(wintypes.POINT), wintypes.COLORREF, ctypes.POINTER(BLENDFUNCTION), wintypes.DWORD,
]
user32.UpdateLayeredWindow.restype = wintypes.BOOL
user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = wintypes.HDC
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, wintypes.LPVOID]
user32.LoadCursorW.restype = wintypes.HANDLE
user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
user32.MonitorFromPoint.restype = wintypes.HANDLE
user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateDIBSection.argtypes = [wintypes.HDC, ctypes.POINTER(BITMAPINFO), wintypes.UINT,
                                   ctypes.POINTER(ctypes.c_void_p), wintypes.HANDLE, wintypes.DWORD]
gdi32.CreateDIBSection.restype = wintypes.HBITMAP
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE

WS_POPUP = 0x80000000
WS_EX_LAYERED, WS_EX_TOPMOST, WS_EX_TOOLWINDOW, WS_EX_NOACTIVATE = 0x80000, 0x8, 0x80, 0x08000000
WM_MOUSEACTIVATE, WM_LBUTTONUP = 0x21, 0x202
MA_NOACTIVATE = 3
SW_HIDE, SW_SHOWNOACTIVATE = 0, 4
ULW_ALPHA = 2
IDC_HAND = 32649
HWND_TOPMOST = -1
SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = 0x1, 0x2, 0x10

SS = 3          # Überabtastung für weiche Kanten
H = 40          # Höhe der Pille (logische Pixel)
PAD = 18        # Rand für den Schatten
BARS = 15

BODY = (31, 30, 29, 242)
BODY_ERR = (52, 24, 20, 244)
EDGE = (255, 240, 225, 34)
WHITE = (250, 246, 240, 240)
RED = (235, 87, 64)
# Akzentfarben der Pille je Design
PALETTES = {
    "creme": ((217, 119, 87), (111, 176, 179)),
    "modern": ((139, 135, 255), (90, 170, 255)),
    "graphite": ((235, 235, 240), (150, 150, 160)),
}
ERR_TEXT = (255, 186, 168, 255)


def _font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("seguisb.ttf", "segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


class Overlay:
    def __init__(self, root, on_click=None) -> None:
        self.on_click = on_click
        self.scale = max(1.0, root.winfo_fpixels("1i") / 96.0)
        self.enabled = True
        self.accent, self.accent2 = PALETTES["creme"]
        self.mode = "hidden"          # hidden | record | handsfree | busy | message | error
        self._draw_mode = "hidden"
        self.text = ""
        self.hide_at = 0.0
        self.levels = [0.0] * BARS
        self.width = 0.0
        self.target_w = 0.0
        self.alpha = 0.0
        self._fading_out = False
        self._visible = False
        self._anchor = (0, 0)
        self._font = _font(round(12.5 * self.scale * SS))
        self._shadow_cache: tuple | None = None
        self._dib_size = (0, 0)
        self._bmp = None
        self._bits = ctypes.c_void_p()
        self._create_window()

    # Fenster

    def _create_window(self) -> None:
        self._proc = WNDPROC(self._wndproc)  # Referenz halten, sonst räumt Python sie weg
        hinst = kernel32.GetModuleHandleW(None)
        wc = WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wc.lpfnWndProc = self._proc
        wc.hInstance = hinst
        wc.hCursor = user32.LoadCursorW(None, ctypes.c_void_p(IDC_HAND))
        wc.lpszClassName = "SayvantPill"
        user32.RegisterClassExW(ctypes.byref(wc))
        ex = WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        self.hwnd = user32.CreateWindowExW(ex, "SayvantPill", "SayvantPill", WS_POPUP, 0, 0, 1, 1, None, None, hinst, None)
        self._screen_dc = user32.GetDC(None)
        self._mem_dc = gdi32.CreateCompatibleDC(self._screen_dc)

    def _wndproc(self, hwnd, msg, wparam, lparam):
        if msg == WM_MOUSEACTIVATE:
            return MA_NOACTIVATE
        if msg == WM_LBUTTONUP:
            try:
                if self.on_click:
                    self.on_click()
            except Exception:
                log.exception("Klick auf die Pille")
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _ensure_dib(self, w: int, h: int) -> None:
        if self._dib_size == (w, h):
            return
        if self._bmp:
            gdi32.SelectObject(self._mem_dc, self._old)
            gdi32.DeleteObject(self._bmp)
        bmi = BITMAPINFO()
        hd = bmi.bmiHeader
        hd.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        hd.biWidth, hd.biHeight = w, -h  # von oben nach unten
        hd.biPlanes, hd.biBitCount, hd.biCompression = 1, 32, 0
        self._bits = ctypes.c_void_p()
        self._bmp = gdi32.CreateDIBSection(self._mem_dc, ctypes.byref(bmi), 0, ctypes.byref(self._bits), None, 0)
        self._old = gdi32.SelectObject(self._mem_dc, self._bmp)
        self._dib_size = (w, h)

    def _push(self, img: Image.Image) -> None:
        w, h = img.size
        arr = np.asarray(img, dtype=np.uint16)
        a = arr[..., 3:4]
        rgb = arr[..., :3] * a // 255  # vormultipliziertes Alpha
        bgra = np.concatenate([rgb[..., ::-1], a], axis=2).astype(np.uint8)
        self._ensure_dib(w, h)
        ctypes.memmove(self._bits, bgra.tobytes(), w * h * 4)
        cx, bottom = self._anchor
        pos = wintypes.POINT(int(cx - w / 2), int(bottom - h))
        size = wintypes.SIZE(w, h)
        src = wintypes.POINT(0, 0)
        blend = BLENDFUNCTION(0, 0, max(0, min(255, int(255 * self.alpha))), 1)
        user32.UpdateLayeredWindow(self.hwnd, self._screen_dc, ctypes.byref(pos), ctypes.byref(size),
                                   self._mem_dc, ctypes.byref(src), 0, ctypes.byref(blend), ULW_ALPHA)

    def _place_anchor(self) -> None:
        pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW(user32.MonitorFromPoint(pt, 2), ctypes.byref(mi))
        r = mi.rcWork
        margin = round((28 - PAD) * self.scale)
        self._anchor = ((r.left + r.right) / 2, r.bottom - margin)

    # Zeichnen

    def _shadow(self, cw: int, ch: int, w: int, h: int, pad: int) -> Image.Image:
        key = (cw, ch)
        if self._shadow_cache and self._shadow_cache[0] == key:
            return self._shadow_cache[1].copy()
        s = self.scale
        mask = Image.new("L", (cw, ch), 0)
        off = round(4 * s)
        ImageDraw.Draw(mask).rounded_rectangle((pad, pad + off, pad + w, pad + h + off), radius=h // 2, fill=120)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=8 * s))
        img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        img.putalpha(mask)
        self._shadow_cache = (key, img)
        return img.copy()

    def _frame(self) -> Image.Image:
        s = self.scale
        h = round(H * s)
        w = max(h, round(self.width))
        pad = round(PAD * s)
        img = self._shadow(w + 2 * pad, h + 2 * pad, w, h, pad)
        u = s * SS
        bw, bh = w * SS, h * SS
        big = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(big)
        mode = self._draw_mode
        d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=bh // 2, fill=BODY_ERR if mode == "error" else BODY,
                            outline=EDGE, width=max(1, round(u * 0.8)))
        t = time.monotonic()
        cy = bh / 2
        if mode in ("record", "handsfree"):
            col = RED if mode == "record" else self.accent
            cx, r = 21 * u, 5 * u
            pulse = (t * 1.3) % 1.0
            gr = r + 6 * u * pulse
            d.ellipse((cx - gr, cy - gr, cx + gr, cy + gr), fill=col + (int(90 * (1 - pulse)),))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
            x0, bar, gap = 38 * u, 3 * u, 3.2 * u
            maxh = bh - 16 * u
            for i, lv in enumerate(self.levels):
                bhh = max(3.5 * u, lv * maxh)
                x = x0 + i * (bar + gap)
                d.rounded_rectangle((x, cy - bhh / 2, x + bar, cy + bhh / 2), radius=bar / 2, fill=WHITE)
            if mode == "handsfree":
                sx = bw - 21 * u
                d.ellipse((sx - 11 * u, cy - 11 * u, sx + 11 * u, cy + 11 * u), fill=(255, 255, 255, 34))
                q = 3.6 * u
                d.rounded_rectangle((sx - q, cy - q, sx + q, cy + q), radius=1.2 * u, fill=WHITE)
        elif mode == "busy":
            for i in range(3):
                phase = (math.sin(t * 5.5 - i * 0.9) + 1) / 2
                r = (3.0 + 1.8 * phase) * u
                cx = bw / 2 + (i - 1) * 15 * u
                mix = i / 2
                col = tuple(int(self.accent[k] * (1 - mix) + self.accent2[k] * mix) for k in range(3))
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (int(150 + 105 * phase),))
        elif mode in ("message", "error"):
            col = RED if mode == "error" else self.accent
            cx, r = 20 * u, 4 * u
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
            d.text((32 * u, cy), self.text, font=self._font, fill=ERR_TEXT if mode == "error" else WHITE, anchor="lm")
        small = big.resize((w, h), Image.LANCZOS)
        img.alpha_composite(small, (pad, pad))
        return img

    def set_design(self, design: str) -> None:
        self.accent, self.accent2 = PALETTES.get(design, PALETTES["creme"])

    # Zustände

    def _target(self, mode: str) -> float:
        s = self.scale
        if mode == "record":
            return 38 * s + BARS * 6.2 * s + 14 * s
        if mode == "handsfree":
            return 38 * s + BARS * 6.2 * s + 44 * s
        if mode == "busy":
            return 92 * s
        text_w = self._font.getlength(self.text) / SS
        return min(560 * s, max(120 * s, 32 * s + text_w + 20 * s))

    def _show(self, mode: str) -> None:
        self.mode = mode
        self._draw_mode = mode
        self.target_w = self._target(mode)
        self._fading_out = False
        if not self._visible:
            self._place_anchor()
            self.width = self.target_w * 0.82
            self.alpha = 0.0
            self._push(self._frame())
            user32.ShowWindow(self.hwnd, SW_SHOWNOACTIVATE)
            user32.SetWindowPos(self.hwnd, wintypes.HWND(HWND_TOPMOST), 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)
            self._visible = True

    def show_record(self, handsfree: bool = False) -> None:
        if not self.enabled:
            return
        self.hide_at = 0
        if self.mode not in ("record", "handsfree"):
            self.levels = [0.0] * BARS
        self._show("handsfree" if handsfree else "record")

    def show_busy(self) -> None:
        if not self.enabled:
            return
        self.hide_at = 0
        self._show("busy")

    def show_message(self, text: str, error: bool = False, seconds: float = 2.0) -> None:
        if not self.enabled and not error:
            return
        self.text = text
        self.hide_at = time.monotonic() + seconds
        self._show("error" if error else "message")

    def hide(self) -> None:
        if self._visible:
            self._fading_out = True
        self.mode = "hidden"

    def tick(self, level: float) -> None:
        """Alle ~30 ms aus der Hauptschleife."""
        if not self._visible:
            return
        if self.hide_at and time.monotonic() > self.hide_at:
            self.hide_at = 0
            self.hide()
        if self._fading_out:
            self.alpha -= 0.16
            if self.alpha <= 0:
                self.alpha = 0
                user32.ShowWindow(self.hwnd, SW_HIDE)
                self._visible = False
                self._fading_out = False
                self._draw_mode = "hidden"
                return
        elif self.alpha < 1:
            self.alpha = min(1.0, self.alpha + 0.2)
        if abs(self.target_w - self.width) > 0.5:
            self.width += (self.target_w - self.width) * 0.32
        else:
            self.width = self.target_w
        if self._draw_mode in ("record", "handsfree"):
            v = min(1.0, math.sqrt(max(level, 0.0)) * 3.4)
            # Neue Werte laufen von rechts ein, leicht geglättet
            self.levels = self.levels[1:] + [0.55 * v + 0.45 * self.levels[-1]]
        try:
            self._push(self._frame())
        except Exception:
            log.exception("Pille nicht zeichenbar")
            self._fading_out = True

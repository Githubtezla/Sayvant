"""Einstellungs- und Verlaufsfenster als Weboberfläche (pywebview mit WebView2).

Läuft als eigener Prozess: python -m sayvant.settings_app [--page home|general|hotkeys|engine|cleanup|dictionary|history]
(gepackt: Sayvant.exe --settings --page ...). Die laufende App im Infobereich startet
ihn mit --background versteckt vor und blendet das Fenster per IPC (ui_ipc.json) ein,
damit es sofort da ist. Schließen versteckt es dann nur. Änderungen meldet das Fenster
über ipc.py an die App.
"""
from __future__ import annotations

import os

# numpy (über audio) reserviert sonst je Prozessorkern Rechenpuffer, zusammen über 300 MB.
# Das Fenster rechnet nichts und bleibt vorgestartet im Speicher, also ein Thread.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse  # noqa: E402
import base64
import ctypes
import datetime as dt
import json
import logging
import re
import sys
import threading
import time
import winreg
from pathlib import Path

from . import __version__, audio, cleanup, config, engines, hotkeys, i18n, icons, inject, ipc, keystore
from .history import History
from .i18n import _

log = logging.getLogger("sayvant.ui")
WEBUI = Path(__file__).resolve().parent / "webui"
TITLE = "Sayvant"
PAGES = ("home", "general", "hotkeys", "engine", "cleanup", "dictionary", "history")
OR_CLEANUP_MODELS = [
    "anthropic/claude-haiku-5.5",
    "anthropic/claude-sonnet-5.5",
    "openai/gpt-6-luna",
    "google/gemini-3.5-flash-lite",
]
OPENAI_CLEANUP_MODELS = ["gpt-6-luna", "gpt-6-sol", "gpt-5.6-luna"]
CLAUDE_MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]
KIND_NAMES = {
    "transcriptions": "Transkription (/audio/transcriptions)",
    "chat_audio": "Chat mit Audio (z. B. OpenRouter)",
}
WORDS = re.compile(r"\w+", re.UNICODE)
TYPING_WPM = 40  # übliche Tippgeschwindigkeit für die Zeitersparnis


def _res(result: tuple[bool, str]) -> dict:
    ok, msg = result
    return {"cls": "ok" if ok else "bad", "text": msg}


def _tr(d: dict) -> dict:
    return {k: _(v) for k, v in d.items()}


class Api:
    """Wird im Browser als window.pywebview.api angeboten. Private Felder mit Unterstrich."""

    def __init__(self, page: str) -> None:
        self._page = page
        self._history = History(config.HISTORY_DB)
        self._rec = audio.Recorder()
        self._rec_lock = threading.Lock()

    def initial_page(self) -> str:
        return self._page

    def get_state(self) -> dict:
        cfg = config.load()
        lang = i18n.set_language(cfg.get("ui_language", "auto"))
        names = {"claude", "openai", "llm", "openrouter"} | {config.key_name(p) for p in cfg["api"]["profiles"]}
        try:
            import onnxruntime as rt
            dml = "DmlExecutionProvider" in rt.get_available_providers()
        except Exception:
            dml = False
        return {
            "cfg": cfg,
            "keys": {n: keystore.has_key(n) for n in names},
            "meta": {
                "version": __version__,
                "repo_url": config.REPO_URL,
                "lang": lang,
                "windows_lang": i18n.windows_language(),
                "ui_languages": {"auto": _("Wie Windows"), "de": "Deutsch", "en": "English"},
                "languages": _tr(config.LANGUAGES),
                "local_models": _tr(engines.LOCAL_MODELS),
                "mouse_buttons": _tr(hotkeys.MOUSE_BUTTONS),
                "levels": _tr(cleanup.LEVEL_NAMES),
                "styles": _tr(cleanup.STYLE_NAMES),
                "kinds": _tr(KIND_NAMES),
                "devices": audio.input_devices(),
                "dml": dml,
                "or_models": [],
                "or_cleanup_models": OR_CLEANUP_MODELS,
                "openai_models": OPENAI_CLEANUP_MODELS,
                "claude_models": CLAUDE_MODELS,
                "first_run": not (config.APP_DIR / ".willkommen").exists(),
            },
        }

    def dismiss_welcome(self) -> None:
        (config.APP_DIR / ".willkommen").write_text("1", encoding="utf-8")

    def save(self, cfg: dict, keys: dict) -> dict:
        i18n.set_language(cfg.get("ui_language", "auto"))
        hk = cfg.get("hotkeys", {})
        for field in ("hold", "handsfree_key", "toggle", "cancel"):
            err = hotkeys.validate_combo(hk.get(field, ""))
            if err:
                return {"ok": False, "error": _("Kurzbefehl: {error}", error=err)}
        if not hk.get("hold") and not hk.get("toggle") and hk.get("mouse_button") == "off":
            return {"ok": False, "error": _("Mindestens ein Kurzbefehl oder eine Maustaste muss belegt sein.")}
        if not cfg["api"]["profiles"]:
            return {"ok": False, "error": _("Mindestens ein API-Profil wird gebraucht.")}
        merged = config._merge(config.DEFAULTS, cfg)
        try:
            for name, value in (keys or {}).items():
                keystore.set_key(name, value or "")
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": _("Schlüssel nicht speicherbar: {error}", error=e)}
        config.save(merged)
        applied = bool((ipc.call("apply") or {}).get("ok"))
        names = {"claude", "openai", "llm", "openrouter"} | {config.key_name(p) for p in merged["api"]["profiles"]}
        return {"ok": True, "applied": applied, "keys": {n: keystore.has_key(n) for n in names}}

    # Tests

    def test_profile(self, profile: dict, key: str | None) -> dict:
        if key is None:
            key = keystore.get_key(config.key_name(profile))
        return _res(engines.test_api(profile, key or ""))

    def test_cleanup(self, provider: str, model: str, key: str | None) -> dict:
        name = {"claude": "claude", "openai": "openai", "openrouter": "openrouter"}[provider]
        if key is None:
            key = keystore.get_key(name)
        if provider == "claude":
            return _res(cleanup.test_claude(model, key or ""))
        if provider == "openai":
            return _res(cleanup.test_openai(model, key or ""))
        return _res(engines.test_openrouter(key or "", model))

    def openrouter_models(self) -> list[str]:
        return engines.openrouter_audio_models()

    # Mikrofontest

    def mic_start(self, device: str) -> dict:
        with self._rec_lock:
            try:
                self._rec.stop()
                self._rec.start(device or "")
                return {"ok": True}
            except Exception as e:  # noqa: BLE001
                return {"ok": False, "error": str(e)}

    def mic_level(self) -> float:
        return float(self._rec.level) if self._rec.active else 0.0

    def mic_stop(self, transcribe: bool) -> dict:
        with self._rec_lock:
            data = self._rec.stop()
        if not transcribe:
            return {"ok": True}
        if len(data) < audio.SAMPLE_RATE * 0.3:
            return {"ok": True, "final": "", "note": _("Nichts gehört")}
        r = ipc.call("transcribe_test", timeout=90, wav_b64=base64.b64encode(audio.to_wav(data)).decode("ascii"))
        if r is None:
            return {"ok": False, "error": _("Sayvant läuft nicht.")}
        return r

    # Kurzbefehle aufnehmen (über die laufende App)

    def capture_start(self) -> dict:
        r = ipc.call("capture_start")
        return r if r else {"ok": False, "error": _("Sayvant läuft nicht.")}

    def capture_cancel(self) -> dict:
        return ipc.call("capture_cancel") or {"ok": False}

    def poll(self) -> dict:
        r = ipc.call("poll", timeout=1.0)
        if not r:
            return {"connected": False}
        r["connected"] = True
        return r

    # Verlauf und Statistik

    def history(self, query: str = "") -> list[dict]:
        return [dict(row) for row in self._history.search(query or "")]

    def stats(self) -> dict:
        rows = self._history.search("", limit=1_000_000)
        today = dt.date.today()
        week_start = today - dt.timedelta(days=6)
        words = seconds = words_today = count_today = 0
        days = {(week_start + dt.timedelta(days=i)).isoformat(): 0 for i in range(7)}
        for r in rows:
            n = len(WORDS.findall(r["final"] or ""))
            words += n
            seconds += r["seconds"] or 0
            d = dt.date.fromtimestamp(r["ts"])
            if d == today:
                words_today += n
                count_today += 1
            if d >= week_start:
                days[d.isoformat()] += n
        typing_minutes = words / TYPING_WPM
        saved = max(0.0, typing_minutes - seconds / 60)
        return {
            "count": len(rows), "words": words, "minutes_spoken": round(seconds / 60, 1),
            "saved_minutes": round(saved), "words_today": words_today, "count_today": count_today,
            "week": [{"day": k, "words": v} for k, v in days.items()],
            "wpm": round(words / (seconds / 60)) if seconds > 30 else None,
        }

    def history_copy(self, entry_id: int, field: str) -> bool:
        row = self._history.get(entry_id)
        if row is None or field not in ("final", "raw"):
            return False
        inject.copy(row[field] or "")
        return True

    def history_delete(self, entry_id: int) -> bool:
        self._history.delete(entry_id)
        return True

    def history_clear(self) -> bool:
        self._history.clear()
        return True

    # Dateien

    def open_prompt(self) -> None:
        if not config.PROMPT_FILE.exists():
            config.PROMPT_FILE.write_text(cleanup.BASE_RULES + "\n", encoding="utf-8")
        os.startfile(config.PROMPT_FILE)  # noqa: S606

    def open_log(self) -> None:
        if config.LOG_FILE.exists():
            os.startfile(config.LOG_FILE)  # noqa: S606

    def open_folder(self) -> None:
        os.startfile(config.APP_DIR)  # noqa: S606

    def open_url(self, url: str) -> None:
        if url.startswith("https://"):
            os.startfile(url)  # noqa: S606


def _dark_mode() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            return winreg.QueryValueEx(k, "AppsUseLightTheme")[0] == 0
    except OSError:
        return False


def _find_window(pid: int | None = None, visible_only: bool = False) -> int:
    """Sucht das Sayvant-Fenster, wahlweise nur eines Prozesses oder nur sichtbare."""
    user32 = ctypes.windll.user32
    # pywebview nutzt WinForms; die Klasse beginnt mit "WindowsForms"
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(hwnd, _lp):
        h = ctypes.c_void_p(hwnd)
        if visible_only and not user32.IsWindowVisible(h):
            return True
        if pid is not None:
            owner = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(h, ctypes.byref(owner))
            if owner.value != pid:
                return True
        title = ctypes.create_unicode_buffer(64)
        cls = ctypes.create_unicode_buffer(64)
        user32.GetWindowTextW(h, title, 64)
        user32.GetClassNameW(h, cls, 64)
        if title.value == TITLE and cls.value.startswith("WindowsForms"):
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(cb, None)
    return found[0] if found else 0


def _bring_to_front(hwnd: int) -> None:
    """Holt das Fenster nach vorn. Windows erlaubt das nur dem Vordergrundprozess; deshalb hängt
    sich der Fenster-Thread kurz an die Eingabe des aktuellen Vordergrundfensters."""
    user32 = ctypes.windll.user32
    user32.GetForegroundWindow.restype = ctypes.c_void_p
    h = ctypes.c_void_p(hwnd)
    if user32.IsIconic(h):
        user32.ShowWindow(h, 9)  # SW_RESTORE
    fg = user32.GetForegroundWindow()
    if fg == hwnd:
        return
    own = ctypes.windll.kernel32.GetCurrentThreadId()
    other = user32.GetWindowThreadProcessId(ctypes.c_void_p(fg), None) if fg else 0
    attached = bool(other and other != own and user32.AttachThreadInput(own, other, True))
    try:
        user32.BringWindowToTop(h)
        ok = user32.SetForegroundWindow(h)
    finally:
        if attached:
            user32.AttachThreadInput(own, other, False)
    if not ok:
        log.info("Fenster ließ sich nicht nach vorn holen (angehängt: %s)", attached)


def focus_existing() -> bool:
    hwnd = _find_window(visible_only=True)
    if not hwnd:
        return False
    _bring_to_front(hwnd)
    return True


def _own_window(wait: float = 8.0) -> int:
    hwnd = 0
    for _i in range(int(wait * 10)):
        hwnd = _find_window(pid=os.getpid())
        if hwnd:
            break
        time.sleep(0.1)
    return hwnd


def _apply_icon() -> None:
    """Setzt das Sayvant-Symbol auf Fenster und Taskleiste (läuft nach dem Fensterstart)."""
    try:
        ico = icons.ensure_ico(config.load().get("design", "creme"))
    except Exception:
        log.exception("Symbol nicht erzeugbar")
        return
    user32 = ctypes.windll.user32
    user32.LoadImageW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    user32.LoadImageW.restype = ctypes.c_void_p
    user32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]
    hwnd = _own_window()
    if not hwnd:
        return
    for which, px in ((1, 32), (0, 16)):  # ICON_BIG, ICON_SMALL
        h = user32.LoadImageW(None, ico, 1, px, px, 0x10)  # IMAGE_ICON, LR_LOADFROMFILE
        if h:
            user32.SendMessageW(hwnd, 0x80, which, h)  # WM_SETICON


def _exit_with_parent(pid: int) -> None:
    """Beendet das vorgestartete Fenster, sobald die App im Infobereich endet (auch nach einem Absturz)."""
    kernel32 = ctypes.windll.kernel32
    kernel32.OpenProcess.restype = ctypes.c_void_p
    handle = kernel32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
    if not handle:
        os._exit(0)
    kernel32.WaitForSingleObject(ctypes.c_void_p(handle), 0xFFFFFFFF)
    os._exit(0)


class Background:
    """Versteckt vorgestartetes Fenster: die App blendet es per IPC ein, Schließen versteckt es nur."""

    def __init__(self, window) -> None:
        self.window = window
        self.server: ipc.Server | None = None

    def handle(self, cmd: str, args: dict) -> dict:
        if cmd == "show":
            self.show(str(args.get("page") or "home"))
            return {"ok": True}
        if cmd == "ping":
            return {"ok": True}
        return {"ok": False, "error": f"Unbekannter Befehl {cmd}"}

    def show(self, page: str) -> None:
        if page not in PAGES:
            page = "home"
        self.window.run_js(f"window.sayvantShow && window.sayvantShow({json.dumps(page)})")
        self.window.show()
        hwnd = _find_window(pid=os.getpid())
        if hwnd:
            _bring_to_front(hwnd)

    def on_closing(self) -> bool:
        # Beim Abmelden oder Herunterfahren wirklich schließen, sonst hält das Fenster Windows auf
        if ctypes.windll.user32.GetSystemMetrics(0x2000):  # SM_SHUTTINGDOWN
            return True
        threading.Thread(target=self.hide, daemon=True).start()
        return False

    def hide(self) -> None:
        self.window.hide()
        self.window.run_js("window.sayvantHide && window.sayvantHide()")

    def started(self) -> None:
        """Läuft nach dem Fensterstart: Symbol setzen, lauschen, der App Bescheid geben."""
        _apply_icon()
        self.window.events.loaded.wait(20)
        self.server = ipc.Server(self.handle, ipc.UI_IPC_FILE)
        log.info("Fenster vorgestartet")
        r = ipc.call("ui_ready", pid=os.getpid()) or {}
        if r.get("show"):
            self.show(str(r["show"]))


def main(argv: list[str] | None = None) -> None:
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", action="store_true")  # nur für Sayvant.exe
    parser.add_argument("--page", default="home", choices=PAGES)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--on-top", action="store_true")
    parser.add_argument("--background", action="store_true")  # versteckt vorstarten, die App blendet ein
    parser.add_argument("--parent", type=int, default=0)
    args = parser.parse_args(argv)
    config.APP_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(config.UI_LOG_FILE, encoding="utf-8")],
    )
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        # Eigene Gruppe in der Taskleiste statt "Python"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Sayvant.Einstellungen")
    except Exception:
        pass
    if not args.background:
        if focus_existing():
            return
        # Ein vorgestartetes, verstecktes Fenster einblenden statt ein zweites zu öffnen
        if (ipc.call("show", timeout=1.0, file=ipc.UI_IPC_FILE, page=args.page) or {}).get("ok"):
            return
    elif args.parent:
        threading.Thread(target=_exit_with_parent, args=(args.parent,), daemon=True, name="eltern").start()

    import webview

    try:
        cfg = config.load()
    except Exception:
        cfg = {}
    appearance = cfg.get("appearance", "auto")
    dark = appearance == "dark" or (appearance == "auto" and _dark_mode())
    backgrounds = {"creme": ("#f7f2ea", "#262624"), "modern": ("#f4f5f7", "#17171b"), "graphite": ("#fafafa", "#0e0e10")}
    light_bg, dark_bg = backgrounds.get(cfg.get("design", "creme"), backgrounds["creme"])
    window = webview.create_window(
        TITLE, url=str(WEBUI / "index.html"), js_api=Api(args.page),
        width=1100, height=760, min_size=(900, 620), on_top=args.on_top,
        background_color=dark_bg if dark else light_bg, hidden=args.background,
    )
    # WebView2 braucht nach dem Schließen sonst einige Sekunden zum Aufräumen
    window.events.closed += lambda: threading.Timer(0.3, os._exit, (0,)).start()
    start = _apply_icon
    if args.background:
        bg = Background(window)
        window.events.closing += bg.on_closing
        start = bg.started
    webview.start(start, gui="edgechromium", debug=args.debug, private_mode=True)


if __name__ == "__main__":
    main()

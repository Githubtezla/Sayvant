"""Sayvant: Diktieren per Shortcut, Text landet an der Cursorposition.

Threads:
  Tk-Hauptthread   Anzeige, Fenster, Warteschlange self.q
  Hook-Threads     Tastatur und Maus (hotkeys.py), rufen self.handle() auf
  Aktions-Thread   Mikrofon starten und stoppen, der Reihe nach
  Verarbeitung     Erkennung, Nachbearbeitung, Einfügen, der Reihe nach
"""
from __future__ import annotations

import copy
import ctypes
import logging
import logging.handlers
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
import winsound
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pystray

from . import audio, cleanup, config, engines, hotkeys, i18n, icons, inject, ipc, runtime, textproc
from .history import History
from .i18n import _
from .overlay import Overlay

log = logging.getLogger("sayvant")
_user32 = ctypes.windll.user32
ROOT_DIR = runtime.ROOT_DIR
STARTUP_LNK = Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs/Startup/Sayvant.lnk"


def _window_title() -> str:
    hwnd = _user32.GetForegroundWindow()
    n = _user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    _user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


_ICON_CACHE: dict[str, dict] = {}


def tray_icons(design: str) -> dict:
    """Symbole für den Infobereich; im Ruhezustand in der Farbe des Designs."""
    if design not in _ICON_CACHE:
        _ICON_CACHE[design] = {
            "idle": icons.icon_image(icons.DESIGN_COLORS.get(design, icons.DESIGN_COLORS["creme"])),
            "record": icons.icon_image(icons.RED),
            "busy": icons.icon_image(icons.AMBER),
            "loading": icons.icon_image(icons.GRAY),
        }
    return _ICON_CACHE[design]


class App:
    def __init__(self) -> None:
        self.cfg = config.load()
        self.q: queue.Queue = queue.Queue()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.report_callback_exception = lambda *a: log.error("Tk-Fehler", exc_info=a)
        self.overlay = Overlay(self.root, on_click=self._pill_click)
        self.recorder = audio.Recorder()
        self.engines = engines.EngineManager()
        self.history = History(config.HISTORY_DB)
        self.hotkeys = hotkeys.HotkeyManager(self.handle, lambda: self.state)
        self.actions = ThreadPoolExecutor(1, thread_name_prefix="aktion")
        self.processing = ThreadPoolExecutor(1, thread_name_prefix="verarbeitung")
        self._lock = threading.Lock()
        self.state = "idle"  # idle | hold | handsfree
        self.source = ""
        self.t_start = 0.0
        self.window_title = ""
        self.busy = 0
        self.loading = False
        self.status = "Bereit"
        self.ui_proc: subprocess.Popen | None = None
        self.ui_pending: str | None = None  # Seite, die das Fenster zeigen soll, sobald es bereit ist
        self.ui_pid = 0  # PID des Fensterprozesses, meldet er selbst mit ui_ready
        self._capture: dict | None = None
        self.history_seq = 0
        self.ipc: ipc.Server | None = None
        self._watch_misses = 0
        self.tray: pystray.Icon | None = None
        self._make_sounds()
        self._apply_runtime()

    # Hilfen für Threads

    def post(self, fn, *args) -> None:
        """Führt fn im Tk-Hauptthread aus."""
        self.q.put((fn, args))

    def _pump(self) -> None:
        try:
            while True:
                fn, args = self.q.get_nowait()
                try:
                    fn(*args)
                except Exception:
                    log.exception("Fehler in der Hauptschleife")
        except queue.Empty:
            pass
        self.overlay.tick(self.recorder.level)
        self._watchdog()
        self.root.after(30, self._pump)

    # Einstellungen

    def _apply_runtime(self) -> None:
        i18n.set_language(self.cfg.get("ui_language", "auto"))
        errors = self.hotkeys.configure(self.cfg["hotkeys"])
        for e in errors:
            log.warning("Kurzbefehl ungültig: %s", e)
        self.overlay.enabled = self.cfg["overlay"]["enabled"]
        design = self.cfg.get("design", "creme")
        self.overlay.set_design(design)
        self.icons = tray_icons(design)
        if getattr(self, "tray", None) is not None and self.state == "idle" and not self.busy and not self.loading:
            self.tray.icon = self.icons["idle"]
        if self.cfg["history"]["enabled"]:
            self.history.prune(self.cfg["history"]["keep_days"])

    def apply_settings(self, new_cfg: dict) -> None:
        old = self.cfg
        self.cfg = copy.deepcopy(new_cfg)
        config.save(self.cfg)
        self._apply_runtime()
        if old["autostart"] != self.cfg["autostart"] or self.cfg["autostart"]:
            self._set_autostart(self.cfg["autostart"])
        if old["local"] != self.cfg["local"] or old["engine"] != self.cfg["engine"]:
            self._preload()
        threading.Thread(target=cleanup.warm_up, args=(self.cfg,), daemon=True, name="vorladen").start()
        if self.tray is not None and old.get("ui_language") != self.cfg.get("ui_language"):
            self.tray.menu = self._menu()
        self._update_tray()
        log.info("Einstellungen gespeichert")

    def _set_autostart(self, on: bool) -> None:
        try:
            if on:
                target, arguments = runtime.autostart_target()
                ps = (
                    "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:LNK);"
                    "$s.TargetPath=$env:TGT;$s.Arguments=$env:ARGS;$s.WorkingDirectory=$env:WD;"
                    "$s.Description='Sayvant';$s.IconLocation=$env:ICO;$s.Save()"
                )
                env = dict(os.environ, LNK=str(STARTUP_LNK), TGT=target, ARGS=arguments, WD=str(ROOT_DIR),
                           ICO=icons.ensure_ico(self.cfg.get("design", "creme")))
                subprocess.run(["powershell", "-NoProfile", "-Command", ps], env=env, check=True,
                               creationflags=subprocess.CREATE_NO_WINDOW, timeout=20)
            elif STARTUP_LNK.exists():
                STARTUP_LNK.unlink()
        except Exception:
            log.exception("Autostart nicht änderbar")
            self.notify(_("Autostart ließ sich nicht ändern, siehe Protokoll."))

    # Töne

    def _make_sounds(self) -> None:
        config.SOUND_DIR.mkdir(parents=True, exist_ok=True)
        tones = {"start": [880, 1320], "stop": [1320, 880], "cancel": [440], "error": [330, 260]}
        self.sounds = {}
        for name, freqs in tones.items():
            path = config.SOUND_DIR / f"{name}.wav"
            if not path.exists():
                audio.make_tone(path, freqs, dur=0.06 if name != "error" else 0.12, volume=0.18)
            self.sounds[name] = str(path)

    def sound(self, name: str) -> None:
        if self.cfg["audio"]["sounds"] and name in self.sounds:
            winsound.PlaySound(self.sounds[name], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)

    # Zustandsmaschine (aus Hook-Threads und Tk-Thread)

    def handle(self, event: str, source: str) -> None:
        with self._lock:
            now = time.monotonic()
            st = self.state
            min_hold = self.cfg["hotkeys"]["min_hold_ms"] / 1000
            if event == "hold_start" and st == "idle":
                self._begin("hold", source, now)
            elif event == "hold_end" and st == "hold" and source == self.source:
                if now - self.t_start < min_hold:
                    if source == "mouse" and self.cfg["hotkeys"]["mouse_mode"] == "auto":
                        self.state = "handsfree"
                        self.post(self.overlay.show_record, True)
                    else:
                        self._cancel(silent=True)
                else:
                    self._finish()
            elif event == "promote" and st == "hold":
                self.state = "handsfree"
                self.post(self.overlay.show_record, True)
            elif event == "toggle":
                if st == "idle":
                    self._begin("handsfree", source, now)
                elif st == "hold":
                    self.state = "handsfree"
                    self.post(self.overlay.show_record, True)
                else:
                    self._finish()
            elif event == "stop" and st == "handsfree":
                self._finish()
            elif event == "cancel" and st in ("hold", "handsfree"):
                self._cancel(silent=False)
            elif event == "abort" and st == "hold" and now - self.t_start < 1.0:
                self._cancel(silent=True)

    def _begin(self, state: str, source: str, now: float) -> None:
        self.state = state
        self.source = source
        self.t_start = now
        self._watch_misses = 0
        self.window_title = _window_title()
        self.actions.submit(self._a_start)
        self.post(self.overlay.show_record, state == "handsfree")
        self.post(self._set_icon, "record")

    def _finish(self) -> None:
        self.state = "idle"
        self.actions.submit(self._a_finish, self.window_title)

    def _cancel(self, silent: bool) -> None:
        self.state = "idle"
        self.actions.submit(self._a_cancel, silent)

    def _pill_click(self) -> None:
        if self.state == "handsfree":
            self.handle("stop", "pill")
        elif self.state == "hold":
            self.handle("cancel", "pill")

    def _watchdog(self) -> None:
        """Fängt verlorene Loslass-Ereignisse und zu lange Aufnahmen ab."""
        if self.state == "idle":
            return
        if time.monotonic() - self.t_start > self.cfg["audio"]["max_seconds"]:
            log.info("Maximale Aufnahmedauer erreicht")
            with self._lock:
                if self.state != "idle":
                    self._finish()
            return
        if self.state == "hold" and self.source == "kb" and self.hotkeys.hold_watchable:
            if hotkeys.physically_down(self.hotkeys.hold):
                self._watch_misses = 0
            else:
                self._watch_misses += 1
                if self._watch_misses >= 4:
                    log.info("Haltetaste nicht mehr gedrückt, beende Aufnahme")
                    self.handle("hold_end", "kb")

    # Aktionen (Aktions-Thread)

    def _a_start(self) -> None:
        try:
            self.sound("start")
            self.recorder.start(self.cfg["audio"]["device"])
        except Exception as e:  # noqa: BLE001
            log.exception("Mikrofon nicht startbar")
            with self._lock:
                self.state = "idle"
            self.post(self.overlay.show_message, _("Mikrofon: {error}", error=e), True, 4)
            self.post(self._set_icon, "idle")
            self.sound("error")

    def _a_finish(self, window_title: str) -> None:
        audio_data = self.recorder.stop()
        self.sound("stop")
        with self._lock:
            self.busy += 1
        self.post(self.overlay.show_busy)
        self.post(self._set_icon, "busy")
        self.processing.submit(self._process, audio_data, window_title)

    def _a_cancel(self, silent: bool) -> None:
        self.recorder.stop()
        if not silent:
            self.sound("cancel")
            self.post(self.overlay.show_message, _("Abgebrochen"), False, 1.0)
        else:
            self.post(self._hide_if_idle)
        self.post(self._set_icon, "idle")

    # Verarbeitung (Verarbeitungs-Thread)

    def _process(self, audio_data, window_title: str) -> None:
        try:
            self._process_inner(audio_data, window_title)
        except Exception as e:  # noqa: BLE001
            log.exception("Verarbeitung fehlgeschlagen")
            self.sound("error")
            self.post(self.overlay.show_message, _("Fehler: {error}", error=e)[:120], True, 5)
        finally:
            with self._lock:
                self.busy -= 1
                busy = self.busy
            if not busy:
                self.post(self._set_icon, "idle")

    def _process_inner(self, audio_data, window_title: str) -> None:
        cfg = self.cfg
        seconds = len(audio_data) / audio.SAMPLE_RATE
        if seconds < 0.3 or audio.rms(audio_data) < 0.0015:
            self.post(self.overlay.show_message, _("Nichts gehört"), False, 1.2)
            return
        terms = cfg["dictionary"]["terms"]
        t0 = time.monotonic()
        raw, engine_used = self.engines.transcribe(cfg, audio_data, ", ".join(terms))
        t1 = time.monotonic()
        raw = (raw or "").strip()
        if not raw:
            self.post(self.overlay.show_message, _("Nichts erkannt"), False, 1.2)
            return
        text = textproc.apply_replacements(raw, cfg["dictionary"]["replacements"])
        snippet = textproc.match_snippet(text, cfg["snippets"])
        cleanup_used = ""
        if snippet is not None:
            text = snippet
            cleanup_used = "Textbaustein"
        elif cfg["cleanup"]["mode"] != "off":
            text, err = cleanup.clean(cfg, text, terms, window_title)
            if err:
                log.warning("Nachbearbeitung: %s", err)
                self.post(self.overlay.show_message, err, True, 2.5)
            else:
                cleanup_used = cfg["cleanup"]["mode"]
                text = textproc.apply_replacements(text, cfg["dictionary"]["replacements"])
        t2 = time.monotonic()
        final = textproc.finalize(text, cfg["paste"]["trailing_space"])
        self._insert(final, cfg)
        log.info("Diktat %.1f s, Erkennung %.2f s (%s), Nachbearbeitung %.2f s, %d Zeichen",
                 seconds, t1 - t0, engine_used, t2 - t1, len(final))
        if cfg["history"]["enabled"]:
            self.history.add(seconds, engine_used, raw, final.strip(), cleanup_used, window_title)
            self.history_seq += 1
        self.post(self._hide_if_idle)

    def _hide_if_idle(self) -> None:
        if self.state == "idle" and not self.busy and self.overlay.mode in ("busy", "record", "handsfree"):
            self.overlay.hide()

    # Modell vorladen

    def _preload(self) -> None:
        if self.cfg["engine"] != "local":
            return
        eng = self.engines.local_engine(self.cfg)
        if eng.loaded:
            return

        def run() -> None:
            self.loading = True
            self.post(self._set_icon, "loading")
            self.post(self._set_status, "Lade Modell …")
            first = not _model_cached(eng.model_name)
            if first:
                self.notify(_("Lade das Erkennungsmodell, beim ersten Mal einige hundert MB. Das kann einige Minuten dauern."))
            try:
                eng.load()
                self.post(self._set_status, "Bereit")
                if first:
                    self.notify(_("Modell geladen. Sayvant ist bereit."))
            except Exception as e:  # noqa: BLE001
                log.exception("Modell nicht ladbar")
                self.post(self._set_status, "Modell fehlt")
                self.notify(_("Modell nicht ladbar: {error}", error=e))
            finally:
                self.loading = False
                self.post(self._set_icon, "idle")

        threading.Thread(target=run, daemon=True, name="modell").start()

    # Tray

    def _set_status(self, text: str) -> None:
        self.status = text
        self._update_tray()

    def _set_icon(self, name: str) -> None:
        if self.tray is None:
            return
        if name == "idle" and self.loading:
            name = "loading"
        if name == "idle" and (self.busy or self.state != "idle"):
            return
        self.tray.icon = self.icons[name]

    def notify(self, text: str) -> None:
        try:
            if self.tray is not None:
                self.tray.notify(text, "Sayvant")
        except Exception:
            log.exception("Benachrichtigung fehlgeschlagen")

    def _tooltip(self) -> str:
        hk = self.cfg["hotkeys"]
        if self.cfg["engine"] == "api":
            p = config.api_profile(self.cfg)
            eng = f"API {p['name']}" if p else "API"
        else:
            eng = engines.LOCAL_MODELS.get(self.cfg["local"]["model"], "lokal").split(" (")[0]
        return _("Sayvant: {status}\n{engine}\nHalten: {hotkey}", status=_(self.status), engine=eng, hotkey=hotkeys.pretty(hk["hold"]))[:127]

    def _update_tray(self) -> None:
        if self.tray is not None:
            self.tray.title = self._tooltip()
            self.tray.update_menu()

    def _menu(self) -> pystray.Menu:
        M, I = pystray.Menu, pystray.MenuItem

        def set_engine(kind: str, pid: str | None = None):
            def act(icon, item):
                def apply():
                    c = copy.deepcopy(self.cfg)
                    c["engine"] = kind
                    if pid:
                        c["api"]["profile"] = pid
                    self.apply_settings(c)
                self.post(apply)
            return act

        def is_engine(kind: str, pid: str | None = None):
            def check(item):
                if self.cfg["engine"] != kind:
                    return False
                return pid is None or self.cfg["api"]["profile"] == pid
            return check

        def set_cleanup(mode: str):
            def act(icon, item):
                def apply():
                    c = copy.deepcopy(self.cfg)
                    c["cleanup"]["mode"] = mode
                    self.apply_settings(c)
                self.post(apply)
            return act

        def engine_items():
            local = engines.LOCAL_MODELS.get(self.cfg["local"]["model"], "Lokal").split(" (")[0]
            items = [I(_("Lokal: {name}", name=local), set_engine("local"), checked=is_engine("local"), radio=True)]
            for p in self.cfg["api"]["profiles"]:
                items.append(I(_("API: {name}", name=p["name"]), set_engine("api", p["id"]), checked=is_engine("api", p["id"]), radio=True))
            return items

        return M(
            I(lambda item: f"Sayvant: {_(self.status)}", None, enabled=False),
            M.SEPARATOR,
            I(_("Erkennung"), M(lambda: engine_items())),
            I(_("Nachbearbeitung"), M(*[
                I(_(label), set_cleanup(mode), checked=lambda i, m=mode: self.cfg["cleanup"]["mode"] == m, radio=True)
                for mode, label in cleanup.MODE_NAMES.items()
            ])),
            I(_("Letztes Diktat erneut einfügen"), lambda icon, item: self.processing.submit(self._paste_last)),
            M.SEPARATOR,
            I(_("Verlauf …"), lambda icon, item: self.post(self.open_history)),
            I(_("Einstellungen …"), lambda icon, item: self.post(self.open_settings), default=True),
            I(_("Protokoll öffnen"), lambda icon, item: os.startfile(config.LOG_FILE)),  # noqa: S606
            M.SEPARATOR,
            I(_("Beenden"), lambda icon, item: self.post(self.quit)),
        )

    def _paste_last(self) -> None:
        row = self.history.last()
        if row and row["final"]:
            time.sleep(0.3)
            text = textproc.finalize(row["final"], self.cfg["paste"]["trailing_space"])
            self._insert(text, self.cfg)

    @staticmethod
    def _insert(text: str, cfg: dict) -> None:
        p = cfg["paste"]
        inject.insert(text, p["method"], p["restore_clipboard"], p["keep_out_of_history"], p["keep_in_clipboard"])

    # Fenster

    def _ui_alive(self) -> bool:
        return self.ui_proc is not None and self.ui_proc.poll() is None

    def _start_ui(self) -> None:
        """Startet das Einstellungsfenster versteckt vor, damit es beim Klick sofort da ist."""
        if self._ui_alive():
            return
        self.ui_pid = 0
        try:
            self.ui_proc = subprocess.Popen(
                runtime.settings_background_command(os.getpid()), cwd=str(ROOT_DIR),
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except OSError:
            log.exception("Einstellungsfenster nicht startbar")
            self.ui_pending = None
            self.notify(_("Einstellungsfenster ließ sich nicht öffnen, siehe Protokoll."))

    def open_settings(self, page: str = "home") -> None:
        """Blendet das vorgestartete Einstellungsfenster ein; ist es noch nicht bereit, sobald es fertig ist."""
        if self._ui_alive():
            # Das Fenster darf sich nach vorn holen, weil der Klick auf das Symbol bei uns ankam.
            # Aus dem Quellcode ist ui_proc nur der Starter der venv, daher die gemeldete PID.
            ctypes.windll.user32.AllowSetForegroundWindow(self.ui_pid or self.ui_proc.pid)
            if (ipc.call("show", timeout=1.0, file=ipc.UI_IPC_FILE, page=page) or {}).get("ok"):
                return
        self.ui_pending = page
        self._start_ui()

    def open_history(self) -> None:
        self.open_settings("history")

    # Verbindung zum Einstellungsfenster (läuft im IPC-Thread)

    def _ipc_handler(self, cmd: str, args: dict) -> dict:
        if cmd == "poll":
            cap = None
            if self._capture is not None and self._capture["done"]:
                cap, self._capture = self._capture, None
            if self.state != "idle":
                state, text = "recording", _("Aufnahme läuft")
            elif self.busy:
                state, text = "busy", _("Verarbeite …")
            elif self.loading:
                state, text = "busy", _("Lade Modell …")
            else:
                state, text = "idle", _("Bereit · {engine}", engine=self._engine_label())
            return {"ok": True, "state": state, "text": text, "capture": cap, "history_seq": self.history_seq}
        if cmd == "ui_ready":
            self.ui_pid = int(args.get("pid") or 0)
            page, self.ui_pending = self.ui_pending, None
            if page:
                ctypes.windll.user32.AllowSetForegroundWindow(self.ui_pid or -1)
            return {"ok": True, "show": page}
        if cmd == "apply":
            self.post(self._reload_settings)
            return {"ok": True}
        if cmd == "capture_start":
            box = {"done": False, "value": ""}
            self._capture = box

            def done(name: str) -> None:
                box["value"] = name
                box["done"] = True

            self.hotkeys.capture(done)
            return {"ok": True}
        if cmd == "capture_cancel":
            self.hotkeys.cancel_capture()
            self._capture = None
            return {"ok": True}
        if cmd == "transcribe_test":
            return self._transcribe_test(args.get("wav_b64", ""))
        return {"ok": False, "error": f"Unbekannter Befehl {cmd}"}

    def _transcribe_test(self, wav_b64: str) -> dict:
        """Testdiktat aus dem Einstellungsfenster: erkennen und nachbearbeiten, nicht einfügen."""
        import base64
        import io
        import wave

        import numpy as np

        try:
            with wave.open(io.BytesIO(base64.b64decode(wav_b64))) as w:
                data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
        except Exception:
            return {"ok": False, "error": "WAV"}
        if audio.rms(data) < 0.0015:
            return {"ok": True, "raw": "", "final": "", "engine": "", "note": _("Nichts gehört")}
        cfg = self.cfg
        t0 = time.monotonic()
        try:
            raw, engine_used = self.engines.transcribe(cfg, data, ", ".join(cfg["dictionary"]["terms"]))
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}
        t1 = time.monotonic()
        text = textproc.apply_replacements((raw or "").strip(), cfg["dictionary"]["replacements"])
        err = None
        if text and cfg["cleanup"]["mode"] != "off":
            text, err = cleanup.clean(cfg, text, cfg["dictionary"]["terms"], "")
        return {"ok": True, "raw": raw, "final": text, "engine": engine_used, "error_cleanup": err,
                "seconds": round(t1 - t0, 2), "total": round(time.monotonic() - t0, 2)}

    def _reload_settings(self) -> None:
        self.apply_settings(config.load())

    def _engine_label(self) -> str:
        if self.cfg["engine"] == "api":
            p = config.api_profile(self.cfg)
            return p["name"] if p else "API"
        return engines.LOCAL_MODELS.get(self.cfg["local"]["model"], "lokal").split(" (")[0]

    # Lebenszyklus

    def run(self) -> None:
        self.tray = pystray.Icon("Sayvant", self.icons["idle"], self._tooltip(), self._menu())
        self.tray.run_detached()
        self.hotkeys.start()
        try:
            self.ipc = ipc.Server(self._ipc_handler)
        except OSError:
            log.exception("Verbindung für das Einstellungsfenster nicht startbar")
        self._preload()
        threading.Thread(target=self._check_autostart, daemon=True, name="autostart").start()
        self.root.after(30, self._pump)
        self.root.after(1500, self._start_ui)
        threading.Thread(target=cleanup.warm_up, args=(self.cfg,), daemon=True, name="vorladen").start()
        log.info("Sayvant gestartet")
        first_run = not (config.APP_DIR / ".gestartet").exists()
        if first_run:
            (config.APP_DIR / ".gestartet").write_text("1")
            self.root.after(800, lambda: self.open_settings("home"))
            self.root.after(1500, lambda: self.notify(
                _("Willkommen bei Sayvant. Halte {hotkey} gedrückt und sprich.", hotkey=hotkeys.pretty(self.cfg["hotkeys"]["hold"]))))
        self.root.mainloop()

    def _check_autostart(self) -> None:
        """Legt die Autostart-Verknüpfung wieder an, falls sie eingeschaltet ist, aber fehlt."""
        if self.cfg["autostart"] and not STARTUP_LNK.exists():
            self._set_autostart(True)
            log.info("Autostart-Verknüpfung angelegt")

    def quit(self) -> None:
        log.info("Sayvant wird beendet")
        self.hotkeys.stop()
        if self.ipc is not None:
            self.ipc.close()
        if self._ui_alive():
            self.ui_proc.terminate()
        try:
            self.recorder.stop()
        except Exception:
            pass
        if self.tray is not None:
            self.tray.stop()
        self.root.quit()


def _model_cached(model: str) -> bool:
    try:
        from huggingface_hub import scan_cache_dir

        # onnx-asr lädt z. B. nemo-parakeet-tdt-0.6b-v3 aus istupakov/parakeet-tdt-0.6b-v3-onnx
        key = model.split("/")[-1].removeprefix("nemo-")
        return any(key in r.repo_id for r in scan_cache_dir().repos)
    except Exception:
        return False


_mutex = None


def _single_instance() -> bool:
    global _mutex
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    _mutex = kernel32.CreateMutexW(None, False, "Local\\SayvantDiktat")
    return ctypes.get_last_error() != 183  # ERROR_ALREADY_EXISTS


def setup_logging(console: bool) -> None:
    config.APP_DIR.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.handlers.RotatingFileHandler(config.LOG_FILE, maxBytes=1_000_000, backupCount=2, encoding="utf-8")
    ]
    if console and sys.stderr:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", handlers=handlers)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    # Hugging Face warnt unter Windows ohne Entwicklermodus bei jedem Laden wegen Symlinks
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    # Unter pythonw gibt es keine Konsole; Bibliotheken, die dorthin schreiben, würden abstürzen
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
    console = "--console" in sys.argv
    setup_logging(console)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    try:
        i18n.set_language(config.load().get("ui_language", "auto"))
    except Exception:
        log.exception("Einstellungen nicht lesbar")
    if not _single_instance():
        ctypes.windll.user32.MessageBoxW(None, _("Sayvant läuft bereits (Symbol im Infobereich)."), "Sayvant", 0x40)
        return
    App().run()

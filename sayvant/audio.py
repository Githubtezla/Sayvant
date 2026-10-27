"""Mikrofonaufnahme mit 16 kHz Mono, Pegel für die Anzeige und WAV-Kodierung."""
from __future__ import annotations

import io
import logging
import threading
import time
import wave

import numpy as np
import sounddevice as sd

log = logging.getLogger(__name__)
SAMPLE_RATE = 16000


def input_devices() -> list[str]:
    """Namen der Eingabegeräte (MME, damit jedes Gerät nur einmal erscheint)."""
    try:
        apis = sd.query_hostapis()
        mme = next((i for i, a in enumerate(apis) if a["name"] == "MME"), None)
        names = []
        for d in sd.query_devices():
            if d["max_input_channels"] > 0 and (mme is None or d["hostapi"] == mme):
                if d["name"] not in names and "Microsoft Sound Mapper" not in d["name"]:
                    names.append(d["name"])
        return names
    except Exception:
        log.exception("Geräteliste nicht lesbar")
        return []


def _resolve_device(name: str):
    if not name:
        return None
    try:
        apis = sd.query_hostapis()
        mme = next((i for i, a in enumerate(apis) if a["name"] == "MME"), None)
        for i, d in enumerate(sd.query_devices()):
            if d["name"] == name and d["max_input_channels"] > 0 and (mme is None or d["hostapi"] == mme):
                return i
    except Exception:
        log.exception("Gerät %s nicht auflösbar", name)
    log.warning("Mikrofon %r nicht gefunden, nehme Standardgerät", name)
    return None


class Recorder:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stream: sd.InputStream | None = None
        self._chunks: list[np.ndarray] = []
        self._rate = SAMPLE_RATE
        self.level = 0.0
        self.started = 0.0

    @property
    def active(self) -> bool:
        return self._stream is not None

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.started if self.active else 0.0

    def _callback(self, indata, frames, t, status) -> None:
        mono = indata[:, 0].copy()
        self._chunks.append(mono)
        rms = float(np.sqrt(np.mean(mono * mono))) if len(mono) else 0.0
        # Pegel weich nachführen, damit die Balken nicht flackern
        self.level = max(rms, self.level * 0.75)

    def start(self, device_name: str = "") -> None:
        with self._lock:
            if self._stream is not None:
                return
            self._chunks = []
            self.level = 0.0
            device = _resolve_device(device_name)
            for rate in (SAMPLE_RATE, None):
                try:
                    if rate is None:
                        info = sd.query_devices(device, "input")
                        rate = int(info["default_samplerate"])
                    stream = sd.InputStream(
                        samplerate=rate, channels=1, dtype="float32", device=device,
                        blocksize=int(rate * 0.05), callback=self._callback,
                    )
                    stream.start()
                    self._stream = stream
                    self._rate = rate
                    break
                except Exception:
                    if rate == SAMPLE_RATE:
                        log.info("16 kHz nicht möglich, versuche Geräterate")
                        continue
                    raise
            self.started = time.monotonic()

    def stop(self) -> np.ndarray:
        with self._lock:
            stream, self._stream = self._stream, None
        if stream is not None:
            try:
                stream.stop()
                stream.close()
            except Exception:
                log.exception("Aufnahme ließ sich nicht sauber schließen")
        self.level = 0.0
        if not self._chunks:
            return np.zeros(0, dtype=np.float32)
        audio = np.concatenate(self._chunks).astype(np.float32)
        self._chunks = []
        if self._rate != SAMPLE_RATE and len(audio):
            n = int(len(audio) * SAMPLE_RATE / self._rate)
            audio = np.interp(
                np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio
            ).astype(np.float32)
        return audio


def rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(audio * audio))) if len(audio) else 0.0


def to_wav(audio: np.ndarray) -> bytes:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def make_tone(path, freqs: list[float], dur: float = 0.07, volume: float = 0.25) -> None:
    """Schreibt einen kurzen Signalton (eine oder mehrere Stufen) als WAV."""
    rate = 44100
    parts = []
    for f in freqs:
        t = np.linspace(0, dur, int(rate * dur), endpoint=False)
        tone = np.sin(2 * np.pi * f * t)
        fade = np.minimum(1, np.minimum(t, dur - t) / 0.01)
        parts.append(tone * fade * volume)
    data = (np.concatenate(parts) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())

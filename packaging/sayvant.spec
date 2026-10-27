# PyInstaller-Bauanleitung für Sayvant.exe (Ordner-Variante, startet schneller und
# wird seltener von Virenscannern fälschlich gemeldet als eine Einzeldatei).
# Aufruf über packaging\build.ps1
import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

ROOT = Path(SPECPATH).parent
BUILD = ROOT / "build"

datas = [(str(ROOT / "sayvant" / "webui"), "sayvant/webui")]
datas += collect_data_files("onnx_asr")
# Einige Pakete lesen zur Laufzeit ihre eigene Versionsangabe oder Einstiegspunkte
for dist in ("onnx-asr", "onnxruntime", "huggingface-hub", "anthropic", "httpx", "keyring", "tqdm", "pywebview", "numpy"):
    try:
        datas += copy_metadata(dist)
    except Exception:
        pass

hiddenimports = [
    "pynput.keyboard._win32",
    "pynput.mouse._win32",
    "pystray._win32",
    "keyring.backends.Windows",
    "webview.platforms.edgechromium",
    "webview.platforms.winforms",
    "clr",
]
hiddenimports += collect_submodules("onnx_asr")

a = Analysis(
    [str(ROOT / "packaging" / "sayvant_entry.py")],
    pathex=[str(ROOT)],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["matplotlib", "pandas", "scipy", "IPython", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Sayvant",
    console=False,
    icon=str(BUILD / "sayvant.ico"),
    version=str(BUILD / "version.txt"),
)
coll = COLLECT(exe, a.binaries, a.datas, name="Sayvant")

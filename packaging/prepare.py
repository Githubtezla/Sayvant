"""Erzeugt Symbol und Versionsangaben für den Build (build/sayvant.ico, build/version.txt)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sayvant import __version__  # noqa: E402
from sayvant.icons import icon_image  # noqa: E402

build = ROOT / "build"
build.mkdir(exist_ok=True)
icon_image(size=256).save(build / "sayvant.ico", sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (128, 128), (256, 256)])

parts = [int(p) for p in __version__.split(".")[:3]] + [0]
nums = ", ".join(str(p) for p in parts[:4])
(build / "version.txt").write_text(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers=({nums}), prodvers=({nums}), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040704b0', [
      StringStruct('CompanyName', 'Githubtezla'),
      StringStruct('FileDescription', 'Sayvant'),
      StringStruct('FileVersion', '{__version__}'),
      StringStruct('InternalName', 'Sayvant'),
      StringStruct('LegalCopyright', 'MIT License'),
      StringStruct('OriginalFilename', 'Sayvant.exe'),
      StringStruct('ProductName', 'Sayvant'),
      StringStruct('ProductVersion', '{__version__}')])]),
    VarFileInfo([VarStruct('Translation', [1031, 1200, 1033, 1200])])
  ]
)
""", encoding="utf-8")
print(__version__)

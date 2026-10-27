"""Programmsymbol: abgerundetes Quadrat mit Farbverlauf und weißem Mikrofon."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from . import config

TERRACOTTA = ((226, 140, 108), (180, 87, 47))
INDIGO = TERRACOTTA  # alter Name, Standardfarbe
# Farbverlauf des Symbols je Design
DESIGN_COLORS = {
    "creme": ((222, 140, 108), (95, 165, 168)),
    "modern": ((124, 116, 255), (61, 139, 255)),
    "graphite": ((70, 70, 76), (17, 17, 19)),
}
RED = ((255, 95, 80), (220, 38, 60))
AMBER = ((255, 196, 80), (240, 140, 30))
GRAY = ((150, 150, 160), (110, 110, 122))
ICO_FILE = config.APP_DIR / "sayvant-2.ico"


def icon_image(colors: tuple = INDIGO, size: int = 64) -> Image.Image:
    """In 256 px gezeichnet und verkleinert, damit die Kanten weich bleiben."""
    top, bottom = colors
    n = 256
    yy, xx = np.mgrid[0:n, 0:n]
    t = ((xx + yy) / (2 * (n - 1)))[..., None]
    rgb = np.array(top) * (1 - t) + np.array(bottom) * t
    fill = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).rounded_rectangle((8, 8, n - 8, n - 8), radius=58, fill=255)
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    img.paste(fill, (0, 0), mask)
    d = ImageDraw.Draw(img)
    w = (255, 255, 255, 255)
    d.rounded_rectangle((100, 48, 156, 146), radius=28, fill=w)
    d.arc((72, 86, 184, 182), start=0, end=180, fill=w, width=16)
    d.line((128, 182, 128, 210), fill=w, width=16)
    return img if size == n else img.resize((size, size), Image.LANCZOS)


def ensure_ico(design: str = "creme") -> str:
    """Schreibt das Symbol des Designs als .ico (für Fenster und Verknüpfungen) und liefert den Pfad."""
    path = config.APP_DIR / f"sayvant-{design}.ico"
    if not path.exists():
        config.APP_DIR.mkdir(parents=True, exist_ok=True)
        colors = DESIGN_COLORS.get(design, DESIGN_COLORS["creme"])
        icon_image(colors, size=256).save(path, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (256, 256)])
    return str(path)

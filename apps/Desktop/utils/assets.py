"""Resolución de rutas a los recursos empaquetados con la aplicación."""

from __future__ import annotations

from pathlib import Path

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

_POPPINS_WEIGHTS = (
    "Poppins-Regular.ttf",
    "Poppins-Medium.ttf",
    "Poppins-SemiBold.ttf",
    "Poppins-Bold.ttf",
)


def icon_path(name: str) -> Path:
    """Ruta a un icono SVG, por ejemplo ``point.svg``."""
    return _ASSETS_DIR / "icons" / name


def image_path(name: str) -> Path:
    """Ruta a una imagen de marca, por ejemplo ``marca.png``."""
    return _ASSETS_DIR / "images" / name


def font_paths() -> tuple[Path, ...]:
    """Las cuatro variantes de Poppins que usa la interfaz."""
    return tuple(_ASSETS_DIR / "fonts" / name for name in _POPPINS_WEIGHTS)

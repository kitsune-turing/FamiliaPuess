"""Registro de las tipografías de marca en la aplicación Qt."""

from __future__ import annotations

from PySide6.QtGui import QFontDatabase

from apps.Desktop.utils.assets import font_paths


def register_application_fonts() -> list[int]:
    """
    Carga Poppins en la base de datos de fuentes de Qt.

    Debe llamarse después de crear la QApplication y antes de construir la
    ventana, o los widgets se dibujarán con la tipografía del sistema.
    Devuelve los identificadores que asigna Qt; -1 indica que la carga falló.
    """
    return [QFontDatabase.addApplicationFont(str(ruta)) for ruta in font_paths()]

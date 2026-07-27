from PySide6.QtGui import QFontDatabase

from apps.Desktop.utils.assets import font_paths


def register_application_fonts() -> list[int]:
    return [QFontDatabase.addApplicationFont(str(path)) for path in font_paths()]

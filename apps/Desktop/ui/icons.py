from PySide6.QtCore import QSize
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QWidget

from apps.Desktop.utils.assets import icon_path


def _svg_icon(filename: str, size: int, parent: QWidget | None) -> QSvgWidget:
    widget = QSvgWidget(str(icon_path(filename)), parent)
    widget.setFixedSize(QSize(size, size))
    return widget


def location_pin_icon(parent: QWidget | None = None, size: int = 48) -> QSvgWidget:
    return _svg_icon("point.svg", size, parent)


def clock_icon(parent: QWidget | None = None, size: int = 48) -> QSvgWidget:
    return _svg_icon("time.svg", size, parent)


def wifi_icon(parent: QWidget | None = None, size: int = 32) -> QSvgWidget:
    return _svg_icon("wifi.svg", size, parent)

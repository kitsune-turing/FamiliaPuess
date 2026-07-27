from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class LocationPinIcon(QWidget):
    def __init__(self, color: str = "#F2B84B", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(48, 48)

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override signature)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(10, 4, 28, 28))
        painter.drawPolygon(
            [QPoint(14, 24), QPoint(34, 24), QPoint(24, 44)]
        )
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(QRectF(18, 12, 12, 12))


class ClockIcon(QWidget):
    def __init__(self, color: str = "#FFFFFF", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(48, 48)

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override signature)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self._color, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(4, 4, 40, 40))
        painter.drawLine(24, 24, 24, 12)
        painter.drawLine(24, 24, 33, 28)

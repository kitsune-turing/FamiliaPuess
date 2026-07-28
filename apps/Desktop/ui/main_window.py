from datetime import datetime

from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from apps.Desktop.api.token_client import TokenRecibido
from apps.Desktop.services.qr_service import build_qr_pixmap
from apps.Desktop.ui.icons import clock_icon, location_pin_icon, wifi_icon
from apps.Desktop.utils.assets import image_path
from apps.Desktop.utils.formatting import format_datetime_es

COLOR_BACKGROUND = "#F9EAD8"
COLOR_HEADER = "#4C1F06"
COLOR_BADGE = "#6A3F26"
COLOR_ACCENT_PINK = "#F24976"
COLOR_PILL_GREEN = "#6DB144"
COLOR_TEXT_DARK = "#3B2415"
COLOR_CODE_BOX = "#F0E0C8"
COLOR_DISCONNECTED = "#F24976"
COLOR_WAVE_PINK = "#F24976"
COLOR_WAVE_YELLOW = "#F2A20C"
COLOR_WAVE_ORANGE = "#E8792B"

FONT_FAMILY = "Poppins"

DESIGN_W = 1728
DESIGN_H = 1117


class _WaveBandsWidget(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w = self.width()
        h = self.height()

        bands = [
            (COLOR_WAVE_PINK, 0.0),
            (COLOR_WAVE_YELLOW, 0.30),
            (COLOR_WAVE_ORANGE, 0.55),
        ]
        band_height = h * 0.35

        for color_hex, y_ratio in bands:
            y_start = h * y_ratio
            path = QPainterPath()
            path.moveTo(0, y_start + band_height * 0.6)
            path.cubicTo(
                QPointF(w * 0.25, y_start),
                QPointF(w * 0.75, y_start + band_height * 0.4),
                QPointF(w, y_start - band_height * 0.1),
            )
            path.lineTo(w, y_start + band_height)
            path.cubicTo(
                QPointF(w * 0.75, y_start + band_height * 1.4),
                QPointF(w * 0.25, y_start + band_height * 0.7),
                QPointF(0, y_start + band_height * 1.2),
            )
            path.closeSubpath()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color_hex))
            painter.drawPath(path)

        painter.end()


class _HeartWidget(QWidget):

    def __init__(self, color: str, size: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self._color))
        w = self.width()
        h = self.height()
        path = QPainterPath()
        path.moveTo(w * 0.5, h * 0.85)
        path.cubicTo(QPointF(0, h * 0.55), QPointF(0, h * 0.1), QPointF(w * 0.5, h * 0.3))
        path.cubicTo(QPointF(w, h * 0.1), QPointF(w, h * 0.55), QPointF(w * 0.5, h * 0.85))
        painter.drawPath(path)
        painter.end()


class DesktopMainWindow(QWidget):
    """Pantalla unica del Sistema de Escritorio (HU-ESC-005).

    Es un QWidget puro (no QMainWindow): nunca existira menuBar, toolbar,
    statusBar ni dock widgets, porque esas capacidades no existen en QWidget.

    La ventana ocupa el 80 % de la pantalla (10 % de margen en cada lado)
    y escala todos los elementos proporcionalmente desde el diseno de
    referencia 1728 x 1117.
    """

    def __init__(
        self,
        registro_publico_url: str,
        dispositivo_identificador: str,
        sede_nombre: str = "Sede principal",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._registro_publico_url = registro_publico_url

        screen = QApplication.primaryScreen().availableGeometry()
        self._cw = int(screen.width() * 0.8)
        self._ch = int(screen.height() * 0.8)
        self._kx = self._cw / DESIGN_W
        self._ky = self._ch / DESIGN_H
        self._ks = min(self._kx, self._ky)

        self.setWindowTitle("Familia Puess - Control de Asistencia")
        self.setFixedSize(self._cw, self._ch)
        self.move(
            screen.x() + (screen.width() - self._cw) // 2,
            screen.y() + (screen.height() - self._ch) // 2,
        )
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")

        self._build_background_decorations()
        self._build_header(dispositivo_identificador, sede_nombre)
        self._build_left_panel()
        self._build_qr_panel()
        self._build_decorative_waves()
        self._build_footer()

    def _x(self, v: float) -> int:
        return int(v * self._kx)

    def _y(self, v: float) -> int:
        return int(v * self._ky)

    def _s(self, v: float) -> int:
        return max(1, int(v * self._ks))

    def _image_label(
        self,
        parent: QWidget,
        filename: str,
        x: int,
        y: int,
        w: int,
        h: int,
        mirror: bool = False,
    ) -> QLabel:
        pixmap = QPixmap(str(image_path(filename)))
        if mirror:
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))
        pixmap = pixmap.scaled(
            w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        label = QLabel(parent)
        label.setPixmap(pixmap)
        label.setGeometry(x, y, w, h)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _build_background_decorations(self) -> None:
        self._image_label(
            self, "mazorca1.png", self._x(-140), self._y(160), self._x(374), self._y(618)
        ).lower()
        self._image_label(
            self, "mazorca1.png", self._x(1494), self._y(340), self._x(374), self._y(618),
            mirror=True,
        ).lower()

    def _build_header(self, dispositivo_identificador: str, sede_nombre: str) -> None:
        header = QWidget(self)
        header.setGeometry(0, 0, self._cw, self._y(133))
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header.setStyleSheet(f"background-color: {COLOR_HEADER};")

        self._image_label(header, "marca.png", 0, self._y(19), self._x(484), self._y(95))

        titulo = QLabel("SISTEMA DE CONTROL DE ASISTENCIA", header)
        titulo.setGeometry(self._x(573), self._y(48), self._x(582), self._y(38))
        titulo.setStyleSheet(
            f"color: #FFFFFF; font-size: {self._s(27)}px; "
            f"font-family: '{FONT_FAMILY}'; letter-spacing: {self._s(1)}px;"
        )

        badge = QWidget(header)
        badge.setGeometry(self._x(1354), self._y(24), self._x(259), self._y(84))
        badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        badge.setStyleSheet(
            f"background-color: {COLOR_BADGE}; border-radius: {self._s(15)}px;"
        )

        location_pin_icon(badge).move(self._x(11), self._y(18))

        masked_identificador = "*" * len(dispositivo_identificador)
        sede_label = QLabel(f"{sede_nombre}\nDispositivo: {masked_identificador}", badge)
        sede_label.setGeometry(self._x(59), self._y(15), self._x(193), self._y(55))
        sede_label.setStyleSheet(
            f"color: #FFFFFF; font-size: {self._s(15)}px; font-family: '{FONT_FAMILY}';"
        )

    def _build_left_panel(self) -> None:
        greeting = QLabel("¡Hola!", self)
        greeting.setGeometry(self._x(60), self._y(190), self._x(500), self._y(90))
        greeting.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: {self._s(64)}px; font-weight: 800; "
            f"font-family: '{FONT_FAMILY}';"
        )

        subtitle = QLabel("Marca tu asistencia\nEscanea el QR o ingresa el código", self)
        subtitle.setGeometry(self._x(65), self._y(300), self._x(620), self._y(70))
        subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: {self._s(20)}px; font-weight: 600; "
            f"font-family: '{FONT_FAMILY}';"
        )

        self._image_label(
            self, "logos.png", self._x(60), self._y(395), self._x(560), self._y(210)
        )

        codigo_titulo = QLabel("Código de validación", self)
        codigo_titulo.setGeometry(self._x(65), self._y(630), self._x(400), self._y(34))
        codigo_titulo.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: {self._s(20)}px; font-weight: 700; "
            f"font-family: '{FONT_FAMILY}';"
        )

        codigo_box = QWidget(self)
        box_w = self._x(560)
        box_h = self._y(130)
        codigo_box.setGeometry(self._x(65), self._y(675), box_w, box_h)
        codigo_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        codigo_box.setStyleSheet(
            f"background-color: {COLOR_CODE_BOX}; border-radius: {self._s(20)}px;"
        )

        self._codigo_label = QLabel("--------", codigo_box)
        self._codigo_label.setGeometry(0, 0, box_w, box_h)
        self._codigo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._codigo_label.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: {self._s(48)}px; font-weight: 800; "
            f"letter-spacing: {self._s(6)}px; font-family: '{FONT_FAMILY}';"
        )

    def _build_qr_panel(self) -> None:
        box_w = self._x(590)
        box_h = self._y(683)

        box = QWidget(self)
        box.setGeometry(self._x(966), self._y(207), box_w, box_h)
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setStyleSheet("background-color: transparent;")

        pill_w = self._x(358)
        pill_h = self._y(85)
        pill = QWidget(box)
        pill.setGeometry(self._x(115), self._y(40), pill_w, pill_h)
        pill.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        pill.setStyleSheet(
            f"background-color: {COLOR_ACCENT_PINK}; border-radius: {self._s(15)}px;"
        )

        clock_icon(pill).move(self._x(30), self._y(19))

        self._timer_label = QLabel("VALIDO POR\n-- SEGUNDOS", pill)
        self._timer_label.setGeometry(self._x(86), self._y(11), self._x(188), self._y(73))
        self._timer_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self._timer_label.setStyleSheet(
            f"color: #FFFFFF; font-size: {self._s(18)}px; font-weight: 700; "
            f"font-family: '{FONT_FAMILY}';"
        )

        qr_size = self._s(380)
        pad = self._s(20)
        inner_side = qr_size + pad * 2

        inner = QWidget(box)
        inner_x = (box_w - inner_side) // 2
        inner_y = self._y(40) + pill_h + self._y(30)
        inner.setGeometry(inner_x, inner_y, inner_side, inner_side)
        inner.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        inner.setStyleSheet(
            f"background-color: #FFFFFF; border-radius: {self._s(18)}px;"
        )

        self._qr_label = QLabel(inner)
        self._qr_label.setGeometry(pad, pad, qr_size, qr_size)
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        caption_pill_w = self._x(380)
        caption_pill_h = self._y(60)
        caption_pill = QWidget(box)
        caption_pill.setGeometry(
            (box_w - caption_pill_w) // 2,
            box_h - self._y(90),
            caption_pill_w,
            caption_pill_h,
        )
        caption_pill.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        caption_pill.setStyleSheet(
            f"background-color: #F2DDB6; border-radius: {self._s(14)}px;"
        )

        caption = QLabel("Código único y seguro\nNo compartas este código", caption_pill)
        caption.setGeometry(0, 0, caption_pill_w, caption_pill_h)
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: {self._s(14)}px; font-weight: 600; "
            f"font-family: '{FONT_FAMILY}';"
        )

    def _build_decorative_waves(self) -> None:
        wave_height = self._y(120)
        footer_height = self._y(80)
        wave_y = self._ch - footer_height - wave_height

        waves = _WaveBandsWidget(self)
        waves.setGeometry(0, wave_y, self._cw, wave_height)
        waves.lower()

        _HeartWidget(COLOR_ACCENT_PINK, self._s(28), self).move(
            self._x(1520), wave_y + self._y(10)
        )
        _HeartWidget(COLOR_ACCENT_PINK, self._s(18), self).move(
            self._x(1560), wave_y + self._y(45)
        )
        _HeartWidget(COLOR_WAVE_YELLOW, self._s(22), self).move(
            self._x(750), wave_y + self._y(20)
        )

    def _build_footer(self) -> None:
        footer = QWidget(self)
        footer_h = self._y(80)
        footer.setGeometry(0, self._ch - footer_h, self._cw, footer_h)
        footer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        footer.setStyleSheet(f"background-color: {COLOR_HEADER};")

        clock_icon(footer).move(self._x(30), self._y(16))

        self._datetime_label = QLabel(footer)
        self._datetime_label.setGeometry(self._x(90), self._y(8), self._x(500), self._y(60))
        self._datetime_label.setStyleSheet(
            f"color: #FFFFFF; font-size: {self._s(15)}px; font-family: '{FONT_FAMILY}';"
        )

        self._wifi_icon = wifi_icon(footer, size=self._s(28))
        self._wifi_icon.move(self._cw - self._x(380), self._y(16))
        self._wifi_icon.setVisible(False)

        self._connection_label = QLabel("Conectando...", footer)
        self._connection_label.setGeometry(
            self._cw - self._x(330), self._y(12), self._x(260), self._y(30)
        )
        self._connection_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._connection_label.setStyleSheet(
            f"color: #FFFFFF; font-size: {self._s(16)}px; font-weight: 700; "
            f"font-family: '{FONT_FAMILY}';"
        )

        version_label = QLabel("Version: 1.0.0", footer)
        version_label.setGeometry(
            self._cw - self._x(330), self._y(42), self._x(220), self._y(24)
        )
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        version_label.setStyleSheet(
            f"color: #FFFFFF; font-size: {self._s(13)}px; font-family: '{FONT_FAMILY}';"
        )

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._refresh_datetime_label)
        self._clock_timer.start(1000)
        self._refresh_datetime_label()

    def _refresh_datetime_label(self) -> None:
        self._datetime_label.setText(format_datetime_es(datetime.now()))

    def update_token(self, token: TokenRecibido) -> None:
        pixmap = build_qr_pixmap(token.token, self._registro_publico_url)
        self._qr_label.setPixmap(
            pixmap.scaled(
                self._qr_label.width(),
                self._qr_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self._codigo_label.setText(token.codigo_alfa)

        validez_segundos = max(1, round((token.expira_en - token.generado_en).total_seconds()))
        self._timer_label.setText(f"VALIDO POR\n{validez_segundos} SEGUNDOS")

    def set_connection_status(self, connected: bool) -> None:
        self._wifi_icon.setVisible(connected)
        if connected:
            self._connection_label.setText("Connected")
            self._connection_label.setStyleSheet(
                f"color: #FFFFFF; font-size: {self._s(16)}px; font-weight: 700; "
                f"font-family: '{FONT_FAMILY}';"
            )
        else:
            self._connection_label.setText("Sin conexión")
            self._connection_label.setStyleSheet(
                f"color: {COLOR_DISCONNECTED}; font-size: {self._s(16)}px; font-weight: 700; "
                f"font-family: '{FONT_FAMILY}';"
            )

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QLabel, QWidget

from apps.Desktop.api.token_client import TokenRecibido
from apps.Desktop.services.qr_service import build_qr_pixmap
from apps.Desktop.ui.icons import clock_icon, location_pin_icon, wifi_icon
from apps.Desktop.utils.assets import image_path
from apps.Desktop.utils.formatting import format_datetime_es

COLOR_BACKGROUND = "#FBEFDE"
COLOR_HEADER = "#401801"
COLOR_BADGE = "#4C3523"
COLOR_ACCENT_PINK = "#F24976"
COLOR_TEXT_DARK = "#3B2415"
COLOR_CODE_BOX = "#E9D7B3"
COLOR_DISCONNECTED = "#F24976"

FONT_FAMILY = "Poppins"


class DesktopMainWindow(QWidget):
    """Pantalla unica del Sistema de Escritorio (HU-ESC-005).

    Es un QWidget puro (no QMainWindow): nunca existira menuBar, toolbar,
    statusBar ni dock widgets, porque esas capacidades no existen en QWidget.
    """

    CANVAS_WIDTH = 1728
    CANVAS_HEIGHT = 1117

    def __init__(
        self,
        registro_publico_url: str,
        dispositivo_identificador: str,
        sede_nombre: str = "Sede principal",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._registro_publico_url = registro_publico_url
        self.setWindowTitle("Familia Puess - Control de Asistencia")
        self.setFixedSize(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")

        self._build_background_decorations()
        self._build_header(dispositivo_identificador, sede_nombre)
        self._build_left_panel()
        self._build_qr_panel()
        self._build_footer()

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
        # Solo se entrego un asset de mazorca; se reutiliza en ambos costados
        # (el derecho reflejado) para aproximar la composicion original de Figma.
        self._image_label(self, "mazorca1.png", -140, 160, 374, 618).lower()
        self._image_label(self, "mazorca1.png", 1494, 340, 374, 618, mirror=True).lower()

    def _build_header(self, dispositivo_identificador: str, sede_nombre: str) -> None:
        header = QWidget(self)
        header.setGeometry(0, 0, self.CANVAS_WIDTH, 133)
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header.setStyleSheet(f"background-color: {COLOR_HEADER};")

        self._image_label(header, "marca.png", 0, 19, 484, 95)

        titulo = QLabel("SISTEMA DE CONTROL DE ASISTENCIA", header)
        titulo.setGeometry(573, 48, 582, 38)
        titulo.setStyleSheet(
            f"color: #FFFFFF; font-size: 27px; font-family: '{FONT_FAMILY}'; letter-spacing: 1px;"
        )

        badge = QWidget(header)
        badge.setGeometry(1354, 24, 259, 84)
        badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        badge.setStyleSheet(f"background-color: {COLOR_BADGE}; border-radius: 15px;")

        location_pin_icon(badge).move(11, 18)

        masked_identificador = "*" * len(dispositivo_identificador)
        sede_label = QLabel(f"{sede_nombre}\nDispositivo: {masked_identificador}", badge)
        sede_label.setGeometry(59, 15, 193, 55)
        sede_label.setStyleSheet(
            f"color: #FFFFFF; font-size: 15px; font-family: '{FONT_FAMILY}';"
        )

    def _build_left_panel(self) -> None:
        greeting = QLabel("¡Hola!", self)
        greeting.setGeometry(60, 190, 500, 90)
        greeting.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: 64px; font-weight: 800; "
            f"font-family: '{FONT_FAMILY}';"
        )

        subtitle = QLabel("Marca tu asistencia\nEscanea el QR o ingresa el código", self)
        subtitle.setGeometry(65, 300, 620, 70)
        subtitle.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: 20px; font-weight: 600; "
            f"font-family: '{FONT_FAMILY}';"
        )

        self._image_label(self, "logos.png", 60, 395, 560, 210)

        codigo_titulo = QLabel("Código de validación", self)
        codigo_titulo.setGeometry(65, 630, 400, 34)
        codigo_titulo.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: 20px; font-weight: 700; "
            f"font-family: '{FONT_FAMILY}';"
        )

        codigo_box = QWidget(self)
        codigo_box.setGeometry(65, 675, 560, 130)
        codigo_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        codigo_box.setStyleSheet(f"background-color: {COLOR_CODE_BOX}; border-radius: 20px;")

        self._codigo_label = QLabel("--------", codigo_box)
        self._codigo_label.setGeometry(0, 0, 560, 130)
        self._codigo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._codigo_label.setStyleSheet(
            f"color: {COLOR_TEXT_DARK}; font-size: 48px; font-weight: 800; "
            f"letter-spacing: 6px; font-family: '{FONT_FAMILY}';"
        )

    def _build_qr_panel(self) -> None:
        box = QWidget(self)
        box.setGeometry(966, 207, 590, 683)
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setStyleSheet(
            f"background-color: rgba(217, 217, 217, 0); "
            f"border: 10px solid {COLOR_ACCENT_PINK}; border-radius: 30px;"
        )

        pill = QWidget(box)
        pill.setGeometry(1081 - 966, 247 - 207, 358, 85)
        pill.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        pill.setStyleSheet(f"background-color: {COLOR_ACCENT_PINK}; border-radius: 15px;")

        clock_icon(pill).move(1111 - 1081, 266 - 247)

        self._timer_label = QLabel("VALIDO POR\n-- SEGUNDOS", pill)
        self._timer_label.setGeometry(1167 - 1081, 258 - 247, 188, 73)
        self._timer_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self._timer_label.setStyleSheet(
            f"color: #FFFFFF; font-size: 18px; font-weight: 700; font-family: '{FONT_FAMILY}';"
        )

        qr_size = 380
        qr_x = (590 - qr_size) // 2
        self._qr_label = QLabel(box)
        self._qr_label.setGeometry(qr_x, 247 - 207 + 85 + 40, qr_size, qr_size)
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        caption = QLabel("Código único y seguro\nNo compartas este código", box)
        caption.setGeometry(45, 683 - 95, 500, 60)
        caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        caption.setStyleSheet(
            f"color: {COLOR_BADGE}; font-size: 16px; font-weight: 600; "
            f"font-family: '{FONT_FAMILY}';"
        )

    def _build_footer(self) -> None:
        footer = QWidget(self)
        footer_height = 80
        footer.setGeometry(0, self.CANVAS_HEIGHT - footer_height, self.CANVAS_WIDTH, footer_height)
        footer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        footer.setStyleSheet(f"background-color: {COLOR_HEADER};")

        clock_icon(footer).move(30, 16)

        self._datetime_label = QLabel(footer)
        self._datetime_label.setGeometry(90, 8, 500, 60)
        self._datetime_label.setStyleSheet(
            f"color: #FFFFFF; font-size: 15px; font-family: '{FONT_FAMILY}';"
        )

        self._wifi_icon = wifi_icon(footer, size=28)
        self._wifi_icon.move(self.CANVAS_WIDTH - 370, 16)
        self._wifi_icon.setVisible(False)

        self._connection_label = QLabel("Conectando...", footer)
        self._connection_label.setGeometry(self.CANVAS_WIDTH - 330, 12, 220, 30)
        self._connection_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        version_label = QLabel("Version: 1.0.0", footer)
        version_label.setGeometry(self.CANVAS_WIDTH - 330, 42, 220, 24)
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        version_label.setStyleSheet(
            f"color: #FFFFFF; font-size: 13px; font-family: '{FONT_FAMILY}';"
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
                f"color: #FFFFFF; font-size: 16px; font-weight: 700; "
                f"font-family: '{FONT_FAMILY}';"
            )
        else:
            self._connection_label.setText("Sin conexión")
            self._connection_label.setStyleSheet(
                f"color: {COLOR_DISCONNECTED}; font-size: 16px; font-weight: 700; "
                f"font-family: '{FONT_FAMILY}';"
            )

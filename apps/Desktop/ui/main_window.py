"""
Pantalla única del kiosco de asistencia.

Es un `QWidget` y no un `QMainWindow` a propósito: un kiosco no debe poder
mostrar menús, barras de herramientas ni barra de estado. Por la misma razón
no hay pestañas ni pilas de páginas; la aplicación tiene una sola vista.
"""

from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import QByteArray, Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from apps.Desktop.api.token_client import TokenRecibido
from apps.Desktop.services.qr_service import build_qr_pixmap
from apps.Desktop.utils.assets import icon_path, image_path
from apps.Desktop.utils.formatting import format_datetime_es

# ------------------------------------------------------------ Colores ----

CAFE_OSCURO = "#3B1A0B"
CAFE = "#4A2110"
CREMA = "#FDF3E4"
CREMA_CAJA = "#F6E7CE"
ROSA = "#F24976"
ROSA_SUAVE = "#FBD7E1"
AMARILLO = "#F2A20C"
BLANCO = "#FFFFFF"
TEXTO_TENUE = "#B99A7E"

TAMANO_QR = 250


def _svg(nombre: str, color: str, lado: int) -> QSvgWidget:
    """
    Carga un icono SVG con el color indicado.

    Los archivos usan `currentColor`, que QtSvg no resuelve, así que se
    sustituye el valor antes de entregar el contenido al widget.
    """
    contenido = icon_path(nombre).read_text(encoding="utf-8")
    contenido = contenido.replace("currentColor", color)

    widget = QSvgWidget()
    widget.load(QByteArray(contenido.encode("utf-8")))
    widget.setFixedSize(lado, lado)
    return widget


def _etiqueta(texto: str, estilo: str, alineacion=Qt.AlignmentFlag.AlignLeft) -> QLabel:
    etiqueta = QLabel(texto)
    etiqueta.setStyleSheet(estilo)
    etiqueta.setAlignment(alineacion)
    return etiqueta


class DesktopMainWindow(QWidget):
    def __init__(
        self,
        registro_publico_url: str,
        dispositivo_identificador: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._registro_publico_url = registro_publico_url
        self._dispositivo_identificador = dispositivo_identificador

        self.setWindowTitle("Familia Puess · Control de asistencia")
        self.setMinimumSize(1180, 700)
        self.setStyleSheet(f"background: {CREMA};")

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        raiz.addWidget(self._construir_cabecera())
        raiz.addWidget(self._construir_cuerpo(), 1)
        raiz.addWidget(self._construir_pie())

        # El reloj del pie avanza solo, sin depender de la red.
        self._reloj = QTimer(self)
        self._reloj.timeout.connect(self._actualizar_reloj)
        self._reloj.start(1000)
        self._actualizar_reloj()

        self.set_connection_status(False)

    # ------------------------------------------------------- Cabecera ----

    def _construir_cabecera(self) -> QWidget:
        barra = QWidget()
        barra.setFixedHeight(74)
        barra.setStyleSheet(f"background: {CAFE_OSCURO};")

        fila = QHBoxLayout(barra)
        fila.setContentsMargins(26, 0, 22, 0)
        fila.setSpacing(18)

        logo = QLabel()
        logo.setPixmap(
            QPixmap(str(image_path("marca.png"))).scaledToHeight(
                40, Qt.TransformationMode.SmoothTransformation
            )
        )
        fila.addWidget(logo)

        fila.addWidget(
            _etiqueta(
                "SISTEMA DE CONTROL DE ASISTENCIA",
                f"color: {BLANCO}; font-size: 15px; font-weight: 600;"
                " letter-spacing: 1px; background: transparent;",
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            )
        )
        fila.addStretch(1)
        fila.addWidget(self._construir_insignia_sede())
        return barra

    def _construir_insignia_sede(self) -> QWidget:
        insignia = QFrame()
        insignia.setStyleSheet(
            f"background: {CAFE}; border: 1px solid {AMARILLO}; border-radius: 12px;"
        )

        fila = QHBoxLayout(insignia)
        fila.setContentsMargins(12, 7, 16, 7)
        fila.setSpacing(9)

        icono = _svg("point.svg", AMARILLO, 18)
        icono.setStyleSheet("background: transparent; border: none;")
        fila.addWidget(icono)

        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(0)
        textos.addWidget(
            _etiqueta(
                "Sede principal",
                f"color: {AMARILLO}; font-size: 12px; font-weight: 600;"
                " background: transparent; border: none;",
            )
        )
        # El identificador no se muestra completo: es un dato sensible.
        textos.addWidget(
            _etiqueta(
                "Dispositivo: " + "•" * 8,
                f"color: {TEXTO_TENUE}; font-size: 11px;"
                " background: transparent; border: none;",
            )
        )
        fila.addLayout(textos)
        return insignia

    # ---------------------------------------------------------- Cuerpo ---

    def _construir_cuerpo(self) -> QWidget:
        cuerpo = QWidget()
        cuerpo.setStyleSheet(f"background: {CREMA};")

        fila = QHBoxLayout(cuerpo)
        fila.setContentsMargins(28, 26, 28, 26)
        fila.setSpacing(26)

        fila.addWidget(self._construir_mazorca(), 0, Qt.AlignmentFlag.AlignVCenter)
        fila.addWidget(self._construir_bienvenida(), 1)
        fila.addWidget(self._construir_tarjeta_qr(), 0, Qt.AlignmentFlag.AlignVCenter)
        fila.addWidget(self._construir_mazorca(), 0, Qt.AlignmentFlag.AlignVCenter)
        return cuerpo

    def _construir_mazorca(self) -> QLabel:
        """Decoración lateral de marca."""
        mazorca = QLabel()
        imagen = QPixmap(str(image_path("mazorca1.png"))).scaledToWidth(
            96, Qt.TransformationMode.SmoothTransformation
        )
        mazorca.setPixmap(imagen)
        mazorca.setFixedWidth(imagen.width())
        mazorca.setStyleSheet("background: transparent;")
        return mazorca

    def _construir_bienvenida(self) -> QWidget:
        columna = QWidget()
        columna.setMinimumWidth(400)
        columna.setStyleSheet("background: transparent;")

        caja = QVBoxLayout(columna)
        caja.setContentsMargins(0, 0, 0, 0)
        caja.setSpacing(14)
        caja.addStretch(1)

        centrado = Qt.AlignmentFlag.AlignHCenter

        caja.addWidget(
            _etiqueta(
                "¡Hola!",
                f"color: {CAFE_OSCURO}; font-size: 52px; font-weight: 700;"
                " background: transparent;",
                centrado,
            )
        )
        caja.addWidget(
            _etiqueta(
                "Marca tu asistencia\nEscanea el QR o ingresa el código",
                f"color: {CAFE}; font-size: 14px; font-weight: 500;"
                " background: transparent;",
                centrado,
            )
        )

        logos = QLabel()
        logos.setPixmap(
            QPixmap(str(image_path("logos.png"))).scaledToWidth(
                300, Qt.TransformationMode.SmoothTransformation
            )
        )
        logos.setAlignment(centrado)
        logos.setStyleSheet("background: transparent;")
        caja.addWidget(logos)

        caja.addWidget(
            _etiqueta(
                "Código de validación",
                f"color: {CAFE_OSCURO}; font-size: 14px; font-weight: 700;"
                " background: transparent;",
                centrado,
            )
        )

        self._codigo_label = QLabel("--------")
        self._codigo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._codigo_label.setMinimumWidth(330)
        self._codigo_label.setStyleSheet(
            f"background: {CREMA_CAJA}; color: {CAFE_OSCURO}; border-radius: 14px;"
            " font-size: 34px; font-weight: 700; letter-spacing: 4px; padding: 16px 26px;"
        )
        caja.addWidget(self._codigo_label)
        caja.addStretch(1)
        return columna

    def _construir_tarjeta_qr(self) -> QWidget:
        tarjeta = QFrame()
        tarjeta.setFixedWidth(310)
        tarjeta.setStyleSheet(
            f"background: {CREMA}; border: 2px solid {ROSA_SUAVE}; border-radius: 22px;"
        )

        caja = QVBoxLayout(tarjeta)
        caja.setContentsMargins(24, 22, 24, 22)
        caja.setSpacing(18)

        caja.addWidget(self._construir_pastilla_tiempo(), 0, Qt.AlignmentFlag.AlignHCenter)

        self._qr_label = QLabel()
        self._qr_label.setFixedSize(TAMANO_QR, TAMANO_QR)
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setStyleSheet(
            f"background: {BLANCO}; border: none; border-radius: 10px;"
        )
        caja.addWidget(self._qr_label, 0, Qt.AlignmentFlag.AlignHCenter)

        aviso = _etiqueta(
            "Código único y seguro\nNo compartas este código",
            f"background: {CREMA_CAJA}; color: {CAFE}; border: none; border-radius: 12px;"
            " font-size: 12px; font-weight: 600; padding: 10px 18px;",
            Qt.AlignmentFlag.AlignCenter,
        )
        caja.addWidget(aviso)
        return tarjeta

    def _construir_pastilla_tiempo(self) -> QWidget:
        pastilla = QFrame()
        pastilla.setStyleSheet(f"background: {ROSA}; border: none; border-radius: 15px;")

        fila = QHBoxLayout(pastilla)
        fila.setContentsMargins(16, 7, 20, 7)
        fila.setSpacing(10)

        icono = _svg("time.svg", BLANCO, 18)
        icono.setStyleSheet("background: transparent; border: none;")
        fila.addWidget(icono)

        self._timer_label = QLabel()
        self._timer_label.setTextFormat(Qt.TextFormat.RichText)
        self._timer_label.setStyleSheet(
            f"color: {BLANCO}; background: transparent; border: none;"
            " font-size: 12px; font-weight: 700; letter-spacing: 1px;"
        )
        self._fijar_texto_temporizador(0)
        fila.addWidget(self._timer_label)
        return pastilla

    # ------------------------------------------------------------- Pie ---

    def _construir_pie(self) -> QWidget:
        barra = QWidget()
        barra.setFixedHeight(62)
        barra.setStyleSheet(f"background: {CAFE_OSCURO};")

        fila = QHBoxLayout(barra)
        fila.setContentsMargins(26, 0, 26, 0)
        fila.setSpacing(12)

        icono_reloj = _svg("time.svg", TEXTO_TENUE, 20)
        icono_reloj.setStyleSheet("background: transparent;")
        fila.addWidget(icono_reloj, 0, Qt.AlignmentFlag.AlignVCenter)

        self._fecha_label = _etiqueta(
            "",
            f"color: {BLANCO}; font-size: 13px; font-weight: 500; background: transparent;",
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        fila.addWidget(self._fecha_label)
        fila.addStretch(1)

        self._wifi_icon = _svg("wifi.svg", "#4CC38A", 20)
        self._wifi_icon.setStyleSheet("background: transparent;")
        fila.addWidget(self._wifi_icon, 0, Qt.AlignmentFlag.AlignVCenter)

        estado = QVBoxLayout()
        estado.setContentsMargins(0, 0, 0, 0)
        estado.setSpacing(0)

        self._connection_label = _etiqueta(
            "Sin conexión",
            f"color: {BLANCO}; font-size: 12px; font-weight: 600; background: transparent;",
        )
        estado.addWidget(self._connection_label)
        estado.addWidget(
            _etiqueta(
                "Version: 1.0.0",
                f"color: {TEXTO_TENUE}; font-size: 11px; background: transparent;",
            )
        )
        fila.addLayout(estado)
        return barra

    # ------------------------------------------------------ Interfaz ----

    def update_token(self, token: TokenRecibido) -> None:
        """Pinta a la vez el QR, el código alfanumérico y la validez restante."""
        self._qr_label.setPixmap(
            build_qr_pixmap(token.token, self._registro_publico_url, TAMANO_QR)
        )
        self._codigo_label.setText(token.codigo_alfa)
        self._fijar_texto_temporizador(self._segundos_de_validez(token))

    def set_connection_status(self, conectado: bool) -> None:
        """Refleja en el pie si el kiosco está hablando con la API."""
        self._connection_label.setText("Connected" if conectado else "Sin conexión")
        self._wifi_icon.setVisible(conectado)

    # ------------------------------------------------------- Internos ----

    @staticmethod
    def _segundos_de_validez(token: TokenRecibido) -> int:
        expira = token.expira_en
        generado = token.generado_en
        if expira.tzinfo is None:
            expira = expira.replace(tzinfo=timezone.utc)
        if generado.tzinfo is None:
            generado = generado.replace(tzinfo=timezone.utc)
        return max(0, round((expira - generado).total_seconds()))

    def _fijar_texto_temporizador(self, segundos: int) -> None:
        self._timer_label.setText(
            f"VALIDO POR<br><span style='color:{AMARILLO};'>{segundos} SEGUNDOS</span>"
        )

    def _actualizar_reloj(self) -> None:
        self._fecha_label.setText(format_datetime_es(datetime.now()))

"""Generación del código QR que escanea el trabajador."""

from __future__ import annotations

from io import BytesIO

import qrcode
from PIL import Image
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QPixmap

_COLOR_QR = "#3B1A0B"


def build_qr_content(token: str, registro_url: str) -> str:
    """
    Arma la URL que codifica el QR, respetando la cadena de consulta que ya
    traiga `registro_url`.
    """
    separador = "&" if "?" in registro_url else "?"
    return f"{registro_url}{separador}token={token}"


def build_qr_pixmap(token: str, registro_url: str, tamano: int = 300) -> QPixmap:
    """Devuelve el QR con fondo transparente listo para pintarse en un QLabel."""
    codigo = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    codigo.add_data(build_qr_content(token, registro_url))
    codigo.make(fit=True)

    imagen = codigo.make_image(fill_color=_COLOR_QR, back_color="white")
    rgba = imagen.convert("RGBA")
    datos = rgba.getdata()
    nuevos = []
    for r, g, b, a in datos:
        if r > 240 and g > 240 and b > 240:
            nuevos.append((r, g, b, 0))
        else:
            nuevos.append((r, g, b, a))
    rgba.putdata(nuevos)

    buffer = BytesIO()
    rgba.save(buffer, format="PNG")

    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(buffer.getvalue()), "PNG")
    return pixmap.scaled(tamano, tamano)

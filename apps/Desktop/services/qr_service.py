from io import BytesIO

import qrcode
from PySide6.QtGui import QPixmap


def build_qr_content(token: str, registro_publico_url: str) -> str:
    separator = "&" if "?" in registro_publico_url else "?"
    return f"{registro_publico_url}{separator}token={token}"


def build_qr_pixmap(token: str, registro_publico_url: str) -> QPixmap:
    content = build_qr_content(token, registro_publico_url)

    qr = qrcode.QRCode(border=2)
    qr.add_data(content)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    pixmap = QPixmap()
    pixmap.loadFromData(buffer.getvalue(), "PNG")
    return pixmap

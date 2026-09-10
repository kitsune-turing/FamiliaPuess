from PySide6.QtGui import QPixmap

from apps.Desktop.services.qr_service import build_qr_content, build_qr_pixmap


def test_build_qr_content_embeds_token_and_registro_url():
    content = build_qr_content("tok-abc123", "https://app.familiapuess.com/registro")

    assert content == "https://app.familiapuess.com/registro?token=tok-abc123"


def test_build_qr_content_appends_with_ampersand_when_url_has_query():
    content = build_qr_content("tok-xyz", "https://app.familiapuess.com/registro?sede=1")

    assert content == "https://app.familiapuess.com/registro?sede=1&token=tok-xyz"


def test_build_qr_pixmap_returns_non_empty_pixmap(qtbot):
    pixmap = build_qr_pixmap("tok-abc123", "https://app.familiapuess.com/registro")

    assert isinstance(pixmap, QPixmap)
    assert not pixmap.isNull()
    assert pixmap.width() > 0
    assert pixmap.height() > 0

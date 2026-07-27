from datetime import datetime, timedelta, timezone

from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QMainWindow, QMenuBar, QStackedWidget, QTabWidget

from apps.Desktop.api.token_client import TokenRecibido
from apps.Desktop.ui.main_window import DesktopMainWindow


def _make_window(qtbot) -> DesktopMainWindow:
    window = DesktopMainWindow(
        registro_publico_url="https://app.familiapuess.com/registro",
        dispositivo_identificador="KIOSK-001",
    )
    qtbot.addWidget(window)
    return window


def test_window_is_not_a_qmainwindow_so_it_can_never_have_menus_or_toolbars(qtbot):
    window = _make_window(qtbot)

    assert not isinstance(window, QMainWindow)


def test_window_has_no_navigation_widgets(qtbot):
    window = _make_window(qtbot)

    assert window.findChildren(QTabWidget) == []
    assert window.findChildren(QStackedWidget) == []
    assert window.findChildren(QMenuBar) == []


def test_update_token_sets_qr_pixmap_codigo_and_timer_together(qtbot):
    window = _make_window(qtbot)
    now = datetime.now(timezone.utc)
    token = TokenRecibido(
        token="tok-abc",
        codigo_alfa="A1B2C3",
        generado_en=now,
        expira_en=now + timedelta(seconds=30),
    )

    window.update_token(token)

    assert window._codigo_label.text() == "A1B2C3"
    assert not window._qr_label.pixmap().isNull()
    assert "30 SEGUNDOS" in window._timer_label.text()


def test_update_token_replaces_previous_values_completely(qtbot):
    window = _make_window(qtbot)
    now = datetime.now(timezone.utc)
    first = TokenRecibido(
        token="tok-1", codigo_alfa="AAAAAA", generado_en=now, expira_en=now + timedelta(seconds=30)
    )
    second = TokenRecibido(
        token="tok-2", codigo_alfa="BBBBBB", generado_en=now, expira_en=now + timedelta(seconds=30)
    )

    window.update_token(first)
    window.update_token(second)

    assert window._codigo_label.text() == "BBBBBB"


def test_set_connection_status_updates_label_text(qtbot):
    window = _make_window(qtbot)

    window.set_connection_status(True)
    assert window._connection_label.text() == "Connected"

    window.set_connection_status(False)
    assert window._connection_label.text() == "Sin conexión"


def test_set_connection_status_toggles_wifi_icon_visibility(qtbot):
    # isHidden() reflects the widget's own explicit visibility flag, unlike
    # isVisible(), which also requires the whole ancestor chain to be shown.
    window = _make_window(qtbot)

    window.set_connection_status(True)
    assert not window._wifi_icon.isHidden()

    window.set_connection_status(False)
    assert window._wifi_icon.isHidden()


def test_window_uses_real_svg_icons_not_painted_placeholders(qtbot):
    window = _make_window(qtbot)

    # point.svg (badge) + time.svg (pill) + time.svg (footer) + wifi.svg (footer)
    assert len(window.findChildren(QSvgWidget)) >= 4

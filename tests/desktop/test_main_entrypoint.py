import inspect

from apps.Desktop import main as desktop_main


def test_main_does_not_launch_fullscreen():
    source = inspect.getsource(desktop_main.main)

    assert "showFullScreen" not in source
    assert "window.show()" in source


def test_main_registers_application_fonts_before_building_the_window():
    source = inspect.getsource(desktop_main.main)

    register_index = source.index("register_application_fonts()")
    window_index = source.index("DesktopMainWindow(")

    assert register_index < window_index

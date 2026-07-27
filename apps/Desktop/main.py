import sys

from PySide6.QtWidgets import QApplication

from apps.Desktop.api.token_client import TokenClient
from apps.Desktop.ui.main_window import DesktopMainWindow
from apps.Desktop.utils.config import get_desktop_settings
from apps.Desktop.utils.fonts import register_application_fonts
from apps.Desktop.workers.token_rotation_worker import TokenRotationWorker


def main() -> int:
    settings = get_desktop_settings()
    app = QApplication(sys.argv)
    register_application_fonts()

    window = DesktopMainWindow(
        registro_publico_url=settings.registro_publico_url,
        dispositivo_identificador=settings.dispositivo_identificador,
    )

    client = TokenClient(
        base_url=settings.api_base_url,
        dispositivo_identificador=settings.dispositivo_identificador,
    )
    worker = TokenRotationWorker(
        client=client,
        fallback_interval_seconds=settings.rotacion_fallback_segundos,
        parent=window,
    )
    worker.token_ready.connect(window.update_token)
    worker.token_ready.connect(lambda _token: window.set_connection_status(True))
    worker.token_error.connect(lambda _message: window.set_connection_status(False))

    window.show()
    worker.start()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

"""Punto de entrada del kiosco de asistencia."""

from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import QApplication

from apps.Desktop.api.token_client import TokenClient
from apps.Desktop.ui.main_window import DesktopMainWindow
from apps.Desktop.utils.fonts import register_application_fonts
from apps.Desktop.workers.token_rotation_worker import TokenRotationWorker

API_BASE_URL = os.getenv("DESKTOP_API_BASE_URL", "http://localhost:8000")
REGISTRO_PUBLICO_URL = os.getenv(
    "DESKTOP_REGISTRO_URL", "http://localhost:5173/registro"
)
DISPOSITIVO_IDENTIFICADOR = os.getenv("DESKTOP_DISPOSITIVO_ID", "KIOSK-001")


def main() -> int:
    app = QApplication(sys.argv)

    # Las fuentes deben quedar registradas antes de construir los widgets.
    register_application_fonts()

    window = DesktopMainWindow(
        registro_publico_url=REGISTRO_PUBLICO_URL,
        dispositivo_identificador=DISPOSITIVO_IDENTIFICADOR,
    )

    cliente = TokenClient(
        base_url=API_BASE_URL,
        dispositivo_identificador=DISPOSITIVO_IDENTIFICADOR,
    )
    worker = TokenRotationWorker(client=cliente)

    def _al_recibir(token) -> None:
        window.update_token(token)
        window.set_connection_status(True)

    def _al_fallar(_mensaje: str) -> None:
        window.set_connection_status(False)

    worker.token_ready.connect(_al_recibir)
    worker.token_error.connect(_al_fallar)

    window.show()
    worker.start()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

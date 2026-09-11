"""Punto de entrada del kiosco de asistencia."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

if getattr(sys, "frozen", False):
    _PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    _PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")

from apps.Desktop.api.token_client import (
    DeviceNotFoundError,
    TokenClient,
    TokenClientError,
)
from apps.Desktop.ui.main_window import DesktopMainWindow
from apps.Desktop.utils.config import get_api_key, get_device_id, save_api_key
from apps.Desktop.utils.fonts import register_application_fonts
from apps.Desktop.workers.token_rotation_worker import TokenRotationWorker

API_BASE_URL = os.getenv("DESKTOP_API_BASE_URL", "https://process-api.familiapues.com")
REGISTRO_PUBLICO_URL = os.getenv(
    "DESKTOP_REGISTRO_URL", "http://localhost:5173/registro"
)


def _ensure_registered(cliente: TokenClient) -> None:
    """Register the device if this is the first install (device not in API)."""
    try:
        cliente.consultar_estado()
    except DeviceNotFoundError:
        try:
            cliente.registrar()
        except TokenClientError:
            pass
    except TokenClientError:
        pass


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--set-api-key":
        key = sys.argv[2] if len(sys.argv) > 2 else input("API Key: ").strip()
        save_api_key(key)
        print("API key guardada en ~/.familia_puess/config.ini")
        return 0

    app = QApplication(sys.argv)
    register_application_fonts()

    dispositivo_id = get_device_id()
    api_key = get_api_key()

    window = DesktopMainWindow(
        registro_publico_url=REGISTRO_PUBLICO_URL,
        dispositivo_identificador=dispositivo_id,
    )

    cliente = TokenClient(
        base_url=API_BASE_URL,
        dispositivo_identificador=dispositivo_id,
        api_key=api_key,
    )

    _ensure_registered(cliente)

    worker = TokenRotationWorker(client=cliente)

    _sede_loaded = False

    def _al_recibir(token) -> None:
        nonlocal _sede_loaded
        window.update_token(token)
        window.set_connection_status(True)
        if not _sede_loaded:
            try:
                estado = cliente.consultar_estado()
                if estado.sede_nombre:
                    window.set_sede_nombre(estado.sede_nombre)
                _sede_loaded = True
            except Exception:
                pass

    def _al_fallar(_mensaje: str) -> None:
        window.set_connection_status(False)

    def _al_inactivo() -> None:
        window.show_inactive()

    def _al_necesitar_sede() -> None:
        window.show_inactive("Dispositivo activo pero sin sede asignada.")

    def _al_fuera_horario() -> None:
        window.show_inactive("Fuera del horario de registro.")

    worker.token_ready.connect(_al_recibir)
    worker.token_error.connect(_al_fallar)
    worker.device_inactive.connect(_al_inactivo)
    worker.device_needs_sede.connect(_al_necesitar_sede)
    worker.fuera_de_horario.connect(_al_fuera_horario)

    window.show()
    worker.start()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

"""Punto de entrada del kiosco de asistencia."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox

_LOG_DIR = Path.home() / ".familia_puess"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_LOG_DIR / "desktop.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("desktop")

if getattr(sys, "frozen", False):
    _PROJECT_ROOT = Path(sys.executable).resolve().parent
    # SSL certs for httpx inside PyInstaller bundle
    _cert_file = Path(sys._MEIPASS) / "certifi" / "cacert.pem"
    if _cert_file.is_file():
        os.environ.setdefault("SSL_CERT_FILE", str(_cert_file))
        logger.info("SSL cert: %s", _cert_file)
    else:
        logger.warning("SSL cert NOT found at %s", _cert_file)
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
    "DESKTOP_REGISTRO_PUBLICO_URL",
    os.getenv("DESKTOP_REGISTRO_URL", "https://imputar.familiapues.com/registro"),
)


def _ensure_registered(cliente: TokenClient) -> None:
    """Register the device if this is the first install (device not in API)."""
    try:
        estado = cliente.consultar_estado()
        logger.info("Dispositivo ya registrado: %s (activo=%s)", estado.identificador, estado.activo)
    except DeviceNotFoundError:
        logger.info("Dispositivo no encontrado, registrando...")
        try:
            estado = cliente.registrar()
            logger.info("Dispositivo registrado: id=%s", estado.id)
        except TokenClientError as e:
            logger.error("No se pudo registrar el dispositivo: %s", e)
    except TokenClientError as e:
        logger.error("Error consultando estado del dispositivo: %s", e)


def _prompt_api_key(app: QApplication) -> str:
    """Show a dialog asking the user for the API key."""
    key, ok = QInputDialog.getText(
        None,
        "Familia Puess — Configuración",
        "Ingrese la API Key para conectar con el servidor:",
    )
    if ok and key.strip():
        save_api_key(key.strip())
        return key.strip()
    return ""


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

    if not api_key:
        logger.warning("No hay API key configurada, solicitando al usuario...")
        api_key = _prompt_api_key(app)
        if not api_key:
            QMessageBox.critical(
                None,
                "Familia Puess",
                "Se requiere una API Key para conectar con el servidor.\n"
                "La aplicación se cerrará.",
            )
            return 1

    logger.info("API: %s", API_BASE_URL)
    logger.info("Registro URL: %s", REGISTRO_PUBLICO_URL)
    logger.info("Dispositivo: %s", dispositivo_id)
    logger.info("API key configurada: sí (len=%d)", len(api_key))

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

    def _al_fallar(mensaje: str) -> None:
        logger.warning("Token error: %s", mensaje)
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

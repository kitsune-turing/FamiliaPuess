"""Rotación automática del token de asistencia."""

from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import QObject, QTimer, Signal

from apps.Desktop.api.token_client import (
    AuthenticationError,
    DeviceInactiveError,
    DeviceNotFoundError,
    FueraDeHorarioError,
    TokenClientError,
    TokenRecibido,
)

INTERVALO_POR_DEFECTO_SEGUNDOS = 30
INTERVALO_POLLING_INACTIVO_SEGUNDOS = 15
INTERVALO_FUERA_HORARIO_SEGUNDOS = 300


class TokenRotationWorker(QObject):
    token_ready = Signal(object)
    token_error = Signal(str)
    device_inactive = Signal()
    device_needs_sede = Signal()
    fuera_de_horario = Signal()

    def __init__(
        self,
        client,
        fallback_interval_seconds: int = INTERVALO_POR_DEFECTO_SEGUNDOS,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._client = client
        self._fallback_interval_seconds = fallback_interval_seconds
        self._polling_inactive = False
        self._fuera_horario = False

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._rotar)

    def start(self) -> None:
        self._rotar()

    def stop(self) -> None:
        self._timer.stop()

    def _rotar(self) -> None:
        if self._polling_inactive:
            self._check_activation()
            return
        if self._fuera_horario:
            self._check_horario()
            return
        try:
            recibido = self._client.solicitar_token()
        except AuthenticationError:
            self.token_error.emit("API key inválida. Revise la variable DESKTOP_API_KEY.")
            self._programar(self._fallback_interval_seconds)
            return
        except DeviceNotFoundError:
            self.token_error.emit(
                "Dispositivo no registrado. Contacte al administrador."
            )
            self._polling_inactive = True
            self._programar(INTERVALO_POLLING_INACTIVO_SEGUNDOS)
            return
        except FueraDeHorarioError:
            self.fuera_de_horario.emit()
            self._fuera_horario = True
            self._programar(INTERVALO_FUERA_HORARIO_SEGUNDOS)
            return
        except DeviceInactiveError:
            self._check_inactive_reason()
            return
        except TokenClientError as error:
            self.token_error.emit(str(error))
            self._programar(self._fallback_interval_seconds)
            return

        self._fuera_horario = False
        self.token_ready.emit(recibido)
        self._programar(self._next_interval_seconds(recibido))

    def _check_horario(self) -> None:
        try:
            self._client.solicitar_token()
        except FueraDeHorarioError:
            self.fuera_de_horario.emit()
            self._programar(INTERVALO_FUERA_HORARIO_SEGUNDOS)
            return
        except TokenClientError:
            self._programar(INTERVALO_FUERA_HORARIO_SEGUNDOS)
            return
        self._fuera_horario = False
        self._rotar()

    def _check_inactive_reason(self) -> None:
        try:
            estado = self._client.consultar_estado()
        except TokenClientError:
            self.device_inactive.emit()
            self._polling_inactive = True
            self._programar(INTERVALO_POLLING_INACTIVO_SEGUNDOS)
            return
        if estado.activo:
            self._polling_inactive = False
            self._rotar()
            return
        if estado.id_sede is None:
            self.device_needs_sede.emit()
        else:
            self.device_inactive.emit()
        self._polling_inactive = True
        self._programar(INTERVALO_POLLING_INACTIVO_SEGUNDOS)

    def _check_activation(self) -> None:
        try:
            estado = self._client.consultar_estado()
        except TokenClientError:
            self._programar(INTERVALO_POLLING_INACTIVO_SEGUNDOS)
            return
        if estado.activo:
            self._polling_inactive = False
            self._rotar()
        else:
            self.device_inactive.emit()
            self._programar(INTERVALO_POLLING_INACTIVO_SEGUNDOS)

    def _next_interval_seconds(self, token: TokenRecibido) -> int:
        ahora = datetime.now(timezone.utc)
        expira = token.expira_en
        if expira.tzinfo is None:
            expira = expira.replace(tzinfo=timezone.utc)
        restantes = round((expira - ahora).total_seconds())
        if restantes <= 0:
            return self._fallback_interval_seconds
        return restantes

    def _programar(self, segundos: int) -> None:
        self._timer.start(max(1, segundos) * 1000)

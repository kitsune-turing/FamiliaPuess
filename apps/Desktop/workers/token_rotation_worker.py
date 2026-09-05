"""Rotación automática del token de asistencia."""

from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import QObject, QTimer, Signal

from apps.Desktop.api.token_client import TokenClientError, TokenRecibido

INTERVALO_POR_DEFECTO_SEGUNDOS = 30


class TokenRotationWorker(QObject):
    """
    Pide un token nuevo cada vez que el anterior caduca.

    El intervalo lo manda el servidor a través de `expira_en`, no el cliente,
    para que el kiosco nunca muestre un token ya vencido. Si el token llega
    caducado o la API falla, se recurre al intervalo de respaldo.
    """

    token_ready = Signal(object)
    token_error = Signal(str)

    def __init__(
        self,
        client,
        fallback_interval_seconds: int = INTERVALO_POR_DEFECTO_SEGUNDOS,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._client = client
        self._fallback_interval_seconds = fallback_interval_seconds

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._rotar)

    def start(self) -> None:
        """Pide el primer token y programa el siguiente."""
        self._rotar()

    def stop(self) -> None:
        self._timer.stop()

    def _rotar(self) -> None:
        try:
            recibido = self._client.solicitar_token()
        except TokenClientError as error:
            self.token_error.emit(str(error))
            self._programar(self._fallback_interval_seconds)
            return

        self.token_ready.emit(recibido)
        self._programar(self._next_interval_seconds(recibido))

    def _next_interval_seconds(self, token: TokenRecibido) -> int:
        """Segundos que faltan para que caduque el token, o el de respaldo."""
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

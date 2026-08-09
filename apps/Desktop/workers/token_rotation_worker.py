import logging

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal

from apps.Desktop.api.token_client import TokenClient, TokenClientError, TokenRecibido

logger = logging.getLogger(__name__)


class _FetchSignals(QObject):
    succeeded = Signal(object)
    failed = Signal(str)


class _FetchTokenRunnable(QRunnable):
    def __init__(self, client: TokenClient) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self._client = client
        self.signals = _FetchSignals()

    def run(self) -> None:
        try:
            token = self._client.solicitar_token()
        except TokenClientError as exc:
            logger.error("Token fetch failed: %s", exc)
            self.signals.failed.emit(str(exc))
            return
        except Exception as exc:
            logger.error("Unexpected error fetching token: %s", exc)
            self.signals.failed.emit(str(exc))
            return
        self.signals.succeeded.emit(token)


class TokenRotationWorker(QObject):

    token_ready = Signal(object)
    token_error = Signal(str)

    def __init__(
        self,
        client: TokenClient,
        fallback_interval_seconds: float,
        thread_pool: QThreadPool | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._client = client
        self._fallback_interval_seconds = fallback_interval_seconds
        self._thread_pool = thread_pool or QThreadPool.globalInstance()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._request_token)
        self._current_runnable: _FetchTokenRunnable | None = None

    def start(self) -> None:
        self._request_token()

    def stop(self) -> None:
        self._timer.stop()

    def _request_token(self) -> None:
        runnable = _FetchTokenRunnable(self._client)
        self._current_runnable = runnable
        runnable.signals.succeeded.connect(self._on_token_received)
        runnable.signals.failed.connect(self._on_token_failed)
        self._thread_pool.start(runnable)

    def _on_token_received(self, token: TokenRecibido) -> None:
        self._current_runnable = None
        self.token_ready.emit(token)
        self._timer.start(int(self._next_interval_seconds(token) * 1000))

    def _on_token_failed(self, message: str) -> None:
        self._current_runnable = None
        self.token_error.emit(message)
        self._timer.start(int(self._fallback_interval_seconds * 1000))

    def _next_interval_seconds(self, token: TokenRecibido) -> float:
        remaining = (token.expira_en - token.generado_en).total_seconds()
        return remaining if remaining > 0 else self._fallback_interval_seconds

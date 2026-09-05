"""Cliente HTTP para pedir tokens de asistencia a la API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import httpx

TIEMPO_ESPERA_SEGUNDOS = 10.0


class TokenClientError(RuntimeError):
    """La API no pudo entregar un token válido."""


@dataclass(frozen=True)
class TokenRecibido:
    """Token vigente devuelto por ``POST /desktop/tokens``."""

    token: str
    codigo_alfa: str
    generado_en: datetime
    expira_en: datetime


class TokenClient:
    def __init__(
        self,
        base_url: str,
        dispositivo_identificador: str,
        api_key: str = "",
        timeout: float = TIEMPO_ESPERA_SEGUNDOS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._dispositivo_identificador = dispositivo_identificador
        self._api_key = api_key
        self._timeout = timeout

    def solicitar_token(self) -> TokenRecibido:
        """
        Pide un token nuevo. Cualquier fallo de red o de servidor se traduce a
        `TokenClientError`, para que la ventana solo tenga que manejar un tipo
        de error y pueda mostrar el estado "Sin conexión".
        """
        headers: dict[str, str] = {}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key

        try:
            respuesta = httpx.post(
                f"{self._base_url}/desktop/tokens",
                json={"dispositivo_identificador": self._dispositivo_identificador},
                headers=headers,
                timeout=self._timeout,
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
        except httpx.HTTPError as error:
            raise TokenClientError(str(error)) from error

        try:
            return TokenRecibido(
                token=datos["token"],
                codigo_alfa=datos["codigo_alfa"],
                generado_en=datetime.fromisoformat(datos["generado_en"]),
                expira_en=datetime.fromisoformat(datos["expira_en"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise TokenClientError(f"Respuesta inesperada de la API: {error}") from error

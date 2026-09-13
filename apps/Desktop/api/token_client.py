"""Cliente HTTP para pedir tokens de asistencia a la API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import httpx

TIEMPO_ESPERA_SEGUNDOS = 10.0


class TokenClientError(RuntimeError):
    """La API no pudo entregar un token válido."""


class DeviceInactiveError(TokenClientError):
    """El dispositivo existe pero está inactivo o sin sede asignada."""


class AuthenticationError(TokenClientError):
    """La API rechazó la API key (401)."""


class DeviceNotFoundError(TokenClientError):
    """El dispositivo no está registrado en el sistema."""


class FueraDeHorarioError(TokenClientError):
    """El dispositivo está fuera del horario de registro."""


@dataclass(frozen=True)
class TokenRecibido:
    """Token vigente devuelto por ``POST /desktop/tokens``."""

    token: str
    codigo_alfa: str
    generado_en: datetime
    expira_en: datetime
    exigir_codigo: bool


@dataclass(frozen=True)
class DeviceStatus:
    """Estado del dispositivo devuelto por ``GET /desktop/status/{id}``."""

    id: int
    identificador: str
    id_sede: int | None
    sede_nombre: str | None
    id_estado: int
    activo: bool


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

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key
        return headers

    def registrar(self, descripcion: str | None = None) -> DeviceStatus:
        """Auto-registra el dispositivo como inactivo."""
        payload: dict = {"identificador": self._dispositivo_identificador}
        if descripcion:
            payload["descripcion"] = descripcion
        try:
            respuesta = httpx.post(
                f"{self._base_url}/desktop/register",
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
            )
            if respuesta.status_code == 401:
                raise AuthenticationError("API key inválida o ausente")
            respuesta.raise_for_status()
            datos = respuesta.json()
        except AuthenticationError:
            raise
        except httpx.HTTPError as error:
            raise TokenClientError(str(error)) from error
        return DeviceStatus(
            id=datos["id"],
            identificador=datos["identificador"],
            id_sede=datos.get("id_sede"),
            sede_nombre=datos.get("sede_nombre"),
            id_estado=datos["id_estado"],
            activo=False,
        )

    def consultar_estado(self) -> DeviceStatus:
        """Consulta el estado actual del dispositivo."""
        try:
            respuesta = httpx.get(
                f"{self._base_url}/desktop/status/{self._dispositivo_identificador}",
                headers=self._headers(),
                timeout=self._timeout,
            )
            if respuesta.status_code == 401:
                raise AuthenticationError("API key inválida o ausente")
            if respuesta.status_code == 404:
                raise DeviceNotFoundError(self._dispositivo_identificador)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except (AuthenticationError, DeviceNotFoundError):
            raise
        except httpx.HTTPError as error:
            raise TokenClientError(str(error)) from error
        return DeviceStatus(
            id=datos["id"],
            identificador=datos["identificador"],
            id_sede=datos.get("id_sede"),
            sede_nombre=datos.get("sede_nombre"),
            id_estado=datos["id_estado"],
            activo=datos.get("activo", False),
        )

    def solicitar_token(self) -> TokenRecibido:
        """Pide un token nuevo."""
        try:
            respuesta = httpx.post(
                f"{self._base_url}/desktop/tokens",
                json={"dispositivo_identificador": self._dispositivo_identificador},
                headers=self._headers(),
                timeout=self._timeout,
            )
            if respuesta.status_code == 401:
                raise AuthenticationError("API key inválida o ausente")
            if respuesta.status_code == 404:
                raise DeviceNotFoundError(self._dispositivo_identificador)
            if respuesta.status_code == 403:
                detail = ""
                try:
                    detail = respuesta.json().get("detail", "")
                except Exception:
                    pass
                if "horario" in detail.lower():
                    raise FueraDeHorarioError(self._dispositivo_identificador)
                raise DeviceInactiveError(self._dispositivo_identificador)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except (AuthenticationError, DeviceNotFoundError, DeviceInactiveError, FueraDeHorarioError):
            raise
        except httpx.HTTPError as error:
            raise TokenClientError(str(error)) from error

        try:
            return TokenRecibido(
                token=datos["token"],
                codigo_alfa=datos["codigo_alfa"],
                generado_en=datetime.fromisoformat(datos["generado_en"]),
                expira_en=datetime.fromisoformat(datos["expira_en"]),
                exigir_codigo=datos.get("exigir_codigo", True),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise TokenClientError(f"Respuesta inesperada de la API: {error}") from error

    def check_token_used(self, token_value: str) -> bool:
        """Returns True if the token has been consumed by a registration."""
        try:
            respuesta = httpx.get(
                f"{self._base_url}/desktop/tokens/{token_value}/used",
                headers=self._headers(),
                timeout=self._timeout,
            )
            if respuesta.status_code == 200:
                return respuesta.json().get("used", False)
        except httpx.HTTPError:
            pass
        return False

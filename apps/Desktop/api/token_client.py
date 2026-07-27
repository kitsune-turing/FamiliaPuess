from dataclasses import dataclass
from datetime import datetime

import httpx


class TokenClientError(Exception):
    pass


@dataclass(frozen=True)
class TokenRecibido:
    token: str
    codigo_alfa: str
    generado_en: datetime
    expira_en: datetime


class TokenClient:
    def __init__(self, base_url: str, dispositivo_identificador: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._dispositivo_identificador = dispositivo_identificador
        self._timeout = timeout

    def solicitar_token(self) -> TokenRecibido:
        try:
            response = httpx.post(
                f"{self._base_url}/desktop/tokens",
                json={"dispositivo_identificador": self._dispositivo_identificador},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise TokenClientError(str(exc)) from exc

        payload = response.json()
        return TokenRecibido(
            token=payload["token"],
            codigo_alfa=payload["codigo_alfa"],
            generado_en=datetime.fromisoformat(payload["generado_en"]),
            expira_en=datetime.fromisoformat(payload["expira_en"]),
        )

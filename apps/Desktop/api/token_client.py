import logging
from dataclasses import dataclass
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class TokenClientError(Exception):
    pass


class AuthenticationError(TokenClientError):
    pass


@dataclass(frozen=True)
class TokenRecibido:
    token: str
    codigo_alfa: str
    generado_en: datetime
    expira_en: datetime


class TokenClient:
    def __init__(
        self,
        base_url: str,
        dispositivo_identificador: str,
        username: str,
        password: str,
        timeout: float = 5.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._dispositivo_identificador = dispositivo_identificador
        self._username = username
        self._password = password
        self._timeout = timeout
        self._access_token: str | None = None
        self._refresh_token: str | None = None

    def _login(self) -> None:
        try:
            response = httpx.post(
                f"{self._base_url}/auth/login",
                json={"username": self._username, "password": self._password},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AuthenticationError(f"Login failed: {exc}") from exc

        data = response.json()
        self._access_token = data["access_token"]
        self._refresh_token = data.get("refresh_token")
        logger.info("Desktop authenticated successfully")

    def _refresh(self) -> bool:
        if not self._refresh_token:
            return False
        try:
            response = httpx.post(
                f"{self._base_url}/auth/refresh",
                json={"refresh_token": self._refresh_token},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            logger.warning("Token refresh failed, will re-login")
            return False

        data = response.json()
        self._access_token = data["access_token"]
        self._refresh_token = data.get("refresh_token", self._refresh_token)
        return True

    def _auth_headers(self) -> dict[str, str]:
        if not self._access_token:
            self._login()
        return {"Authorization": f"Bearer {self._access_token}"}

    def solicitar_token(self) -> TokenRecibido:
        for attempt in range(2):
            try:
                response = httpx.post(
                    f"{self._base_url}/desktop/tokens",
                    json={"dispositivo_identificador": self._dispositivo_identificador},
                    headers=self._auth_headers(),
                    timeout=self._timeout,
                )
                if response.status_code == 401 and attempt == 0:
                    if not self._refresh():
                        self._login()
                    continue
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

        raise TokenClientError("Failed to obtain token after re-authentication")

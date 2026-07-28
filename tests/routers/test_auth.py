from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.main import app
from apps.API.services.auth_service import LoginResult, PermisoInfo, RefreshResult
from shared.exceptions.auth import (
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    RefreshTokenInvalidoError,
    SesionNoEncontradaError,
    TokenInvalidoError,
    UsuarioInactivoError,
)


async def _fake_session():
    yield object()


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = _fake_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _login_result() -> LoginResult:
    return LoginResult(
        access_token="access.jwt.token",
        refresh_token="refresh.jwt.token",
        token_type="bearer",
        usuario_id=10,
        nombre="Admin",
        username="admin",
        rol_codigo="SUPER_ADMIN",
        rol_nombre="Super Usuario",
        debe_cambiar_pw=False,
        permisos=[
            PermisoInfo(
                modulo_codigo="DASHBOARD",
                modulo_nombre="Dashboard",
                puede_leer=True,
                puede_escribir=False,
                puede_eliminar=False,
                puede_administrar=False,
            ),
        ],
    )


# ── POST /auth/login ──


def test_login_returns_200_with_tokens(client):
    with patch(
        "apps.API.routers.auth.auth_service.login",
        new=AsyncMock(return_value=_login_result()),
    ):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "secret"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access.jwt.token"
    assert body["refresh_token"] == "refresh.jwt.token"
    assert body["token_type"] == "bearer"
    assert body["usuario_id"] == 10
    assert body["rol_codigo"] == "SUPER_ADMIN"
    assert len(body["permisos"]) == 1
    assert body["permisos"][0]["modulo_codigo"] == "DASHBOARD"


def test_login_returns_401_on_invalid_credentials(client):
    with patch(
        "apps.API.routers.auth.auth_service.login",
        new=AsyncMock(side_effect=CredencialesInvalidasError()),
    ):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrong"},
        )

    assert response.status_code == 401


def test_login_returns_403_on_inactive_user(client):
    with patch(
        "apps.API.routers.auth.auth_service.login",
        new=AsyncMock(side_effect=UsuarioInactivoError()),
    ):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "secret"},
        )

    assert response.status_code == 403


def test_login_returns_429_on_lockout(client):
    with patch(
        "apps.API.routers.auth.auth_service.login",
        new=AsyncMock(side_effect=CuentaBloqueadaError(15)),
    ):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "any"},
        )

    assert response.status_code == 429


def test_login_returns_422_on_missing_fields(client):
    response = client.post("/auth/login", json={})

    assert response.status_code == 422


# ── POST /auth/refresh ──


def test_refresh_returns_200(client):
    with patch(
        "apps.API.routers.auth.auth_service.refresh",
        new=AsyncMock(
            return_value=RefreshResult(
                access_token="new.access",
                refresh_token="new.refresh",
                token_type="bearer",
            )
        ),
    ):
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "old.refresh"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "new.access"


def test_refresh_returns_401_on_invalid_refresh(client):
    with patch(
        "apps.API.routers.auth.auth_service.refresh",
        new=AsyncMock(side_effect=RefreshTokenInvalidoError()),
    ):
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "bad.token"},
        )

    assert response.status_code == 401


# ── POST /auth/logout ──


def test_logout_returns_204(client):
    with (
        patch(
            "apps.API.routers.auth.auth_service.validate_token",
            new=AsyncMock(return_value={"sub": "10", "type": "access"}),
        ),
        patch(
            "apps.API.routers.auth.auth_service.logout",
            new=AsyncMock(),
        ),
    ):
        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer valid.jwt.token"},
        )

    assert response.status_code == 204


def test_logout_returns_401_without_token(client):
    response = client.post("/auth/logout")

    assert response.status_code == 403


def test_logout_returns_404_on_session_not_found(client):
    with (
        patch(
            "apps.API.routers.auth.auth_service.validate_token",
            new=AsyncMock(return_value={"sub": "10", "type": "access"}),
        ),
        patch(
            "apps.API.routers.auth.auth_service.logout",
            new=AsyncMock(side_effect=SesionNoEncontradaError()),
        ),
    ):
        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer valid.jwt.token"},
        )

    assert response.status_code == 404


# ── GET /auth/me ──


def test_me_returns_401_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 403

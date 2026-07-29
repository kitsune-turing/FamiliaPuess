from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.horarios import (
    HorarioInmutableError,
    HorarioNoEncontradoError,
    HorarioSolapamientoError,
    HorarioToleranciaInvalidaError,
    HorarioVigenciaInvalidaError,
)
from shared.exceptions.sedes import SedeInactivaError, SedeNoEncontradaError

FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeSede:
    id: int = 1
    nombre: str = "Sede Central"


@dataclass
class _FakeHorario:
    id: int = 10
    id_sede: int = 1
    nombre: str | None = "Horario Principal"
    hora_entrada: time = field(default_factory=lambda: time(8, 0))
    hora_salida: time | None = None
    tolerancia_min: int = 15
    vigente_desde: date = field(default_factory=lambda: date(2026, 1, 1))
    vigente_hasta: date | None = None
    created_at: datetime = field(default_factory=lambda: FIXED_NOW)
    sede: _FakeSede = field(default_factory=_FakeSede)


@dataclass
class _FakeAuthUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "HORARIOS"


@dataclass
class _FakePermiso:
    modulo: _FakeModulo = None
    puede_leer: bool = True
    puede_escribir: bool = True
    puede_eliminar: bool = True
    puede_administrar: bool = True

    def __post_init__(self):
        if self.modulo is None:
            self.modulo = _FakeModulo()


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides[get_current_user] = _fake_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _permission_patches():
    return (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeAuthUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
    )


_HEADERS = {"Authorization": "Bearer valid.jwt"}


# ── GET /horarios ──


def test_list_horarios_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.list_horarios",
            new=AsyncMock(return_value=[_FakeHorario()]),
        ),
    ):
        response = client.get("/horarios", headers=_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["sede_nombre"] == "Sede Central"
    assert body["items"][0]["hora_entrada"] == "08:00:00"
    assert body["items"][0]["tolerancia_min"] == 15


def test_list_horarios_with_sede_filter(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.list_horarios",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get("/horarios?id_sede=1", headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_list_horarios_solo_vigentes(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.list_horarios",
            new=AsyncMock(return_value=[_FakeHorario()]),
        ),
    ):
        response = client.get("/horarios?solo_vigentes=true", headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["total"] == 1


# ── GET /horarios/{id} ──


def test_get_horario_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.get_horario",
            new=AsyncMock(return_value=_FakeHorario()),
        ),
    ):
        response = client.get("/horarios/10", headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["id"] == 10


def test_get_horario_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.get_horario",
            new=AsyncMock(side_effect=HorarioNoEncontradoError(999)),
        ),
    ):
        response = client.get("/horarios/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /horarios ──


def test_create_horario_returns_201(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.create_horario",
            new=AsyncMock(return_value=_FakeHorario()),
        ),
    ):
        response = client.post(
            "/horarios",
            headers=_HEADERS,
            json={
                "id_sede": 1,
                "hora_entrada": "08:00:00",
                "tolerancia_min": 15,
                "vigente_desde": "2026-08-01",
            },
        )

    assert response.status_code == 201
    assert response.json()["id"] == 10


def test_create_horario_sede_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.create_horario",
            new=AsyncMock(side_effect=SedeNoEncontradaError(999)),
        ),
    ):
        response = client.post(
            "/horarios",
            headers=_HEADERS,
            json={
                "id_sede": 999,
                "hora_entrada": "08:00:00",
                "vigente_desde": "2026-08-01",
            },
        )

    assert response.status_code == 404


def test_create_horario_sede_inactive(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.create_horario",
            new=AsyncMock(side_effect=SedeInactivaError(1)),
        ),
    ):
        response = client.post(
            "/horarios",
            headers=_HEADERS,
            json={
                "id_sede": 1,
                "hora_entrada": "08:00:00",
                "vigente_desde": "2026-08-01",
            },
        )

    assert response.status_code == 422


def test_create_horario_solapamiento(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.create_horario",
            new=AsyncMock(side_effect=HorarioSolapamientoError(1)),
        ),
    ):
        response = client.post(
            "/horarios",
            headers=_HEADERS,
            json={
                "id_sede": 1,
                "hora_entrada": "08:00:00",
                "vigente_desde": "2026-08-01",
            },
        )

    assert response.status_code == 409


def test_create_horario_invalid_tolerancia(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.create_horario",
            new=AsyncMock(side_effect=HorarioToleranciaInvalidaError()),
        ),
    ):
        response = client.post(
            "/horarios",
            headers=_HEADERS,
            json={
                "id_sede": 1,
                "hora_entrada": "08:00:00",
                "tolerancia_min": 150,
                "vigente_desde": "2026-08-01",
            },
        )

    assert response.status_code == 422


def test_create_horario_invalid_vigencia(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.create_horario",
            new=AsyncMock(side_effect=HorarioVigenciaInvalidaError()),
        ),
    ):
        response = client.post(
            "/horarios",
            headers=_HEADERS,
            json={
                "id_sede": 1,
                "hora_entrada": "08:00:00",
                "vigente_desde": "2026-08-01",
                "vigente_hasta": "2026-07-01",
            },
        )

    assert response.status_code == 422


# ── PUT /horarios/{id} ──


def test_update_horario_returns_200(client):
    p_user, p_permisos = _permission_patches()
    updated = _FakeHorario(nombre="Actualizado", tolerancia_min=30)

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.update_horario",
            new=AsyncMock(return_value=updated),
        ),
    ):
        response = client.put(
            "/horarios/10",
            headers=_HEADERS,
            json={"nombre": "Actualizado", "tolerancia_min": 30},
        )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Actualizado"
    assert response.json()["tolerancia_min"] == 30


def test_update_horario_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.update_horario",
            new=AsyncMock(side_effect=HorarioNoEncontradoError(999)),
        ),
    ):
        response = client.put(
            "/horarios/999",
            headers=_HEADERS,
            json={"nombre": "X"},
        )

    assert response.status_code == 404


def test_update_horario_inmutable(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.update_horario",
            new=AsyncMock(side_effect=HorarioInmutableError(1)),
        ),
    ):
        response = client.put(
            "/horarios/1",
            headers=_HEADERS,
            json={"nombre": "X"},
        )

    assert response.status_code == 409


# ── DELETE /horarios/{id} ──


def test_finalizar_horario_returns_204(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.finalizar_horario",
            new=AsyncMock(),
        ),
    ):
        response = client.delete("/horarios/10", headers=_HEADERS)

    assert response.status_code == 204


def test_finalizar_horario_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.finalizar_horario",
            new=AsyncMock(side_effect=HorarioNoEncontradoError(999)),
        ),
    ):
        response = client.delete("/horarios/999", headers=_HEADERS)

    assert response.status_code == 404


def test_finalizar_horario_inmutable(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.horarios.horarios_service.finalizar_horario",
            new=AsyncMock(side_effect=HorarioInmutableError(1)),
        ),
    ):
        response = client.delete("/horarios/1", headers=_HEADERS)

    assert response.status_code == 409


# ── Authorization ──


def test_horarios_returns_403_without_token():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        response = c.get("/horarios")
    app.dependency_overrides.clear()
    assert response.status_code == 403

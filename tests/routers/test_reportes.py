from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.reportes import (
    RangoFechasInvalidoError,
    ReporteDuplicadoError,
    ReporteNoEncontradoError,
    ReporteSinDatosError,
)

FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeEmpleado:
    id: int = 1
    nombre: str = "Juan"
    apellido: str = "Perez"
    documento: str = "1234567890"


@dataclass
class _FakeSede:
    id: int = 1
    nombre: str = "Sede Central"


@dataclass
class _FakeTipoRegistro:
    id: int = 1
    codigo: str = "ENTRADA"
    nombre: str = "Entrada"


@dataclass
class _FakeCatNovedad:
    id: int = 1
    codigo: str = "TARDANZA"
    nombre: str = "Tardanza"
    color: str | None = "#FF0000"
    icono: str | None = "clock-alert"


@dataclass
class _FakeNovedad:
    id: int = 1
    id_asistencia: int = 100
    tipo_novedad: _FakeCatNovedad = field(default_factory=_FakeCatNovedad)


@dataclass
class _FakeAsistencia:
    id: int = 100
    id_empleado: int = 1
    id_sede: int = 1
    id_tipo_registro: int = 1
    fecha_registro: date = field(default_factory=lambda: date(2026, 7, 28))
    registrado_en: datetime = field(default_factory=lambda: FIXED_NOW)
    empleado: _FakeEmpleado = field(default_factory=_FakeEmpleado)
    sede: _FakeSede = field(default_factory=_FakeSede)
    tipo_registro: _FakeTipoRegistro = field(default_factory=_FakeTipoRegistro)


@dataclass
class _FakeReporte:
    id: int = 1
    fecha_inicio: date = field(default_factory=lambda: date(2026, 7, 20))
    fecha_fin: date = field(default_factory=lambda: date(2026, 7, 26))
    total_registros: int = 50
    total_novedades: int = 3
    created_at: datetime = field(default_factory=lambda: FIXED_NOW)


@dataclass
class _FakeAuthUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "REPORTES"


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


# --- GET /reportes/asistencia ---


async def test_consultar_asistencia_returns_200(client):
    asistencias = [_FakeAsistencia(id=100)]
    novedades = {100: _FakeNovedad(id_asistencia=100)}
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.consultar_asistencia",
            new=AsyncMock(return_value=(asistencias, novedades)),
        ),
    ):
        resp = client.get("/reportes/asistencia", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["empleado_nombre"] == "Juan Perez"
    assert item["novedad_tipo"] == "TARDANZA"
    assert item["novedad_color"] == "#FF0000"


async def test_consultar_asistencia_with_filters(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.consultar_asistencia",
            new=AsyncMock(return_value=([], {})),
        ),
    ):
        resp = client.get(
            "/reportes/asistencia?id_empleado=1&id_sede=2&fecha_desde=2026-07-01&fecha_hasta=2026-07-31",
            headers=_HEADERS,
        )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


async def test_consultar_asistencia_invalid_range(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.consultar_asistencia",
            new=AsyncMock(side_effect=RangoFechasInvalidoError()),
        ),
    ):
        resp = client.get(
            "/reportes/asistencia?fecha_desde=2026-07-31&fecha_hasta=2026-07-01",
            headers=_HEADERS,
        )
    assert resp.status_code == 422


async def test_consultar_asistencia_without_novedad(client):
    asistencias = [_FakeAsistencia(id=200)]
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.consultar_asistencia",
            new=AsyncMock(return_value=(asistencias, {})),
        ),
    ):
        resp = client.get("/reportes/asistencia", headers=_HEADERS)
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["novedad_tipo"] is None
    assert item["novedad_color"] is None


# --- GET /reportes/asistencia/excel ---


async def test_descargar_excel_returns_xlsx(client):
    asistencias = [_FakeAsistencia(id=100)]
    novedades = {}
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.consultar_asistencia",
            new=AsyncMock(return_value=(asistencias, novedades)),
        ),
        patch(
            "apps.API.routers.reportes.reportes_service.generar_excel",
            return_value=b"PK\x03\x04fake-xlsx",
        ),
        patch(
            "apps.API.routers.reportes.reportes_service.generar_nombre_archivo",
            return_value="reporte_asistencia_2026-07-28.xlsx",
        ),
    ):
        resp = client.get("/reportes/asistencia/excel", headers=_HEADERS)
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]
    assert "reporte_asistencia" in resp.headers["content-disposition"]


async def test_descargar_excel_sin_datos(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.consultar_asistencia",
            new=AsyncMock(return_value=([], {})),
        ),
        patch(
            "apps.API.routers.reportes.reportes_service.generar_excel",
            side_effect=ReporteSinDatosError(),
        ),
    ):
        resp = client.get("/reportes/asistencia/excel", headers=_HEADERS)
    assert resp.status_code == 404


# --- GET /reportes/semanales ---


async def test_list_reportes_semanales_returns_200(client):
    reportes = [_FakeReporte(id=1), _FakeReporte(id=2)]
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.list_reportes_semanales",
            new=AsyncMock(return_value=reportes),
        ),
    ):
        resp = client.get("/reportes/semanales", headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


# --- GET /reportes/semanales/{id} ---


async def test_get_reporte_semanal_returns_200(client):
    reporte = _FakeReporte()
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.get_reporte_semanal",
            new=AsyncMock(return_value=reporte),
        ),
    ):
        resp = client.get("/reportes/semanales/1", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
    assert body["total_registros"] == 50


async def test_get_reporte_semanal_not_found(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.get_reporte_semanal",
            new=AsyncMock(side_effect=ReporteNoEncontradoError(999)),
        ),
    ):
        resp = client.get("/reportes/semanales/999", headers=_HEADERS)
    assert resp.status_code == 404


# --- POST /reportes/semanales/generar ---


async def test_generar_reporte_semanal_returns_201(client):
    reporte = _FakeReporte()
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.generar_reporte_semanal",
            new=AsyncMock(return_value=reporte),
        ),
    ):
        resp = client.post("/reportes/semanales/generar", headers=_HEADERS)
    assert resp.status_code == 201
    assert resp.json()["id"] == 1


async def test_generar_reporte_semanal_duplicate(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.generar_reporte_semanal",
            new=AsyncMock(side_effect=ReporteDuplicadoError("2026-07-20", "2026-07-26")),
        ),
    ):
        resp = client.post("/reportes/semanales/generar", headers=_HEADERS)
    assert resp.status_code == 409


# --- GET /reportes/semanales/{id}/excel ---


async def test_descargar_reporte_semanal_excel(client):
    reporte = _FakeReporte()
    asistencias = [_FakeAsistencia()]
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.reportes.reportes_service.get_reporte_semanal",
            new=AsyncMock(return_value=reporte),
        ),
        patch(
            "apps.API.routers.reportes.reportes_service.consultar_asistencia",
            new=AsyncMock(return_value=(asistencias, {})),
        ),
        patch(
            "apps.API.routers.reportes.reportes_service.generar_excel",
            return_value=b"PK\x03\x04fake-xlsx",
        ),
        patch(
            "apps.API.routers.reportes.reportes_service.generar_nombre_archivo",
            return_value="reporte_asistencia_2026-07-20_2026-07-26.xlsx",
        ),
    ):
        resp = client.get("/reportes/semanales/1/excel", headers=_HEADERS)
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]


# --- Auth ---


async def test_reportes_without_token_returns_403():
    app.dependency_overrides[get_session] = _fake_session
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    try:
        with TestClient(app) as test_client:
            resp = test_client.get("/reportes/asistencia")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()

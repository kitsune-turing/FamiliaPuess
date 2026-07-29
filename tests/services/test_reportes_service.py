from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services.reportes_service import (
    _validar_rango_fechas,
    consultar_asistencia,
    generar_excel,
    generar_nombre_archivo,
    generar_reporte_semanal,
    get_reporte_semanal,
    list_reportes_semanales,
)
from shared.exceptions.reportes import (
    RangoFechasInvalidoError,
    ReporteDuplicadoError,
    ReporteNoEncontradoError,
    ReporteSinDatosError,
)

FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)


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


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


def _patches(
    asistencias=None,
    novedades_map=None,
    reporte_by_id=None,
    reporte_by_periodo=None,
    reportes_all=None,
    reporte_created=None,
    novedades_count=0,
):
    return {
        "get_asistencias": patch(
            "apps.API.services.reportes_service.reporte_repository.get_asistencias_filtradas",
            new=AsyncMock(return_value=asistencias if asistencias is not None else []),
        ),
        "get_novedades": patch(
            "apps.API.services.reportes_service.reporte_repository.get_novedades_por_asistencia_ids",
            new=AsyncMock(return_value=novedades_map if novedades_map is not None else {}),
        ),
        "reporte_by_id": patch(
            "apps.API.services.reportes_service.reporte_repository.get_reporte_by_id",
            new=AsyncMock(return_value=reporte_by_id),
        ),
        "reporte_by_periodo": patch(
            "apps.API.services.reportes_service.reporte_repository.get_reporte_by_periodo",
            new=AsyncMock(return_value=reporte_by_periodo),
        ),
        "reportes_all": patch(
            "apps.API.services.reportes_service.reporte_repository.get_all_reportes",
            new=AsyncMock(return_value=reportes_all if reportes_all is not None else []),
        ),
        "create_reporte": patch(
            "apps.API.services.reportes_service.reporte_repository.create_reporte",
            new=AsyncMock(return_value=reporte_created),
        ),
        "contar_novedades": patch(
            "apps.API.services.reportes_service.reporte_repository.contar_novedades_periodo",
            new=AsyncMock(return_value=novedades_count),
        ),
        "auditoria": patch(
            "apps.API.services.reportes_service.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "tz_now": patch(
            "apps.API.services.reportes_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


# --- _validar_rango_fechas ---


def test_validar_rango_fechas_valid():
    _validar_rango_fechas(date(2026, 7, 1), date(2026, 7, 31))


def test_validar_rango_fechas_same_day():
    _validar_rango_fechas(date(2026, 7, 15), date(2026, 7, 15))


def test_validar_rango_fechas_invalid():
    with pytest.raises(RangoFechasInvalidoError):
        _validar_rango_fechas(date(2026, 7, 31), date(2026, 7, 1))


def test_validar_rango_fechas_none_accepted():
    _validar_rango_fechas(None, None)
    _validar_rango_fechas(date(2026, 7, 1), None)
    _validar_rango_fechas(None, date(2026, 7, 31))


# --- consultar_asistencia ---


async def test_consultar_asistencia_returns_data(session):
    asistencias = [_FakeAsistencia(id=100), _FakeAsistencia(id=101)]
    novedades = {100: _FakeNovedad(id_asistencia=100)}
    mocks = _patches(asistencias=asistencias, novedades_map=novedades)
    with mocks["get_asistencias"], mocks["get_novedades"]:
        result_a, result_n = await consultar_asistencia(session)
    assert len(result_a) == 2
    assert 100 in result_n


async def test_consultar_asistencia_with_filters(session):
    mocks = _patches(asistencias=[_FakeAsistencia()])
    with mocks["get_asistencias"], mocks["get_novedades"]:
        result_a, _ = await consultar_asistencia(
            session,
            id_empleado=1,
            id_sede=1,
            fecha_desde=date(2026, 7, 1),
            fecha_hasta=date(2026, 7, 31),
        )
    assert len(result_a) == 1


async def test_consultar_asistencia_invalid_range(session):
    with pytest.raises(RangoFechasInvalidoError):
        await consultar_asistencia(
            session,
            fecha_desde=date(2026, 7, 31),
            fecha_hasta=date(2026, 7, 1),
        )


async def test_consultar_asistencia_empty(session):
    mocks = _patches(asistencias=[], novedades_map={})
    with mocks["get_asistencias"], mocks["get_novedades"]:
        result_a, result_n = await consultar_asistencia(session)
    assert len(result_a) == 0
    assert result_n == {}


# --- generar_reporte_semanal ---


async def test_generar_reporte_semanal_success(session):
    reporte = _FakeReporte()
    mocks = _patches(
        reporte_by_periodo=None,
        asistencias=[_FakeAsistencia()],
        novedades_count=1,
        reporte_created=reporte,
    )
    with (
        mocks["reporte_by_periodo"],
        mocks["get_asistencias"],
        mocks["contar_novedades"],
        mocks["create_reporte"],
        mocks["auditoria"],
        mocks["tz_now"],
    ):
        result = await generar_reporte_semanal(
            session, fecha_referencia=date(2026, 7, 28), id_usuario=1
        )
    assert result.id == 1


async def test_generar_reporte_semanal_duplicate(session):
    existente = _FakeReporte()
    mocks = _patches(reporte_by_periodo=existente)
    with mocks["reporte_by_periodo"], mocks["tz_now"]:
        with pytest.raises(ReporteDuplicadoError):
            await generar_reporte_semanal(
                session, fecha_referencia=date(2026, 7, 28)
            )


async def test_generar_reporte_calculates_correct_week(session):
    reporte = _FakeReporte()
    created_mock = AsyncMock(return_value=reporte)
    mocks = _patches(
        reporte_by_periodo=None,
        asistencias=[],
        novedades_count=0,
        reporte_created=reporte,
    )
    with (
        mocks["reporte_by_periodo"],
        mocks["get_asistencias"],
        mocks["contar_novedades"],
        patch(
            "apps.API.services.reportes_service.reporte_repository.create_reporte",
            new=created_mock,
        ),
        mocks["auditoria"],
        mocks["tz_now"],
    ):
        await generar_reporte_semanal(
            session, fecha_referencia=date(2026, 7, 28)
        )
    call_kwargs = created_mock.call_args.kwargs
    assert call_kwargs["fecha_inicio"] == date(2026, 7, 20)
    assert call_kwargs["fecha_fin"] == date(2026, 7, 26)


# --- list_reportes_semanales ---


async def test_list_reportes_semanales(session):
    reportes = [_FakeReporte(id=1), _FakeReporte(id=2)]
    mocks = _patches(reportes_all=reportes)
    with mocks["reportes_all"]:
        result = await list_reportes_semanales(session)
    assert len(result) == 2


# --- get_reporte_semanal ---


async def test_get_reporte_semanal_found(session):
    reporte = _FakeReporte()
    mocks = _patches(reporte_by_id=reporte)
    with mocks["reporte_by_id"]:
        result = await get_reporte_semanal(session, 1)
    assert result.id == 1


async def test_get_reporte_semanal_not_found(session):
    mocks = _patches(reporte_by_id=None)
    with mocks["reporte_by_id"]:
        with pytest.raises(ReporteNoEncontradoError):
            await get_reporte_semanal(session, 999)


# --- generar_excel ---


def test_generar_excel_creates_xlsx():
    asistencias = [_FakeAsistencia(id=100)]
    novedades = {}
    result = generar_excel(asistencias, novedades)
    assert len(result) > 0
    assert result[:2] == b"PK"


def test_generar_excel_with_novedad():
    asistencias = [_FakeAsistencia(id=100)]
    novedades = {100: _FakeNovedad(id_asistencia=100)}
    result = generar_excel(asistencias, novedades)
    assert len(result) > 0


def test_generar_excel_empty_raises():
    with pytest.raises(ReporteSinDatosError):
        generar_excel([], {})


def test_generar_excel_novedad_without_color():
    cat = _FakeCatNovedad(color=None)
    asistencias = [_FakeAsistencia(id=100)]
    novedades = {100: _FakeNovedad(id_asistencia=100, tipo_novedad=cat)}
    result = generar_excel(asistencias, novedades)
    assert len(result) > 0


# --- generar_nombre_archivo ---


def test_generar_nombre_archivo_with_dates():
    result = generar_nombre_archivo(date(2026, 7, 1), date(2026, 7, 31))
    assert result == "reporte_asistencia_2026-07-01_2026-07-31.xlsx"


def test_generar_nombre_archivo_partial():
    result = generar_nombre_archivo(date(2026, 7, 1))
    assert result == "reporte_asistencia_2026-07-01.xlsx"


def test_generar_nombre_archivo_no_dates():
    with patch("apps.API.services.reportes_service.tz_now", return_value=FIXED_NOW):
        result = generar_nombre_archivo()
    assert result == "reporte_asistencia_2026-07-28.xlsx"

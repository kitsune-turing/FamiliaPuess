from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services.novedades_service import (
    _sumar_tolerancia,
    detectar_novedad_asistencia,
    get_novedad,
    get_novedad_by_asistencia,
    list_novedades,
)
from shared.exceptions.novedades import (
    NovedadNoEncontradaError,
    TipoNovedadNoEncontradoError,
)

FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeEmpleado:
    id: int = 1
    nombre: str = "Juan Perez"
    documento: str = "1234567890"


@dataclass
class _FakeCatNovedad:
    id: int = 1
    codigo: str = "TARDANZA"
    nombre: str = "Tardanza"
    color: str | None = "#FF0000"
    icono: str | None = "clock-alert"


@dataclass
class _FakeHorario:
    id: int = 1
    id_sede: int = 1
    hora_entrada: time = field(default_factory=lambda: time(8, 0))
    tolerancia_min: int = 15


@dataclass
class _FakeNovedad:
    id: int = 1
    id_empleado: int = 1
    id_tipo_novedad: int = 1
    id_asistencia: int | None = 10
    fecha: date = field(default_factory=lambda: date(2026, 7, 28))
    observacion: str | None = "Registro a las 08:30 - Entrada programada: 08:00 (tolerancia: 15 min)"
    created_at: datetime = field(default_factory=lambda: FIXED_NOW)
    empleado: _FakeEmpleado = field(default_factory=_FakeEmpleado)
    tipo_novedad: _FakeCatNovedad = field(default_factory=_FakeCatNovedad)


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


def _patches(
    horario_vigente=None,
    cat_novedad=None,
    novedad_created=None,
    novedad_by_id=None,
    novedad_by_asistencia=None,
    novedades_all=None,
):
    return {
        "get_vigente": patch(
            "apps.API.services.novedades_service.horario_repository.get_vigente_by_sede",
            new=AsyncMock(return_value=horario_vigente),
        ),
        "cat_by_codigo": patch(
            "apps.API.services.novedades_service.cat_novedad_repository.get_by_codigo",
            new=AsyncMock(return_value=cat_novedad),
        ),
        "novedad_create": patch(
            "apps.API.services.novedades_service.novedad_repository.create",
            new=AsyncMock(return_value=novedad_created),
        ),
        "novedad_by_id": patch(
            "apps.API.services.novedades_service.novedad_repository.get_by_id",
            new=AsyncMock(return_value=novedad_by_id),
        ),
        "novedad_by_asistencia": patch(
            "apps.API.services.novedades_service.novedad_repository.get_by_asistencia",
            new=AsyncMock(return_value=novedad_by_asistencia),
        ),
        "novedad_all": patch(
            "apps.API.services.novedades_service.novedad_repository.get_all",
            new=AsyncMock(return_value=novedades_all if novedades_all is not None else []),
        ),
        "tz_now": patch(
            "apps.API.services.novedades_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


# --- _sumar_tolerancia unit tests ---


def test_sumar_tolerancia_basic():
    result = _sumar_tolerancia(time(8, 0), 15)
    assert result == time(8, 15)


def test_sumar_tolerancia_crosses_hour():
    result = _sumar_tolerancia(time(8, 50), 30)
    assert result == time(9, 20)


def test_sumar_tolerancia_zero():
    result = _sumar_tolerancia(time(8, 0), 0)
    assert result == time(8, 0)


def test_sumar_tolerancia_120_min():
    result = _sumar_tolerancia(time(8, 0), 120)
    assert result == time(10, 0)


# --- detectar_novedad_asistencia ---


async def test_detectar_returns_none_when_no_horario(session):
    mocks = _patches(horario_vigente=None)
    with mocks["get_vigente"], mocks["tz_now"]:
        result = await detectar_novedad_asistencia(
            session,
            id_asistencia=10,
            id_empleado=1,
            id_sede=1,
            fecha_registro=date(2026, 7, 28),
            hora_registro=time(9, 0),
        )
    assert result is None


async def test_detectar_returns_none_when_on_time(session):
    horario = _FakeHorario(hora_entrada=time(8, 0), tolerancia_min=15)
    mocks = _patches(horario_vigente=horario)
    with mocks["get_vigente"], mocks["tz_now"]:
        result = await detectar_novedad_asistencia(
            session,
            id_asistencia=10,
            id_empleado=1,
            id_sede=1,
            fecha_registro=date(2026, 7, 28),
            hora_registro=time(8, 10),
        )
    assert result is None


async def test_detectar_returns_none_when_exactly_at_limit(session):
    horario = _FakeHorario(hora_entrada=time(8, 0), tolerancia_min=15)
    mocks = _patches(horario_vigente=horario)
    with mocks["get_vigente"], mocks["tz_now"]:
        result = await detectar_novedad_asistencia(
            session,
            id_asistencia=10,
            id_empleado=1,
            id_sede=1,
            fecha_registro=date(2026, 7, 28),
            hora_registro=time(8, 15),
        )
    assert result is None


async def test_detectar_creates_tardanza_when_late(session):
    horario = _FakeHorario(hora_entrada=time(8, 0), tolerancia_min=15)
    cat = _FakeCatNovedad()
    novedad = _FakeNovedad()
    mocks = _patches(
        horario_vigente=horario,
        cat_novedad=cat,
        novedad_created=novedad,
    )
    with (
        mocks["get_vigente"],
        mocks["cat_by_codigo"],
        mocks["novedad_create"],
        mocks["tz_now"],
    ):
        result = await detectar_novedad_asistencia(
            session,
            id_asistencia=10,
            id_empleado=1,
            id_sede=1,
            fecha_registro=date(2026, 7, 28),
            hora_registro=time(8, 16),
        )
    assert result is not None
    assert result.id == 1
    session.refresh.assert_awaited_once()


async def test_detectar_raises_when_cat_novedad_missing(session):
    horario = _FakeHorario(hora_entrada=time(8, 0), tolerancia_min=15)
    mocks = _patches(horario_vigente=horario, cat_novedad=None)
    with mocks["get_vigente"], mocks["cat_by_codigo"], mocks["tz_now"]:
        with pytest.raises(TipoNovedadNoEncontradoError):
            await detectar_novedad_asistencia(
                session,
                id_asistencia=10,
                id_empleado=1,
                id_sede=1,
                fecha_registro=date(2026, 7, 28),
                hora_registro=time(8, 30),
            )


async def test_detectar_uses_correct_tolerancia(session):
    horario = _FakeHorario(hora_entrada=time(7, 30), tolerancia_min=30)
    mocks = _patches(horario_vigente=horario)
    with mocks["get_vigente"], mocks["tz_now"]:
        result = await detectar_novedad_asistencia(
            session,
            id_asistencia=10,
            id_empleado=1,
            id_sede=1,
            fecha_registro=date(2026, 7, 28),
            hora_registro=time(8, 0),
        )
    assert result is None


async def test_detectar_zero_tolerance_late_by_one_minute(session):
    horario = _FakeHorario(hora_entrada=time(8, 0), tolerancia_min=0)
    cat = _FakeCatNovedad()
    novedad = _FakeNovedad()
    mocks = _patches(
        horario_vigente=horario,
        cat_novedad=cat,
        novedad_created=novedad,
    )
    with (
        mocks["get_vigente"],
        mocks["cat_by_codigo"],
        mocks["novedad_create"],
        mocks["tz_now"],
    ):
        result = await detectar_novedad_asistencia(
            session,
            id_asistencia=10,
            id_empleado=1,
            id_sede=1,
            fecha_registro=date(2026, 7, 28),
            hora_registro=time(8, 1),
        )
    assert result is not None


# --- list_novedades ---


async def test_list_novedades_returns_all(session):
    fake_list = [_FakeNovedad(id=1), _FakeNovedad(id=2)]
    mocks = _patches(novedades_all=fake_list)
    with mocks["novedad_all"]:
        result = await list_novedades(session)
    assert len(result) == 2


async def test_list_novedades_with_filters(session):
    fake_list = [_FakeNovedad(id=1)]
    mocks = _patches(novedades_all=fake_list)
    with mocks["novedad_all"]:
        result = await list_novedades(
            session,
            id_empleado=1,
            id_tipo_novedad=1,
            fecha_desde=date(2026, 7, 1),
            fecha_hasta=date(2026, 7, 31),
        )
    assert len(result) == 1


# --- get_novedad ---


async def test_get_novedad_returns_novedad(session):
    novedad = _FakeNovedad()
    mocks = _patches(novedad_by_id=novedad)
    with mocks["novedad_by_id"]:
        result = await get_novedad(session, 1)
    assert result.id == 1


async def test_get_novedad_raises_when_not_found(session):
    mocks = _patches(novedad_by_id=None)
    with mocks["novedad_by_id"]:
        with pytest.raises(NovedadNoEncontradaError):
            await get_novedad(session, 999)


# --- get_novedad_by_asistencia ---


async def test_get_novedad_by_asistencia_returns_novedad(session):
    novedad = _FakeNovedad()
    mocks = _patches(novedad_by_asistencia=novedad)
    with mocks["novedad_by_asistencia"]:
        result = await get_novedad_by_asistencia(session, 10)
    assert result.id == 1


async def test_get_novedad_by_asistencia_returns_none(session):
    mocks = _patches(novedad_by_asistencia=None)
    with mocks["novedad_by_asistencia"]:
        result = await get_novedad_by_asistencia(session, 999)
    assert result is None

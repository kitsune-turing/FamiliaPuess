from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services.horarios_service import (
    create_horario,
    finalizar_horario,
    get_horario,
    list_horarios,
    update_horario,
)
from shared.exceptions.horarios import (
    HorarioInmutableError,
    HorarioNoEncontradoError,
    HorarioSolapamientoError,
    HorarioToleranciaInvalidaError,
    HorarioVigenciaInvalidaError,
)
from shared.exceptions.sedes import SedeInactivaError, SedeNoEncontradaError

ACTIVO_ID = 1
FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeSede:
    id: int = 1
    nombre: str = "Sede Central"
    id_estado: int = ACTIVO_ID


@dataclass
class _FakeHorario:
    id: int = 1
    id_sede: int = 1
    nombre: str | None = "Horario Principal"
    hora_entrada: time = field(default_factory=lambda: time(8, 0))
    hora_salida: time | None = None
    tolerancia_min: int = 15
    vigente_desde: date = field(default_factory=lambda: date(2026, 1, 1))
    vigente_hasta: date | None = None
    created_at: datetime = field(default_factory=lambda: FIXED_NOW)
    sede: _FakeSede = field(default_factory=_FakeSede)


def _patches(
    horario=None,
    sede=None,
    vigente=None,
    horarios_all=None,
):
    return {
        "get_by_id": patch(
            "apps.API.services.horarios_service.horario_repository.get_by_id",
            new=AsyncMock(return_value=horario),
        ),
        "get_all": patch(
            "apps.API.services.horarios_service.horario_repository.get_all",
            new=AsyncMock(return_value=horarios_all if horarios_all is not None else []),
        ),
        "get_vigente": patch(
            "apps.API.services.horarios_service.horario_repository.get_vigente_by_sede",
            new=AsyncMock(return_value=vigente),
        ),
        "create": patch(
            "apps.API.services.horarios_service.horario_repository.create",
            new=AsyncMock(return_value=horario if horario else _FakeHorario()),
        ),
        "set_vigente_hasta": patch(
            "apps.API.services.horarios_service.horario_repository.set_vigente_hasta",
            new=AsyncMock(),
        ),
        "sede_get": patch(
            "apps.API.services.horarios_service.sede_repository.get_by_id",
            new=AsyncMock(return_value=sede if sede is not None else _FakeSede()),
        ),
        "get_estado_id": patch(
            "apps.API.services.horarios_service.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
        "auditoria": patch(
            "apps.API.services.horarios_service.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "now": patch(
            "apps.API.services.horarios_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


@pytest.fixture
def session():
    s = AsyncMock(spec=AsyncSession)
    s.refresh = AsyncMock()
    return s


# ===== list_horarios =====

async def test_list_horarios(session):
    p = _patches(horarios_all=[_FakeHorario()])
    with p["get_all"]:
        result = await list_horarios(session)
    assert len(result) == 1


async def test_list_horarios_with_sede_filter(session):
    p = _patches(horarios_all=[_FakeHorario()])
    with p["get_all"]:
        result = await list_horarios(session, id_sede=1)
    assert len(result) == 1


# ===== get_horario =====

async def test_get_horario_success(session):
    p = _patches(horario=_FakeHorario())
    with p["get_by_id"]:
        result = await get_horario(session, 1)
    assert result.id == 1


async def test_get_horario_not_found(session):
    p = _patches(horario=None)
    with p["get_by_id"]:
        with pytest.raises(HorarioNoEncontradoError):
            await get_horario(session, 999)


# ===== create_horario (HU-HOR-001) =====

async def test_create_horario_success(session):
    nuevo = _FakeHorario(id=10, vigente_desde=date(2026, 8, 1))
    p = _patches(horario=nuevo, vigente=None)
    with p["sede_get"], p["get_estado_id"], p["get_vigente"], p["create"], \
         p["auditoria"], p["now"]:
        result = await create_horario(
            session,
            id_sede=1,
            hora_entrada=time(8, 0),
            tolerancia_min=15,
            vigente_desde=date(2026, 8, 1),
            user_id=1,
        )
    assert result.id == 10


async def test_create_horario_sede_not_found(session):
    p = _patches(sede=None)
    p["sede_get"] = patch(
        "apps.API.services.horarios_service.sede_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    with p["sede_get"], p["get_estado_id"]:
        with pytest.raises(SedeNoEncontradaError):
            await create_horario(
                session,
                id_sede=999,
                hora_entrada=time(8, 0),
                vigente_desde=date(2026, 8, 1),
                user_id=1,
            )


async def test_create_horario_sede_inactive(session):
    sede_inactiva = _FakeSede(id_estado=99)
    p = _patches(sede=sede_inactiva)
    with p["sede_get"], p["get_estado_id"]:
        with pytest.raises(SedeInactivaError):
            await create_horario(
                session,
                id_sede=1,
                hora_entrada=time(8, 0),
                vigente_desde=date(2026, 8, 1),
                user_id=1,
            )


async def test_create_horario_invalid_tolerancia(session):
    with pytest.raises(HorarioToleranciaInvalidaError):
        await create_horario(
            session,
            id_sede=1,
            hora_entrada=time(8, 0),
            tolerancia_min=150,
            vigente_desde=date(2026, 8, 1),
            user_id=1,
        )


async def test_create_horario_negative_tolerancia(session):
    with pytest.raises(HorarioToleranciaInvalidaError):
        await create_horario(
            session,
            id_sede=1,
            hora_entrada=time(8, 0),
            tolerancia_min=-5,
            vigente_desde=date(2026, 8, 1),
            user_id=1,
        )


async def test_create_horario_invalid_vigencia(session):
    with pytest.raises(HorarioVigenciaInvalidaError):
        await create_horario(
            session,
            id_sede=1,
            hora_entrada=time(8, 0),
            vigente_desde=date(2026, 8, 1),
            vigente_hasta=date(2026, 7, 1),
            user_id=1,
        )


async def test_create_horario_closes_previous(session):
    anterior = _FakeHorario(id=5, vigente_desde=date(2026, 1, 1), vigente_hasta=None)
    nuevo = _FakeHorario(id=10, vigente_desde=date(2026, 8, 1))
    p = _patches(horario=nuevo, vigente=anterior)
    with p["sede_get"], p["get_estado_id"], p["get_vigente"], p["create"], \
         p["set_vigente_hasta"], p["auditoria"], p["now"]:
        result = await create_horario(
            session,
            id_sede=1,
            hora_entrada=time(9, 0),
            vigente_desde=date(2026, 8, 1),
            user_id=1,
        )
    assert result.id == 10


async def test_create_horario_solapamiento_same_day(session):
    anterior = _FakeHorario(
        id=5, vigente_desde=date(2026, 8, 1), vigente_hasta=None
    )
    p = _patches(vigente=anterior)
    with p["sede_get"], p["get_estado_id"], p["get_vigente"]:
        with pytest.raises(HorarioSolapamientoError):
            await create_horario(
                session,
                id_sede=1,
                hora_entrada=time(9, 0),
                vigente_desde=date(2026, 8, 1),
                user_id=1,
            )


# ===== update_horario (HU-HOR-001 / HU-HOR-003) =====

async def test_update_horario_success(session):
    horario = _FakeHorario()
    p = _patches(horario=horario)
    with p["get_by_id"], p["auditoria"], p["now"]:
        result = await update_horario(
            session,
            1,
            nombre="Horario Nuevo",
            user_id=1,
        )
    assert result.nombre == "Horario Nuevo"


async def test_update_horario_not_found(session):
    p = _patches(horario=None)
    with p["get_by_id"]:
        with pytest.raises(HorarioNoEncontradoError):
            await update_horario(session, 999, user_id=1)


async def test_update_horario_inmutable(session):
    horario = _FakeHorario(vigente_hasta=date(2020, 1, 1))
    p = _patches(horario=horario)
    with p["get_by_id"]:
        with pytest.raises(HorarioInmutableError):
            await update_horario(session, 1, nombre="X", user_id=1)


async def test_update_tolerancia_success(session):
    horario = _FakeHorario()
    p = _patches(horario=horario)
    with p["get_by_id"], p["auditoria"], p["now"]:
        result = await update_horario(
            session,
            1,
            tolerancia_min=30,
            user_id=1,
        )
    assert result.tolerancia_min == 30


async def test_update_tolerancia_invalid(session):
    horario = _FakeHorario()
    p = _patches(horario=horario)
    with p["get_by_id"]:
        with pytest.raises(HorarioToleranciaInvalidaError):
            await update_horario(session, 1, tolerancia_min=200, user_id=1)


async def test_update_hora_entrada(session):
    horario = _FakeHorario()
    p = _patches(horario=horario)
    with p["get_by_id"], p["auditoria"], p["now"]:
        result = await update_horario(
            session,
            1,
            hora_entrada=time(9, 30),
            user_id=1,
        )
    assert result.hora_entrada == time(9, 30)


async def test_update_vigente_hasta_invalid(session):
    horario = _FakeHorario(vigente_desde=date(2026, 8, 1))
    p = _patches(horario=horario)
    with p["get_by_id"]:
        with pytest.raises(HorarioVigenciaInvalidaError):
            await update_horario(
                session,
                1,
                vigente_hasta=date(2026, 7, 1),
                user_id=1,
            )


# ===== finalizar_horario =====

async def test_finalizar_horario_success(session):
    horario = _FakeHorario()
    p = _patches(horario=horario)
    with p["get_by_id"], p["set_vigente_hasta"], p["auditoria"], p["now"]:
        await finalizar_horario(session, 1, user_id=1)


async def test_finalizar_horario_not_found(session):
    p = _patches(horario=None)
    with p["get_by_id"]:
        with pytest.raises(HorarioNoEncontradoError):
            await finalizar_horario(session, 999, user_id=1)


async def test_finalizar_horario_inmutable(session):
    horario = _FakeHorario(vigente_hasta=date(2020, 1, 1))
    p = _patches(horario=horario)
    with p["get_by_id"]:
        with pytest.raises(HorarioInmutableError):
            await finalizar_horario(session, 1, user_id=1)


# ===== Historial (HU-HOR-002) =====

async def test_list_horarios_returns_history_ordered(session):
    h1 = _FakeHorario(id=1, vigente_desde=date(2026, 1, 1), vigente_hasta=date(2026, 6, 30))
    h2 = _FakeHorario(id=2, vigente_desde=date(2026, 7, 1), vigente_hasta=None)
    p = _patches(horarios_all=[h2, h1])
    with p["get_all"]:
        result = await list_horarios(session, id_sede=1)
    assert len(result) == 2
    assert result[0].id == 2
    assert result[1].id == 1


async def test_list_horarios_solo_vigentes(session):
    p = _patches(horarios_all=[_FakeHorario()])
    with p["get_all"]:
        result = await list_horarios(session, id_sede=1, solo_vigentes=True)
    assert len(result) == 1

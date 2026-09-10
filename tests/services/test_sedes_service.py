from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import sedes_service
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.sedes import (
    SedeDireccionInvalidaError,
    SedeNoEncontradaError,
    SedeNombreDuplicadoError,
    SedeNombreInvalidoError,
)

ACTIVO_ID = 1
INACTIVO_ID = 2
FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeSede:
    id: int = 1
    nombre: str = "Sede Central"
    direccion: str = "Calle 100 #15-20"
    id_estado: int = ACTIVO_ID
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW


def _patches(sede=None, sede_by_nombre=None):
    if sede is None:
        sede = _FakeSede()

    return {
        "get_by_id": patch(
            "apps.API.repositories.sede_repository.get_by_id",
            new=AsyncMock(return_value=sede),
        ),
        "get_by_nombre": patch(
            "apps.API.repositories.sede_repository.get_by_nombre",
            new=AsyncMock(return_value=sede_by_nombre),
        ),
        "get_all": patch(
            "apps.API.repositories.sede_repository.get_all",
            new=AsyncMock(return_value=[sede]),
        ),
        "create": patch(
            "apps.API.repositories.sede_repository.create",
            new=AsyncMock(return_value=sede),
        ),
        "update_sede": patch(
            "apps.API.repositories.sede_repository.update_sede",
            new=AsyncMock(),
        ),
        "get_estado_id": patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
        "auditoria": patch(
            "apps.API.repositories.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "now": patch(
            "apps.API.services.sedes_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


# ── list_sedes ──


async def test_list_sedes_returns_all():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_all"]:
        result = await sedes_service.list_sedes(session)

    assert len(result) == 1


async def test_list_sedes_with_filters():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_all"] as mock_get_all:
        await sedes_service.list_sedes(
            session, nombre="Central", id_estado=1
        )

    mock_get_all.assert_awaited_once_with(
        session,
        nombre="Central",
        direccion=None,
        id_estado=1,
    )


# ── get_sede ──


async def test_get_sede_returns_existing():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        result = await sedes_service.get_sede(session, 1)

    assert result.nombre == "Sede Central"


async def test_get_sede_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.sede_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(SedeNoEncontradaError):
            await sedes_service.get_sede(session, 999)


# ── create_sede ──


async def test_create_sede_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_nombre"],
        p["get_estado_id"],
        p["create"] as mock_create,
        p["auditoria"],
        p["now"],
    ):
        result = await sedes_service.create_sede(
            session,
            nombre="Sede Norte",
            direccion="Carrera 50 #30-10",
            user_id=1,
        )

    assert result.nombre == "Sede Central"
    mock_create.assert_awaited_once()


async def test_create_sede_raises_on_duplicate_nombre():
    existing = _FakeSede()
    p = _patches(sede_by_nombre=existing)
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_nombre"]:
        with pytest.raises(SedeNombreDuplicadoError):
            await sedes_service.create_sede(
                session,
                nombre="Sede Central",
                direccion="Calle 200 #10-5",
                user_id=1,
            )


async def test_create_sede_raises_on_invalid_nombre():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(SedeNombreInvalidoError):
        await sedes_service.create_sede(
            session,
            nombre="Sede @#$!",
            direccion="Calle 100 #15-20",
            user_id=1,
        )


async def test_create_sede_raises_on_invalid_direccion():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_nombre"]:
        with pytest.raises(SedeDireccionInvalidaError):
            await sedes_service.create_sede(
                session,
                nombre="Sede Norte",
                direccion="Calle 100 @$%&",
                user_id=1,
            )


# ── update_sede ──


async def test_update_sede_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["update_sede"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        result = await sedes_service.update_sede(
            session,
            1,
            direccion="Carrera 80 #10-5",
            updated_at=FIXED_NOW,
            user_id=1,
        )

    mock_update.assert_awaited_once()


async def test_update_sede_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.sede_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(SedeNoEncontradaError):
            await sedes_service.update_sede(
                session,
                999,
                nombre="Test",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_sede_raises_on_concurrency_conflict():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)
    stale_time = datetime(2020, 1, 1, tzinfo=timezone.utc)

    with p["get_by_id"]:
        with pytest.raises(ConflictoConcurrenciaError):
            await sedes_service.update_sede(
                session,
                1,
                nombre="Test",
                updated_at=stale_time,
                user_id=1,
            )


async def test_update_sede_raises_on_duplicate_nombre():
    other = _FakeSede(id=2, nombre="Sede Sur")
    p = _patches()
    p["get_by_nombre"] = patch(
        "apps.API.repositories.sede_repository.get_by_nombre",
        new=AsyncMock(return_value=other),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"], p["get_by_nombre"]:
        with pytest.raises(SedeNombreDuplicadoError):
            await sedes_service.update_sede(
                session,
                1,
                nombre="Sede Sur",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_sede_raises_on_invalid_nombre():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(SedeNombreInvalidoError):
            await sedes_service.update_sede(
                session,
                1,
                nombre="Sede @!#",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_sede_raises_on_invalid_direccion():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(SedeDireccionInvalidaError):
            await sedes_service.update_sede(
                session,
                1,
                direccion="Calle @$%&",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_sede_allows_editing_inactive():
    inactive = _FakeSede(id_estado=INACTIVO_ID)
    p = _patches(sede=inactive)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["update_sede"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await sedes_service.update_sede(
            session,
            1,
            direccion="Nueva Direccion 123",
            updated_at=FIXED_NOW,
            user_id=1,
        )

    mock_update.assert_awaited_once()


# ── deactivate_sede ──


async def test_deactivate_sede_success():
    p = _patches()
    p["get_estado_id"] = patch(
        "apps.API.repositories.cat_estado_repository.get_estado_id",
        new=AsyncMock(return_value=INACTIVO_ID),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_estado_id"],
        p["update_sede"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await sedes_service.deactivate_sede(session, 1, user_id=1)

    mock_update.assert_awaited_once()


async def test_deactivate_sede_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.sede_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(SedeNoEncontradaError):
            await sedes_service.deactivate_sede(session, 999, user_id=1)


# ── activate_sede ──


async def test_activate_sede_success():
    inactive = _FakeSede(id_estado=INACTIVO_ID)
    p = _patches(sede=inactive)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_estado_id"],
        p["update_sede"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await sedes_service.activate_sede(session, 1, user_id=1)

    mock_update.assert_awaited_once()


async def test_activate_sede_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.sede_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(SedeNoEncontradaError):
            await sedes_service.activate_sede(session, 999, user_id=1)

from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import dispositivos_service
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.device import (
    DispositivoNoEncontradoPorIdError,
    IdentificadorDuplicadoError,
    IdentificadorFormatoInvalidoError,
    SedeYaTieneDispositivoError,
)
from shared.exceptions.sedes import SedeInactivaError, SedeNoEncontradaError

ACTIVO_ID = 1
INACTIVO_ID = 2
FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeSede:
    id: int = 1
    nombre: str = "Sede Central"
    id_estado: int = ACTIVO_ID


@dataclass
class _FakeDispositivo:
    id: int = 10
    identificador: str = "DEVICE-001-ABC"
    id_sede: int = 1
    id_estado: int = ACTIVO_ID
    descripcion: str = "Celular Samsung"
    sede: _FakeSede = None
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW

    def __post_init__(self):
        if self.sede is None:
            self.sede = _FakeSede()


def _patches(
    dispositivo=None,
    dispositivo_by_ident=None,
    sede=None,
    active_by_sede=None,
):
    if dispositivo is None:
        dispositivo = _FakeDispositivo()
    if sede is None:
        sede = _FakeSede()

    return {
        "get_by_id": patch(
            "apps.API.repositories.dispositivo_repository.get_by_id",
            new=AsyncMock(return_value=dispositivo),
        ),
        "get_by_identificador": patch(
            "apps.API.repositories.dispositivo_repository.get_by_identificador",
            new=AsyncMock(return_value=dispositivo_by_ident),
        ),
        "get_active_by_sede": patch(
            "apps.API.repositories.dispositivo_repository.get_active_by_sede",
            new=AsyncMock(return_value=active_by_sede),
        ),
        "get_all": patch(
            "apps.API.repositories.dispositivo_repository.get_all",
            new=AsyncMock(return_value=[dispositivo]),
        ),
        "create": patch(
            "apps.API.repositories.dispositivo_repository.create",
            new=AsyncMock(return_value=dispositivo),
        ),
        "update_dispositivo": patch(
            "apps.API.repositories.dispositivo_repository.update_dispositivo",
            new=AsyncMock(),
        ),
        "sede_get_by_id": patch(
            "apps.API.repositories.sede_repository.get_by_id",
            new=AsyncMock(return_value=sede),
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
            "apps.API.services.dispositivos_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


# ── list_dispositivos ──


async def test_list_dispositivos_returns_all():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_all"]:
        result = await dispositivos_service.list_dispositivos(session)

    assert len(result) == 1


async def test_list_dispositivos_with_filters():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_all"] as mock_get_all:
        await dispositivos_service.list_dispositivos(
            session, id_sede=1, id_estado=1
        )

    mock_get_all.assert_awaited_once_with(
        session,
        identificador=None,
        id_sede=1,
        id_estado=1,
    )


# ── get_dispositivo ──


async def test_get_dispositivo_returns_existing():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        result = await dispositivos_service.get_dispositivo(session, 10)

    assert result.identificador == "DEVICE-001-ABC"


async def test_get_dispositivo_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.dispositivo_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(DispositivoNoEncontradoPorIdError):
            await dispositivos_service.get_dispositivo(session, 999)


# ── create_dispositivo ──


async def test_create_dispositivo_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_identificador"],
        p["sede_get_by_id"],
        p["get_estado_id"],
        p["get_active_by_sede"],
        p["create"] as mock_create,
        p["auditoria"],
        p["now"],
    ):
        result = await dispositivos_service.create_dispositivo(
            session,
            identificador="DEVICE-002-XYZ",
            id_sede=1,
            descripcion="Celular nuevo",
            user_id=1,
        )

    assert result.identificador == "DEVICE-001-ABC"
    mock_create.assert_awaited_once()


async def test_create_dispositivo_raises_on_duplicate_identificador():
    existing = _FakeDispositivo()
    p = _patches(dispositivo_by_ident=existing)
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_identificador"]:
        with pytest.raises(IdentificadorDuplicadoError):
            await dispositivos_service.create_dispositivo(
                session,
                identificador="DEVICE-001-ABC",
                id_sede=1,
                user_id=1,
            )


async def test_create_dispositivo_raises_on_invalid_identificador():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(IdentificadorFormatoInvalidoError):
        await dispositivos_service.create_dispositivo(
            session,
            identificador="DEV @#$!",
            id_sede=1,
            user_id=1,
        )


async def test_create_dispositivo_raises_on_sede_not_found():
    p = _patches(sede=None)
    p["sede_get_by_id"] = patch(
        "apps.API.repositories.sede_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_identificador"], p["sede_get_by_id"]:
        with pytest.raises(SedeNoEncontradaError):
            await dispositivos_service.create_dispositivo(
                session,
                identificador="DEVICE-002-XYZ",
                id_sede=999,
                user_id=1,
            )


async def test_create_dispositivo_raises_on_sede_inactiva():
    sede_inactiva = _FakeSede(id_estado=INACTIVO_ID)
    p = _patches(sede=sede_inactiva)
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_identificador"], p["sede_get_by_id"], p["get_estado_id"]:
        with pytest.raises(SedeInactivaError):
            await dispositivos_service.create_dispositivo(
                session,
                identificador="DEVICE-002-XYZ",
                id_sede=1,
                user_id=1,
            )


async def test_create_dispositivo_raises_when_sede_already_has_active_device():
    existing_device = _FakeDispositivo(id=20, identificador="OTHER-DEVICE")
    p = _patches(active_by_sede=existing_device)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_identificador"],
        p["sede_get_by_id"],
        p["get_estado_id"],
        p["get_active_by_sede"],
    ):
        with pytest.raises(SedeYaTieneDispositivoError):
            await dispositivos_service.create_dispositivo(
                session,
                identificador="DEVICE-002-XYZ",
                id_sede=1,
                user_id=1,
            )


# ── update_dispositivo ──


async def test_update_dispositivo_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_by_identificador"],
        p["update_dispositivo"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        result = await dispositivos_service.update_dispositivo(
            session,
            10,
            identificador="DEVICE-003-NEW",
            updated_at=FIXED_NOW,
            user_id=1,
        )

    mock_update.assert_awaited_once()


async def test_update_dispositivo_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.dispositivo_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(DispositivoNoEncontradoPorIdError):
            await dispositivos_service.update_dispositivo(
                session,
                999,
                identificador="DEVICE-NEW",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_dispositivo_raises_on_concurrency_conflict():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)
    stale_time = datetime(2020, 1, 1, tzinfo=timezone.utc)

    with p["get_by_id"]:
        with pytest.raises(ConflictoConcurrenciaError):
            await dispositivos_service.update_dispositivo(
                session,
                10,
                identificador="DEVICE-NEW",
                updated_at=stale_time,
                user_id=1,
            )


async def test_update_dispositivo_raises_on_duplicate_identificador():
    other = _FakeDispositivo(id=20, identificador="DEVICE-OTHER")
    p = _patches()
    p["get_by_identificador"] = patch(
        "apps.API.repositories.dispositivo_repository.get_by_identificador",
        new=AsyncMock(return_value=other),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"], p["get_by_identificador"]:
        with pytest.raises(IdentificadorDuplicadoError):
            await dispositivos_service.update_dispositivo(
                session,
                10,
                identificador="DEVICE-OTHER",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_dispositivo_raises_on_invalid_identificador():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(IdentificadorFormatoInvalidoError):
            await dispositivos_service.update_dispositivo(
                session,
                10,
                identificador="DEV @#$",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_dispositivo_allows_editing_inactive():
    inactive = _FakeDispositivo(id_estado=INACTIVO_ID)
    p = _patches(dispositivo=inactive)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["update_dispositivo"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await dispositivos_service.update_dispositivo(
            session,
            10,
            descripcion="Nueva descripcion",
            updated_at=FIXED_NOW,
            user_id=1,
        )

    mock_update.assert_awaited_once()


# ── deactivate_dispositivo ──


async def test_deactivate_dispositivo_success():
    p = _patches()
    p["get_estado_id"] = patch(
        "apps.API.repositories.cat_estado_repository.get_estado_id",
        new=AsyncMock(return_value=INACTIVO_ID),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_estado_id"],
        p["update_dispositivo"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await dispositivos_service.deactivate_dispositivo(session, 10, user_id=1)

    mock_update.assert_awaited_once()


async def test_deactivate_dispositivo_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.dispositivo_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(DispositivoNoEncontradoPorIdError):
            await dispositivos_service.deactivate_dispositivo(session, 999, user_id=1)


# ── activate_dispositivo ──


async def test_activate_dispositivo_success():
    inactive = _FakeDispositivo(id_estado=INACTIVO_ID)
    p = _patches(dispositivo=inactive)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_estado_id"],
        p["get_active_by_sede"],
        p["update_dispositivo"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await dispositivos_service.activate_dispositivo(session, 10, user_id=1)

    mock_update.assert_awaited_once()


async def test_activate_dispositivo_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.dispositivo_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(DispositivoNoEncontradoPorIdError):
            await dispositivos_service.activate_dispositivo(session, 999, user_id=1)


async def test_activate_dispositivo_raises_when_sede_already_has_active():
    inactive = _FakeDispositivo(id=10, id_estado=INACTIVO_ID)
    other_active = _FakeDispositivo(id=20, identificador="OTHER-ACTIVE")
    p = _patches(dispositivo=inactive, active_by_sede=other_active)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_estado_id"],
        p["get_active_by_sede"],
    ):
        with pytest.raises(SedeYaTieneDispositivoError):
            await dispositivos_service.activate_dispositivo(session, 10, user_id=1)

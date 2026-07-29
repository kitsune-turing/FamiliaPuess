from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import empleados_service
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.empleados import (
    DocumentoDuplicadoError,
    DocumentoFormatoInvalidoError,
    EmpleadoNoEncontradoError,
    NombreInvalidoError,
    SedeInactivaError,
    SedeNoEncontradaError,
)

ACTIVO_ID = 1
INACTIVO_ID = 2
FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeSede:
    id: int = 1
    nombre: str = "Sede Central"
    id_estado: int = ACTIVO_ID


@dataclass
class _FakeEmpleado:
    id: int = 10
    documento: str = "12345678"
    nombre: str = "Juan"
    apellido: str = "Perez"
    cargo: str = "Operario"
    id_estado: int = ACTIVO_ID
    id_sede: int = 1
    sede: _FakeSede = None
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW

    def __post_init__(self):
        if self.sede is None:
            self.sede = _FakeSede()


def _patches(
    empleado=None,
    empleado_by_doc=None,
    sede=None,
):
    if empleado is None:
        empleado = _FakeEmpleado()
    if sede is None:
        sede = _FakeSede()

    return {
        "get_by_id": patch(
            "apps.API.repositories.empleado_repository.get_by_id",
            new=AsyncMock(return_value=empleado),
        ),
        "get_by_documento": patch(
            "apps.API.repositories.empleado_repository.get_by_documento",
            new=AsyncMock(return_value=empleado_by_doc),
        ),
        "get_all": patch(
            "apps.API.repositories.empleado_repository.get_all",
            new=AsyncMock(return_value=[empleado]),
        ),
        "create": patch(
            "apps.API.repositories.empleado_repository.create",
            new=AsyncMock(return_value=empleado),
        ),
        "update_empleado": patch(
            "apps.API.repositories.empleado_repository.update_empleado",
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
            "apps.API.services.empleados_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


# ── list_empleados ──


async def test_list_empleados_returns_all():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_all"]:
        result = await empleados_service.list_empleados(session)

    assert len(result) == 1


async def test_list_empleados_with_filters():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_all"] as mock_get_all:
        await empleados_service.list_empleados(
            session, nombre="Juan", cargo="Operario", id_estado=1
        )

    mock_get_all.assert_awaited_once_with(
        session,
        nombre="Juan",
        documento=None,
        cargo="Operario",
        id_estado=1,
        id_sede=None,
    )


# ── get_empleado ──


async def test_get_empleado_returns_existing():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        result = await empleados_service.get_empleado(session, 10)

    assert result.documento == "12345678"


async def test_get_empleado_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.empleado_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(EmpleadoNoEncontradoError):
            await empleados_service.get_empleado(session, 999)


# ── create_empleado ──


async def test_create_empleado_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_documento"],
        p["sede_get_by_id"],
        p["get_estado_id"],
        p["create"] as mock_create,
        p["auditoria"],
        p["now"],
    ):
        result = await empleados_service.create_empleado(
            session,
            documento="87654321",
            nombre="Maria",
            apellido="Lopez",
            cargo="Supervisora",
            id_sede=1,
            user_id=1,
        )

    assert result.documento == "12345678"
    mock_create.assert_awaited_once()


async def test_create_empleado_raises_on_duplicate_documento():
    existing = _FakeEmpleado()
    p = _patches(empleado_by_doc=existing)
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_documento"]:
        with pytest.raises(DocumentoDuplicadoError):
            await empleados_service.create_empleado(
                session,
                documento="12345678",
                nombre="Maria",
                apellido="Lopez",
                cargo="Operaria",
                id_sede=1,
                user_id=1,
            )


async def test_create_empleado_raises_on_invalid_documento():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(DocumentoFormatoInvalidoError):
        await empleados_service.create_empleado(
            session,
            documento="ABC",
            nombre="Maria",
            apellido="Lopez",
            cargo="Operaria",
            id_sede=1,
            user_id=1,
        )


async def test_create_empleado_raises_on_invalid_nombre():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(NombreInvalidoError):
        await empleados_service.create_empleado(
            session,
            documento="12345678",
            nombre="Juan123",
            apellido="Lopez",
            cargo="Operario",
            id_sede=1,
            user_id=1,
        )


async def test_create_empleado_raises_on_invalid_apellido():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(NombreInvalidoError):
        await empleados_service.create_empleado(
            session,
            documento="12345678",
            nombre="Juan",
            apellido="Perez@!",
            cargo="Operario",
            id_sede=1,
            user_id=1,
        )


async def test_create_empleado_raises_on_sede_not_found():
    p = _patches(sede=None)
    p["sede_get_by_id"] = patch(
        "apps.API.repositories.sede_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_documento"], p["sede_get_by_id"]:
        with pytest.raises(SedeNoEncontradaError):
            await empleados_service.create_empleado(
                session,
                documento="87654321",
                nombre="Maria",
                apellido="Lopez",
                cargo="Operaria",
                id_sede=999,
                user_id=1,
            )


async def test_create_empleado_raises_on_sede_inactiva():
    sede_inactiva = _FakeSede(id_estado=INACTIVO_ID)
    p = _patches(sede=sede_inactiva)
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_documento"], p["sede_get_by_id"], p["get_estado_id"]:
        with pytest.raises(SedeInactivaError):
            await empleados_service.create_empleado(
                session,
                documento="87654321",
                nombre="Maria",
                apellido="Lopez",
                cargo="Operaria",
                id_sede=1,
                user_id=1,
            )


# ── update_empleado ──


async def test_update_empleado_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["update_empleado"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        result = await empleados_service.update_empleado(
            session,
            10,
            cargo="Jefe de Operaciones",
            updated_at=FIXED_NOW,
            user_id=1,
        )

    mock_update.assert_awaited_once()


async def test_update_empleado_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.empleado_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(EmpleadoNoEncontradoError):
            await empleados_service.update_empleado(
                session,
                999,
                nombre="Test",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_empleado_raises_on_concurrency_conflict():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)
    stale_time = datetime(2020, 1, 1, tzinfo=timezone.utc)

    with p["get_by_id"]:
        with pytest.raises(ConflictoConcurrenciaError):
            await empleados_service.update_empleado(
                session,
                10,
                nombre="Test",
                updated_at=stale_time,
                user_id=1,
            )


async def test_update_empleado_raises_on_duplicate_documento():
    other = _FakeEmpleado(id=20, documento="99999999")
    p = _patches()
    p["get_by_documento"] = patch(
        "apps.API.repositories.empleado_repository.get_by_documento",
        new=AsyncMock(return_value=other),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"], p["get_by_documento"]:
        with pytest.raises(DocumentoDuplicadoError):
            await empleados_service.update_empleado(
                session,
                10,
                documento="99999999",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_empleado_raises_on_invalid_documento():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(DocumentoFormatoInvalidoError):
            await empleados_service.update_empleado(
                session,
                10,
                documento="ABCDE",
                updated_at=FIXED_NOW,
                user_id=1,
            )


async def test_update_empleado_allows_editing_inactive():
    inactive = _FakeEmpleado(id_estado=INACTIVO_ID)
    p = _patches(empleado=inactive)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["update_empleado"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await empleados_service.update_empleado(
            session,
            10,
            cargo="Nuevo Cargo",
            updated_at=FIXED_NOW,
            user_id=1,
        )

    mock_update.assert_awaited_once()


# ── deactivate_empleado ──


async def test_deactivate_empleado_success():
    p = _patches()
    p["get_estado_id"] = patch(
        "apps.API.repositories.cat_estado_repository.get_estado_id",
        new=AsyncMock(return_value=INACTIVO_ID),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_estado_id"],
        p["update_empleado"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await empleados_service.deactivate_empleado(session, 10, user_id=1)

    mock_update.assert_awaited_once()


async def test_deactivate_empleado_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.empleado_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(EmpleadoNoEncontradoError):
            await empleados_service.deactivate_empleado(session, 999, user_id=1)


# ── activate_empleado ──


async def test_activate_empleado_success():
    inactive = _FakeEmpleado(id_estado=INACTIVO_ID)
    p = _patches(empleado=inactive)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["get_estado_id"],
        p["update_empleado"] as mock_update,
        p["auditoria"],
        p["now"],
    ):
        await empleados_service.activate_empleado(session, 10, user_id=1)

    mock_update.assert_awaited_once()


async def test_activate_empleado_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.empleado_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(EmpleadoNoEncontradoError):
            await empleados_service.activate_empleado(session, 999, user_id=1)

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services.auditoria_service import list_auditoria


@dataclass
class _FakeAuditoria:
    id: int = 1
    id_usuario: int | None = 1
    recurso: str = "USUARIO"
    id_recurso: str | None = "5"
    operacion: str = "INSERT"
    valor_anterior: dict | None = None
    valor_nuevo: dict | None = field(default_factory=lambda: {"nombre": "Test"})
    ip_address: str | None = "127.0.0.1"
    detalle: str | None = None
    timestamp_accion: datetime = field(
        default_factory=lambda: datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)
    )


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


def _patches(records=None, total=0):
    if records is None:
        records = []
    return {
        "get_all": patch(
            "apps.API.services.auditoria_service.auditoria_repository.get_all",
            new=AsyncMock(return_value=records),
        ),
        "count": patch(
            "apps.API.services.auditoria_service.auditoria_repository.count",
            new=AsyncMock(return_value=total),
        ),
    }


async def test_list_auditoria_returns_items_and_total(session):
    records = [_FakeAuditoria(id=1), _FakeAuditoria(id=2)]
    mocks = _patches(records=records, total=2)
    with mocks["get_all"], mocks["count"]:
        result = await list_auditoria(session)
    assert result.total == 2
    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[1].id == 2


async def test_list_auditoria_empty(session):
    mocks = _patches(records=[], total=0)
    with mocks["get_all"], mocks["count"]:
        result = await list_auditoria(session)
    assert result.total == 0
    assert result.items == []


async def test_list_auditoria_passes_filters(session):
    get_all_mock = AsyncMock(return_value=[_FakeAuditoria()])
    count_mock = AsyncMock(return_value=1)
    with (
        patch(
            "apps.API.services.auditoria_service.auditoria_repository.get_all",
            new=get_all_mock,
        ),
        patch(
            "apps.API.services.auditoria_service.auditoria_repository.count",
            new=count_mock,
        ),
    ):
        result = await list_auditoria(
            session,
            id_usuario=5,
            recurso="EMPLEADO",
            operacion="UPDATE",
            fecha_desde=date(2026, 7, 1),
            fecha_hasta=date(2026, 8, 1),
            limit=10,
            offset=5,
        )

    call_kwargs = get_all_mock.call_args[1]
    assert call_kwargs["id_usuario"] == 5
    assert call_kwargs["recurso"] == "EMPLEADO"
    assert call_kwargs["operacion"] == "UPDATE"
    assert call_kwargs["fecha_desde"] == date(2026, 7, 1)
    assert call_kwargs["fecha_hasta"] == date(2026, 8, 1)
    assert call_kwargs["limit"] == 10
    assert call_kwargs["offset"] == 5

    count_kwargs = count_mock.call_args[1]
    assert count_kwargs["id_usuario"] == 5
    assert count_kwargs["recurso"] == "EMPLEADO"
    assert result.total == 1


async def test_list_auditoria_response_fields(session):
    record = _FakeAuditoria(
        id=10,
        id_usuario=3,
        recurso="SEDE",
        id_recurso="7",
        operacion="DELETE",
        valor_anterior={"nombre": "Sede A"},
        valor_nuevo=None,
        ip_address="10.0.0.1",
        detalle="Desactivacion de sede",
    )
    mocks = _patches(records=[record], total=1)
    with mocks["get_all"], mocks["count"]:
        result = await list_auditoria(session)

    item = result.items[0]
    assert item.id == 10
    assert item.id_usuario == 3
    assert item.recurso == "SEDE"
    assert item.id_recurso == "7"
    assert item.operacion == "DELETE"
    assert item.valor_anterior == {"nombre": "Sede A"}
    assert item.valor_nuevo is None
    assert item.ip_address == "10.0.0.1"
    assert item.detalle == "Desactivacion de sede"


async def test_list_auditoria_default_pagination(session):
    get_all_mock = AsyncMock(return_value=[])
    count_mock = AsyncMock(return_value=0)
    with (
        patch(
            "apps.API.services.auditoria_service.auditoria_repository.get_all",
            new=get_all_mock,
        ),
        patch(
            "apps.API.services.auditoria_service.auditoria_repository.count",
            new=count_mock,
        ),
    ):
        await list_auditoria(session)

    call_kwargs = get_all_mock.call_args[1]
    assert call_kwargs["limit"] == 50
    assert call_kwargs["offset"] == 0

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.models.cat_cargo import CatCargo
from apps.API.models.cat_novedad import CatNovedad
from apps.API.models.cat_tipo_documento import CatTipoDocumento
from apps.API.repositories import auditoria_repository
from apps.API.utils.request import extract_ip
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria

router = APIRouter(prefix="/catalogos", tags=["catalogos"])


class TipoCatalogo(StrEnum):
    CARGOS = "cargos"
    DOCUMENTOS = "documentos"
    MOTIVOS = "motivos"


_MODELOS = {
    TipoCatalogo.CARGOS: CatCargo,
    TipoCatalogo.DOCUMENTOS: CatTipoDocumento,
    TipoCatalogo.MOTIVOS: CatNovedad,
}


class ItemCatalogoResponse(BaseModel):
    id: int
    catalogo: str
    codigo: str
    nombre: str
    descripcion: str | None
    activo: bool
    created_at: datetime
    updated_at: datetime


class ItemCatalogoCreateRequest(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=30)
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str | None = Field(None, max_length=255)


class ItemCatalogoUpdateRequest(BaseModel):
    codigo: str | None = Field(None, min_length=1, max_length=30)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    descripcion: str | None = Field(None, max_length=255)
    activo: bool | None = None


def _to_response(item: Any, catalogo: str) -> ItemCatalogoResponse:
    return ItemCatalogoResponse(
        id=item.id,
        catalogo=catalogo,
        codigo=item.codigo,
        nombre=item.nombre,
        descripcion=item.descripcion,
        activo=item.id_estado == 1,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/{tipo}", response_model=list[ItemCatalogoResponse])
async def listar_catalogo(
    tipo: TipoCatalogo = Path(...),
    session: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_permission("CATALOGOS", "leer")),
) -> list[ItemCatalogoResponse]:
    modelo = _MODELOS[tipo]
    stmt = select(modelo).where(modelo.id_estado == 1).order_by(modelo.id)
    result = await session.execute(stmt)
    items: Sequence = result.scalars().all()
    return [_to_response(item, tipo.value) for item in items]


@router.post(
    "/{tipo}",
    response_model=ItemCatalogoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_item_catalogo(
    payload: ItemCatalogoCreateRequest,
    request: Request,
    tipo: TipoCatalogo = Path(...),
    session: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_permission("CATALOGOS", "escribir")),
) -> ItemCatalogoResponse:
    modelo = _MODELOS[tipo]
    codigo = payload.codigo.strip().upper()

    existing = await session.execute(
        select(modelo).where(modelo.codigo == codigo)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Ya existe un item con código '{codigo}'.")

    item = modelo(
        codigo=codigo,
        nombre=payload.nombre.strip(),
        id_estado=1,
        descripcion=payload.descripcion,
    )
    session.add(item)
    await session.flush()

    await auditoria_repository.create(
        session,
        id_usuario=int(_user["sub"]),
        recurso=RecursoAuditoria.CATALOGO,
        id_recurso=str(item.id),
        operacion=OperacionAuditoria.INSERT,
        ip_address=extract_ip(request),
        detalle=f"Creado {tipo.value}: {item.nombre}",
        valor_nuevo={"codigo": item.codigo, "nombre": item.nombre, "descripcion": item.descripcion},
        timestamp_accion=tz_now(),
    )

    return _to_response(item, tipo.value)


@router.put(
    "/{tipo}/{item_id}",
    response_model=ItemCatalogoResponse,
)
async def actualizar_item_catalogo(
    item_id: int,
    payload: ItemCatalogoUpdateRequest,
    request: Request,
    tipo: TipoCatalogo = Path(...),
    session: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_permission("CATALOGOS", "escribir")),
) -> ItemCatalogoResponse:
    modelo = _MODELOS[tipo]

    result = await session.execute(select(modelo).where(modelo.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item no encontrado.")

    anterior = {"codigo": item.codigo, "nombre": item.nombre, "descripcion": item.descripcion, "activo": item.id_estado == 1}

    values: dict = {}
    if payload.codigo is not None:
        codigo = payload.codigo.strip().upper()
        if codigo != item.codigo:
            dup = await session.execute(
                select(modelo).where(modelo.codigo == codigo).where(modelo.id != item_id)
            )
            if dup.scalar_one_or_none() is not None:
                raise HTTPException(status.HTTP_409_CONFLICT, f"Ya existe un item con código '{codigo}'.")
            values["codigo"] = codigo
    if payload.nombre is not None:
        values["nombre"] = payload.nombre.strip()
    if payload.descripcion is not None:
        values["descripcion"] = payload.descripcion
    if payload.activo is not None:
        values["id_estado"] = 1 if payload.activo else 2

    if values:
        stmt = update(modelo).where(modelo.id == item_id).values(**values)
        await session.execute(stmt)
        await session.flush()

    result2 = await session.execute(select(modelo).where(modelo.id == item_id))
    updated = result2.scalar_one()

    if values:
        nuevo = {"codigo": updated.codigo, "nombre": updated.nombre, "descripcion": updated.descripcion, "activo": updated.id_estado == 1}
        await auditoria_repository.create(
            session,
            id_usuario=int(_user["sub"]),
            recurso=RecursoAuditoria.CATALOGO,
            id_recurso=str(item_id),
            operacion=OperacionAuditoria.UPDATE,
            ip_address=extract_ip(request),
            detalle=f"Actualizado {tipo.value}: {updated.nombre}",
            valor_anterior=anterior,
            valor_nuevo=nuevo,
            timestamp_accion=tz_now(),
        )

    return _to_response(updated, tipo.value)


@router.delete("/{tipo}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_item_catalogo(
    item_id: int,
    request: Request,
    tipo: TipoCatalogo = Path(...),
    session: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_permission("CATALOGOS", "escribir")),
) -> None:
    modelo = _MODELOS[tipo]
    result = await session.execute(select(modelo).where(modelo.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item no encontrado.")

    values = {"id_estado": 2}
    stmt = update(modelo).where(modelo.id == item_id).values(**values)
    await session.execute(stmt)

    await auditoria_repository.create(
        session,
        id_usuario=int(_user["sub"]),
        recurso=RecursoAuditoria.CATALOGO,
        id_recurso=str(item_id),
        operacion=OperacionAuditoria.DELETE,
        ip_address=extract_ip(request),
        detalle=f"Eliminado {tipo.value}: {item.nombre}",
        valor_anterior={"codigo": item.codigo, "nombre": item.nombre},
        timestamp_accion=tz_now(),
    )

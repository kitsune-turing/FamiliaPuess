from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.config_general import ConfigGeneral
from shared.exceptions.configuration import ConfiguracionNoEncontradaError


async def get_many(session: AsyncSession, claves: list[str]) -> dict[str, str]:
    stmt = select(ConfigGeneral.clave, ConfigGeneral.valor).where(
        ConfigGeneral.clave.in_(claves)
    )
    result = await session.execute(stmt)
    return dict(result.all())


async def get_valor(session: AsyncSession, clave: str) -> str:
    stmt = select(ConfigGeneral.valor).where(ConfigGeneral.clave == clave)
    result = await session.execute(stmt)
    valor = result.scalar_one_or_none()
    if valor is None:
        raise ConfiguracionNoEncontradaError(clave)
    return valor


async def get_valor_or_none(session: AsyncSession, clave: str) -> str | None:
    stmt = select(ConfigGeneral.valor).where(ConfigGeneral.clave == clave)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def upsert(
    session: AsyncSession,
    *,
    clave: str,
    valor: str,
    categoria: str = "SISTEMA",
    tipo_dato: str = "STRING",
    descripcion: str | None = None,
    updated_by: int | None = None,
    now: datetime | None = None,
) -> None:
    stmt = select(ConfigGeneral).where(ConfigGeneral.clave == clave)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        values: dict = {"valor": valor}
        if updated_by is not None:
            values["updated_by"] = updated_by
        if now is not None:
            values["updated_at"] = now
        stmt_update = (
            update(ConfigGeneral)
            .where(ConfigGeneral.clave == clave)
            .values(**values)
        )
        await session.execute(stmt_update)
    else:
        config = ConfigGeneral(
            categoria=categoria,
            clave=clave,
            valor=valor,
            tipo_dato=tipo_dato,
            descripcion=descripcion,
            updated_by=updated_by,
        )
        if now is not None:
            config.updated_at = now
        session.add(config)
        await session.flush()

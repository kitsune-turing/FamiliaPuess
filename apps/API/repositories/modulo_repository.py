from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.modulo import Modulo


async def get_by_id(session: AsyncSession, modulo_id: int) -> Modulo | None:
    stmt = select(Modulo).where(Modulo.id == modulo_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_codigo(session: AsyncSession, codigo: str) -> Modulo | None:
    stmt = select(Modulo).where(Modulo.codigo == codigo)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(session: AsyncSession) -> list[Modulo]:
    stmt = select(Modulo).order_by(Modulo.nombre)
    result = await session.execute(stmt)
    return list(result.scalars().all())

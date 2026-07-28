from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.dispositivo import Dispositivo


async def get_by_identificador(session: AsyncSession, identificador: str) -> Dispositivo | None:
    stmt = select(Dispositivo).where(Dispositivo.identificador == identificador)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def count_by_estado(session: AsyncSession, id_estado: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Dispositivo)
        .where(Dispositivo.id_estado == id_estado)
    )
    result = await session.execute(stmt)
    return result.scalar_one()

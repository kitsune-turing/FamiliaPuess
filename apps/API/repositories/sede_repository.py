from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.sede import Sede


async def count_by_estado(session: AsyncSession, id_estado: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Sede)
        .where(Sede.id_estado == id_estado)
    )
    result = await session.execute(stmt)
    return result.scalar_one()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.cat_novedad import CatNovedad


async def get_by_codigo(session: AsyncSession, codigo: str) -> CatNovedad | None:
    stmt = select(CatNovedad).where(CatNovedad.codigo == codigo)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

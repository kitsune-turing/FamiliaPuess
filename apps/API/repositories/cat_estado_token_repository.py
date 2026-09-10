from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.cat_estado_token import CatEstadoToken
from shared.exceptions.catalog import EstadoNoEncontradoError


async def get_estado_token_id(session: AsyncSession, codigo: str) -> int:
    stmt = select(CatEstadoToken.id).where(CatEstadoToken.codigo == codigo)
    result = await session.execute(stmt)
    estado_id = result.scalar_one_or_none()
    if estado_id is None:
        raise EstadoNoEncontradoError(codigo)
    return estado_id

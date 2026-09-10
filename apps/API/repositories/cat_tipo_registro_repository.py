from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.cat_tipo_registro import CatTipoRegistro


async def get_tipo_registro_id(session: AsyncSession, codigo: str) -> int:
    stmt = select(CatTipoRegistro.id).where(CatTipoRegistro.codigo == codigo)
    result = await session.execute(stmt)
    tipo_id = result.scalar_one_or_none()
    if tipo_id is None:
        raise ValueError(f"Tipo de registro '{codigo}' no encontrado en catalogo")
    return tipo_id

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.config_general import ConfigGeneral
from shared.exceptions.configuration import ConfiguracionNoEncontradaError


async def get_valor(session: AsyncSession, clave: str) -> str:
    stmt = select(ConfigGeneral.valor).where(ConfigGeneral.clave == clave)
    result = await session.execute(stmt)
    valor = result.scalar_one_or_none()
    if valor is None:
        raise ConfiguracionNoEncontradaError(clave)
    return valor

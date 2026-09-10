from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.token_qr import TokenQR


async def create(
    session: AsyncSession,
    *,
    id_dispositivo: int,
    id_estado_token: int,
    token: str,
    codigo_alfa: str,
    generado_en: datetime,
    expira_en: datetime,
) -> TokenQR:
    token_qr = TokenQR(
        id_dispositivo=id_dispositivo,
        id_estado_token=id_estado_token,
        token=token,
        codigo_alfa=codigo_alfa,
        generado_en=generado_en,
        expira_en=expira_en,
    )
    session.add(token_qr)
    await session.flush()
    return token_qr


async def get_by_token(session: AsyncSession, token_value: str) -> TokenQR | None:
    stmt = select(TokenQR).where(TokenQR.token == token_value)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def mark_consumed(
    session: AsyncSession,
    *,
    token_id: int,
    id_estado_consumido: int,
    consumido_en: datetime,
) -> None:
    stmt = (
        update(TokenQR)
        .where(TokenQR.id == token_id)
        .values(id_estado_token=id_estado_consumido, consumido_en=consumido_en)
    )
    await session.execute(stmt)


async def try_consume_atomically(
    session: AsyncSession,
    *,
    token_id: int,
    id_estado_activo: int,
    id_estado_consumido: int,
    consumido_en: datetime,
    expira_en_min: datetime,
) -> bool:
    """Atomically consume a token only if it is still active and not expired.

    Returns True if the token was consumed, False if it was already consumed
    or expired (race condition / concurrent request).
    """
    stmt = (
        update(TokenQR)
        .where(
            TokenQR.id == token_id,
            TokenQR.id_estado_token == id_estado_activo,
            TokenQR.expira_en >= expira_en_min,
        )
        .values(id_estado_token=id_estado_consumido, consumido_en=consumido_en)
    )
    result = await session.execute(stmt)
    return result.rowcount > 0

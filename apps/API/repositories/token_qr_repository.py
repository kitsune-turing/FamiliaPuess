from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.token_qr import TokenQR


async def create(
    session: AsyncSession,
    *,
    id_sede: int,
    id_dispositivo: int,
    id_estado_token: int,
    token: str,
    codigo_alfa: str,
    generado_en: datetime,
    expira_en: datetime,
) -> TokenQR:
    token_qr = TokenQR(
        id_sede=id_sede,
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

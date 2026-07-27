from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base


class TokenQR(Base):
    __tablename__ = "token_qr"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sede: Mapped[int] = mapped_column(ForeignKey("sede.id"), nullable=False)
    id_dispositivo: Mapped[int] = mapped_column(ForeignKey("dispositivo.id"), nullable=False)
    id_estado_token: Mapped[int] = mapped_column(
        ForeignKey("cat_estado_token.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    codigo_alfa: Mapped[str] = mapped_column(String(20), nullable=False)
    generado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumido_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ip_generacion: Mapped[str | None] = mapped_column(INET)

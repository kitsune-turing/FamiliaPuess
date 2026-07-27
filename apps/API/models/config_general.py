from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.API.models.base import Base


class ConfigGeneral(Base):
    __tablename__ = "config_general"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria: Mapped[str] = mapped_column(String(30), nullable=False, default="SISTEMA")
    clave: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_dato: Mapped[str] = mapped_column(String(20), nullable=False, default="STRING")
    descripcion: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_by: Mapped[int | None] = mapped_column()

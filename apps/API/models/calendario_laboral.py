from datetime import date, datetime

from sqlalchemy import CheckConstraint, Computed, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base


class CalendarioLaboral(Base):
    """Días no laborables almacenados en la base de datos v2.2."""

    __tablename__ = "calendario_laboral"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('FESTIVO', 'DOMINGO', 'CIERRE_EMPRESA')",
            name="ck_calendario_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    anio: Mapped[int] = mapped_column(
        Integer,
        Computed("EXTRACT(YEAR FROM fecha)::INTEGER", persisted=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

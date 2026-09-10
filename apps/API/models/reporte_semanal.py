from datetime import date, datetime

from sqlalchemy import Date, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base


class ReporteSemanal(Base):
    __tablename__ = "reporte_semanal"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    total_registros: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_novedades: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "fecha_inicio", "fecha_fin", name="uq_reporte_semanal_periodo"
        ),
    )

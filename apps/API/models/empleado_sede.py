from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base


class EmpleadoSede(Base):
    """Historial de asignaciones de sede definido por el esquema v2.2."""

    __tablename__ = "empleado_sede"
    __table_args__ = (
        CheckConstraint(
            "fecha_fin IS NULL OR fecha_fin >= fecha_inicio",
            name="ck_emp_sede_vigencia",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_empleado: Mapped[int] = mapped_column(ForeignKey("empleado.id"), nullable=False)
    id_sede: Mapped[int] = mapped_column(ForeignKey("sede.id"), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

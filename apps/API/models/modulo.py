from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from apps.API.models.base import Base


class Modulo(Base):
    __tablename__ = "modulo"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255))

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.API.models.base import Base
from apps.API.models.modulo import Modulo


class PermisoRol(Base):
    __tablename__ = "permiso_rol"
    __table_args__ = (UniqueConstraint("id_rol", "id_modulo", name="uq_permiso_rol_modulo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    id_rol: Mapped[int] = mapped_column(ForeignKey("cat_rol.id", ondelete="CASCADE"), nullable=False)
    id_modulo: Mapped[int] = mapped_column(ForeignKey("modulo.id", ondelete="CASCADE"), nullable=False)
    puede_leer: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    puede_escribir: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    puede_eliminar: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    puede_administrar: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    modulo: Mapped[Modulo] = relationship(lazy="joined")

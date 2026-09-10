class RolNoEncontradoError(Exception):
    def __init__(self, rol_id: int) -> None:
        self.rol_id = rol_id
        super().__init__(f"Rol con id {rol_id} no encontrado")


class RolCodigoDuplicadoError(Exception):
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(f"Ya existe un rol con el codigo '{codigo}'")


class RolProtegidoError(Exception):
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(f"El rol '{codigo}' es un rol del sistema y no puede eliminarse")


class RolTieneUsuariosError(Exception):
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(
            f"El rol '{codigo}' tiene usuarios asignados y no puede desactivarse"
        )

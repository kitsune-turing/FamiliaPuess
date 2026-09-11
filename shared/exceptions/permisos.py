class PermisoNoEncontradoError(Exception):
    def __init__(self, permiso_id: int) -> None:
        self.permiso_id = permiso_id
        super().__init__(f"Permiso con id {permiso_id} no encontrado")


class PermisoDuplicadoError(Exception):
    def __init__(self, rol_id: int, modulo_codigo: str) -> None:
        self.rol_id = rol_id
        self.modulo_codigo = modulo_codigo
        super().__init__(
            f"Ya existe un permiso para el rol {rol_id} en el modulo '{modulo_codigo}'"
        )


class ModuloNoEncontradoError(Exception):
    def __init__(self, modulo_id: int) -> None:
        self.modulo_id = modulo_id
        super().__init__(f"Modulo con id {modulo_id} no encontrado")

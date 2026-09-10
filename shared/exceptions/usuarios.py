class UsuarioNoEncontradoError(Exception):
    def __init__(self, usuario_id: int) -> None:
        self.usuario_id = usuario_id
        super().__init__(f"Usuario con id {usuario_id} no encontrado")


class CorreoDuplicadoError(Exception):
    def __init__(self, correo: str) -> None:
        self.correo = correo
        super().__init__(f"Ya existe un usuario con el correo '{correo}'")


class UsernameDuplicadoError(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Ya existe un usuario con el username '{username}'")


class UltimoSuperAdminError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No se puede desactivar el unico Super Usuario activo del sistema"
        )


class AutoDesactivacionError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Ha desactivado su propia cuenta. Su sesion ha sido cerrada"
        )


class RolInactivoError(Exception):
    def __init__(self, rol_id: int) -> None:
        self.rol_id = rol_id
        super().__init__(f"El rol con id {rol_id} se encuentra inactivo")

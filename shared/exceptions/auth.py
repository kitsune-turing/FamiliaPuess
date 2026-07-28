class CredencialesInvalidasError(Exception):
    def __init__(self) -> None:
        super().__init__("Usuario o contrasena incorrectos")


class UsuarioInactivoError(Exception):
    def __init__(self) -> None:
        super().__init__("La cuenta de usuario se encuentra inactiva")


class CuentaBloqueadaError(Exception):
    def __init__(self, minutos_restantes: int) -> None:
        self.minutos_restantes = minutos_restantes
        super().__init__(
            f"Cuenta bloqueada por intentos fallidos. Intente en {minutos_restantes} minutos"
        )


class SesionExistenteError(Exception):
    def __init__(self) -> None:
        super().__init__("Ya existe una sesion activa para este usuario")


class TokenInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__("Token de acceso invalido o expirado")


class RefreshTokenInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__("Refresh token invalido o expirado")


class SesionNoEncontradaError(Exception):
    def __init__(self) -> None:
        super().__init__("Sesion no encontrada o ya finalizada")


class PermisoInsuficienteError(Exception):
    def __init__(self, modulo: str, operacion: str) -> None:
        self.modulo = modulo
        self.operacion = operacion
        super().__init__(
            f"Permiso insuficiente para '{operacion}' en modulo '{modulo}'"
        )


class CambioContrasenaRequeridoError(Exception):
    def __init__(self) -> None:
        super().__init__("Debe cambiar su contrasena antes de continuar")

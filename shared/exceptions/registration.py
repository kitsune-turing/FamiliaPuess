class TokenNoEncontradoError(Exception):
    def __init__(self) -> None:
        super().__init__("El codigo QR no es valido")


class TokenFormatoInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__("El codigo QR no es valido")


class TokenExpiradoError(Exception):
    def __init__(self) -> None:
        super().__init__("El codigo QR ha expirado. Escanee nuevamente el codigo QR")


class TokenConsumidoError(Exception):
    def __init__(self) -> None:
        super().__init__("El codigo QR ya fue utilizado. Escanee nuevamente el codigo QR")


class SedeNoDisponibleError(Exception):
    def __init__(self) -> None:
        super().__init__("El punto de control no se encuentra disponible")


class CodigoAlfaInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__("El codigo alfanumerico es invalido")


class DispositivoTokenNoAutorizadoError(Exception):
    def __init__(self) -> None:
        super().__init__("El dispositivo no esta autorizado para esta sede")

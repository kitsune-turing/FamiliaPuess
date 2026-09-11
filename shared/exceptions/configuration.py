class ConfiguracionNoEncontradaError(Exception):
    def __init__(self, clave: str) -> None:
        self.clave = clave
        super().__init__(f"Parametro de configuracion '{clave}' no existe en config_general")


class SetupIncompletoError(Exception):
    def __init__(self, pasos_pendientes: str) -> None:
        self.pasos_pendientes = pasos_pendientes
        super().__init__(
            f"No se puede completar el setup. Pasos pendientes: {pasos_pendientes}"
        )

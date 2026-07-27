class ConfiguracionNoEncontradaError(Exception):
    def __init__(self, clave: str) -> None:
        self.clave = clave
        super().__init__(f"Parametro de configuracion '{clave}' no existe en config_general")

class EstadoNoEncontradoError(Exception):
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(f"Estado con codigo '{codigo}' no existe en cat_estado")

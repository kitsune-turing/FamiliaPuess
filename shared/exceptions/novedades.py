class NovedadNoEncontradaError(Exception):
    def __init__(self, novedad_id: int) -> None:
        self.novedad_id = novedad_id
        super().__init__(f"La novedad con id {novedad_id} no existe")


class TipoNovedadNoEncontradoError(Exception):
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        super().__init__(f"El tipo de novedad '{codigo}' no existe")


class SedesSinHorarioError(Exception):
    def __init__(self, id_sede: int) -> None:
        self.id_sede = id_sede
        super().__init__(
            f"La sede {id_sede} no tiene un horario configurado para la fecha indicada"
        )

class HorarioNoEncontradoError(Exception):
    def __init__(self, horario_id: int) -> None:
        self.horario_id = horario_id
        super().__init__(f"El horario con id {horario_id} no existe")


class HorarioVigenciaInvalidaError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "La fecha vigente_hasta debe ser igual o posterior a vigente_desde"
        )


class HorarioToleranciaInvalidaError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "La tolerancia debe ser un valor entre 0 y 120 minutos"
        )


class HorarioHoraEntradaInvalidaError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "La hora de entrada tiene un formato invalido"
        )


class HorarioSolapamientoError(Exception):
    def __init__(self, id_sede: int) -> None:
        self.id_sede = id_sede
        super().__init__(
            f"Ya existe un horario vigente para la sede {id_sede} en el periodo indicado"
        )


class HorarioInmutableError(Exception):
    def __init__(self, horario_id: int) -> None:
        self.horario_id = horario_id
        super().__init__(
            f"El horario con id {horario_id} no puede ser modificado porque ya no esta vigente"
        )

import secrets
import string

from shared.constants.codigo_formato import CodigoFormato

_CHARSETS = {
    CodigoFormato.NUMERICO: string.digits,
    CodigoFormato.ALFABETICO: string.ascii_uppercase,
    CodigoFormato.ALFANUMERICO: string.ascii_uppercase + string.digits,
}


def generate_codigo(formato: str, longitud: int) -> str:
    charset = _CHARSETS.get(formato)
    if charset is None:
        raise ValueError(f"Formato de codigo no soportado: {formato}")
    return "".join(secrets.choice(charset) for _ in range(longitud))

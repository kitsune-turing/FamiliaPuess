import string

import pytest

from apps.API.utils.codigo_generator import generate_codigo
from shared.constants.codigo_formato import CodigoFormato


@pytest.mark.parametrize(
    ("formato", "allowed_charset"),
    [
        (CodigoFormato.NUMERICO, string.digits),
        (CodigoFormato.ALFABETICO, string.ascii_uppercase),
        (CodigoFormato.ALFANUMERICO, string.ascii_uppercase + string.digits),
    ],
)
def test_generate_codigo_respects_length_and_charset(formato, allowed_charset):
    codigo = generate_codigo(formato, 6)

    assert len(codigo) == 6
    assert all(char in allowed_charset for char in codigo)


def test_generate_codigo_rejects_unsupported_formato():
    with pytest.raises(ValueError):
        generate_codigo("FORMATO_DESCONOCIDO", 6)


def test_generate_codigo_is_not_deterministic():
    codigos = {generate_codigo(CodigoFormato.ALFANUMERICO, 8) for _ in range(20)}

    assert len(codigos) == 20

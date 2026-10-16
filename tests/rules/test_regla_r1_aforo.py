import pytest

from app.core.errors import AforoExcedido
from app.rules import validar_aforo


def test_aforo_valido_menor_que_maximo():
    # Asistentes menor que aforo máximo es totalmente válido
    validar_aforo(asistentes=15, aforo_maximo=20, nombre_sala="Sala Beta")


def test_aforo_valido_limite_exacto():
    # Asistentes exactamente igual al aforo máximo es válido
    validar_aforo(asistentes=25, aforo_maximo=25, nombre_sala="Sala Cosmos Test")


def test_aforo_invalido_excedido_por_uno():
    with pytest.raises(AforoExcedido) as exc_info:
        validar_aforo(asistentes=21, aforo_maximo=20, nombre_sala="Sala Beta")

    error = exc_info.value
    assert error.codigo == "AFORO_EXCEDIDO"
    assert error.status_code == 422
    assert "Sala Beta" in error.mensaje
    assert "20" in error.mensaje
    assert "21" in error.mensaje


def test_aforo_invalido_muy_excedido():
    with pytest.raises(AforoExcedido) as exc_info:
        validar_aforo(asistentes=100, aforo_maximo=10, nombre_sala="Sala Mini")

    error = exc_info.value
    assert error.codigo == "AFORO_EXCEDIDO"
    assert error.status_code == 422
    assert "La sala Sala Mini admite 10 personas y se pidieron 100." == error.mensaje

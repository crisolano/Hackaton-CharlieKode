import pytest

from app.core.config import _numero_env


def test_lee_enteros_y_decimales(monkeypatch):
    monkeypatch.setenv("VARIABLE_DE_PRUEBA", "3")
    assert _numero_env("VARIABLE_DE_PRUEBA", "1") == 3
    monkeypatch.setenv("VARIABLE_DE_PRUEBA", "0.25")
    assert _numero_env("VARIABLE_DE_PRUEBA", "1", float) == 0.25


def test_sin_variable_usa_el_valor_por_defecto(monkeypatch):
    monkeypatch.delenv("VARIABLE_DE_PRUEBA", raising=False)
    assert _numero_env("VARIABLE_DE_PRUEBA", "7") == 7


@pytest.mark.parametrize(("valor", "tipo"), [("diez", int), ("1.5", int), ("abc", float)])
def test_un_valor_no_numerico_falla_nombrando_la_variable(monkeypatch, valor, tipo):
    monkeypatch.setenv("VARIABLE_DE_PRUEBA", valor)

    with pytest.raises(ValueError, match="VARIABLE_DE_PRUEBA"):
        _numero_env("VARIABLE_DE_PRUEBA", "1", tipo)

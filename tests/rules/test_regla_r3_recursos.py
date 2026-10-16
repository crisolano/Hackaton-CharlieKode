import pytest

from app.core.config import EquipoEstado, SalaEstado
from app.core.errors import RecursoNoDisponible
from app.rules.recursos import validar_equipo_disponible, validar_sala_disponible


def test_validar_sala_disponible_activa_ok():
    # No debe levantar ninguna excepción
    validar_sala_disponible(sala_id=1, estado=SalaEstado.ACTIVA.value)


def test_validar_sala_disponible_inhabilitada_falla():
    with pytest.raises(RecursoNoDisponible) as exc_info:
        validar_sala_disponible(sala_id=42, estado=SalaEstado.INHABILITADA.value)
    
    assert exc_info.value.codigo == "RECURSO_NO_DISPONIBLE"
    assert "sala" in exc_info.value.mensaje.lower()
    assert exc_info.value.detalles == {"estado": SalaEstado.INHABILITADA.value}


def test_validar_equipo_disponible_ok():
    # No debe levantar ninguna excepción
    validar_equipo_disponible(equipo_id=10, estado=EquipoEstado.DISPONIBLE.value)


@pytest.mark.parametrize(
    "estado_no_disponible",
    [
        EquipoEstado.PRESTADO.value,
        EquipoEstado.DANADO.value,
        EquipoEstado.INHABILITADO.value,
    ],
)
def test_validar_equipo_no_disponible_falla(estado_no_disponible):
    with pytest.raises(RecursoNoDisponible) as exc_info:
        validar_equipo_disponible(equipo_id=10, estado=estado_no_disponible)
    
    assert exc_info.value.codigo == "RECURSO_NO_DISPONIBLE"
    assert "equipo" in exc_info.value.mensaje.lower()
    assert exc_info.value.detalles == {"estado": estado_no_disponible}

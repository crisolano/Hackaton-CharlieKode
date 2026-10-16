from collections.abc import Sequence
from dataclasses import dataclass

import pytest
from sqlalchemy.orm import Session

from app.ai.base import AIClient, AIError
from app.core.config import (
    IncidenciaCategoria,
    IncidenciaEstado,
    IncidenciaPrioridad,
    IncidenciaRuta,
)
from app.core.errors import DatosInvalidos, NoEncontrado
from app.models import Incidencia
from app.schemas import IncidenciaCreate
from app.services.incidencias import (
    actualizar_estado_incidencia,
    crear_incidencia,
    listar_incidencias,
    obtener_incidencia,
)


@dataclass
class TriajeFalso:
    categoria: str = IncidenciaCategoria.HARDWARE.value
    prioridad: str = IncidenciaPrioridad.MEDIA.value
    ruta: str = IncidenciaRuta.SOPORTE_TECNICO.value
    estado: str = IncidenciaEstado.CLASIFICADA.value
    origen_ia: bool = True


class MockAIClientExitoso(AIClient):
    def generate(self, prompt: str) -> str:
        return '{"categoria": "hardware", "prioridad": "media", "ruta": "soporte_tecnico"}'


class MockAIClientConFallo(AIClient):
    def generate(self, prompt: str) -> str:
        raise AIError("Timeout de conexión con el proveedor")


def test_crear_incidencia_sin_ia(db: Session):
    datos = IncidenciaCreate(texto="Se dañó el tomacorriente en Cosmos")
    incidencia = crear_incidencia(db, datos)

    assert incidencia.id is not None
    assert incidencia.texto == "Se dañó el tomacorriente en Cosmos"
    assert incidencia.estado == IncidenciaEstado.PENDIENTE_REVISION.value
    assert incidencia.origen_ia is False
    assert incidencia.categoria is None
    assert incidencia.prioridad is None
    assert incidencia.ruta is None


def test_crear_incidencia_texto_vacio(db: Session):
    with pytest.raises(DatosInvalidos):
        crear_incidencia(db, IncidenciaCreate(texto="   "))


def test_crear_incidencia_con_ia_cuando_falla_queda_pendiente(db: Session):
    datos = IncidenciaCreate(texto="No hay señal de wifi en Apolo")
    cliente_fallido = MockAIClientConFallo()

    # Aunque la IA falle o lance timeout, la incidencia debe guardarse
    # como 'pendiente_revision' sin propagar error al usuario ni inventar datos
    incidencia = crear_incidencia(db, datos, ai_client=cliente_fallido)

    assert incidencia.id is not None
    assert incidencia.estado == IncidenciaEstado.PENDIENTE_REVISION.value
    assert incidencia.origen_ia is False
    assert incidencia.categoria is None


def test_crear_incidencia_con_modulo_triage_simulado(monkeypatch, db: Session):
    datos = IncidenciaCreate(texto="El proyector parpadea")
    cliente_ok = MockAIClientExitoso()

    # Simulamos el módulo app.ai.triage
    import sys
    import types
    fake_triage_module = types.ModuleType("app.ai.triage")
    fake_triage_module.triar_incidencia = lambda texto, ai_client: TriajeFalso()
    monkeypatch.setitem(sys.modules, "app.ai.triage", fake_triage_module)

    incidencia = crear_incidencia(db, datos, ai_client=cliente_ok)

    assert incidencia.estado == IncidenciaEstado.CLASIFICADA.value
    assert incidencia.origen_ia is True
    assert incidencia.categoria == IncidenciaCategoria.HARDWARE.value
    assert incidencia.prioridad == IncidenciaPrioridad.MEDIA.value
    assert incidencia.ruta == IncidenciaRuta.SOPORTE_TECNICO.value


def test_obtener_incidencia_y_no_encontrado(db: Session):
    inc = Incidencia(texto="Fuga de agua en el baño")
    db.add(inc)
    db.commit()
    db.refresh(inc)

    recuperada = obtener_incidencia(db, inc.id)
    assert recuperada.texto == "Fuga de agua en el baño"

    with pytest.raises(NoEncontrado):
        obtener_incidencia(db, 99999)


def test_listar_incidencias_con_filtros(db: Session):
    inc1 = Incidencia(
        texto="Texto 1",
        categoria=IncidenciaCategoria.RED.value,
        estado=IncidenciaEstado.CLASIFICADA.value,
    )
    inc2 = Incidencia(
        texto="Texto 2",
        categoria=IncidenciaCategoria.MOBILIARIO.value,
        estado=IncidenciaEstado.EN_PROCESO.value,
    )
    inc3 = Incidencia(
        texto="Texto 3",
        categoria=IncidenciaCategoria.RED.value,
        estado=IncidenciaEstado.PENDIENTE_REVISION.value,
    )
    db.add_all([inc1, inc2, inc3])
    db.commit()

    todas: Sequence[Incidencia] = listar_incidencias(db)
    assert len(todas) == 3

    filtradas_red = listar_incidencias(db, categoria=IncidenciaCategoria.RED.value)
    assert len(filtradas_red) == 2

    filtradas_proceso = listar_incidencias(db, estado=IncidenciaEstado.EN_PROCESO.value)
    assert len(filtradas_proceso) == 1
    assert filtradas_proceso[0].texto == "Texto 2"


def test_actualizar_estado_incidencia(db: Session):
    inc = Incidencia(texto="Puerta bloqueada")
    db.add(inc)
    db.commit()
    db.refresh(inc)

    actualizada = actualizar_estado_incidencia(
        db, inc.id, nuevo_estado=IncidenciaEstado.EN_PROCESO.value
    )
    assert actualizada.estado == IncidenciaEstado.EN_PROCESO.value

    with pytest.raises(DatosInvalidos):
        actualizar_estado_incidencia(db, inc.id, nuevo_estado="estado_invalido_inventado")

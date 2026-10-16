import logging

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import engine, get_db
from app.main import app


def test_el_engine_de_la_app_oculta_los_parametros_sql():
    assert engine.hide_parameters is True


def test_un_error_de_bd_no_filtra_el_texto_de_la_incidencia_al_log(caplog):
    """Base sin tablas: el 500 se registra, pero sin los valores enviados por el usuario."""
    vacia = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        hide_parameters=True,
    )
    sesion = sessionmaker(bind=vacia)()
    app.dependency_overrides[get_db] = lambda: sesion
    try:
        with caplog.at_level(logging.ERROR, logger="app.core.errors"):
            response = TestClient(app, raise_server_exceptions=False).post(
                "/api/incidencias", json={"texto": "dato-personal-de-prueba"}
            )
    finally:
        app.dependency_overrides.clear()
        sesion.close()

    assert response.status_code == 500
    assert response.json()["codigo"] == "ERROR_INTERNO"
    assert "Error no controlado" in caplog.text
    assert "dato-personal-de-prueba" not in caplog.text
    assert "dato-personal-de-prueba" not in response.text

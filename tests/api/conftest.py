from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.models import Sala


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """Cliente de la app real con la sesión de BD en memoria del fixture `db`."""
    app.dependency_overrides[get_db] = lambda: db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def sala(db: Session) -> Sala:
    """Sala de pruebas; los datos de negocio de la app vienen del seed, no del código."""
    sala = Sala(nombre="Sala de prueba", aforo=20)
    db.add(sala)
    db.commit()
    db.refresh(sala)
    return sala


@pytest.fixture(autouse=True)
def _reiniciar_limitador():
    from app.api.deps import limitador_incidencias

    limitador_incidencias.reiniciar()

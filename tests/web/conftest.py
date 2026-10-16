import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models import Sala

HTMX = {"HX-Request": "true"}


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def salas_de_prueba(db):
    salas = [Sala(nombre="Sala Uno", aforo=10), Sala(nombre="Sala Dos", aforo=40)]
    db.add_all(salas)
    db.commit()
    return salas


@pytest.fixture
def client_sin_tablas():
    """Cliente cuya base no tiene tablas (BD sin inicializar)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    sesion = sessionmaker(bind=engine)()
    app.dependency_overrides[get_db] = lambda: sesion
    yield TestClient(app)
    app.dependency_overrides.clear()
    sesion.close()

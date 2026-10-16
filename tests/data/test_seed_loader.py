import json
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.data.loader import cargar_salas_dataset
from app.data.seed import RUTA_DATASET_DEFAULT, main, seed_salas
from app.models import Sala


def test_cargar_dataset_oficial():
    """Valida que el archivo oficial contenga las 9 salas autorizadas con aforos exactos."""
    assert RUTA_DATASET_DEFAULT.exists()
    resultado = cargar_salas_dataset(RUTA_DATASET_DEFAULT)

    assert resultado.total_leidas == 9
    assert len(resultado.validas) == 9
    assert len(resultado.rechazadas) == 0

    aforos_esperados = {
        "Auditorio": 100,
        "Cosmos": 25,
        "Skilab": 20,
        "Spooki": 38,
        "Apolo": 34,
        "Blanca": 12,
        "Azul": 10,
        "Amarillas verdes": 6,
        "Artemis": 32,
    }

    nombres_cargados = {s["nombre"]: s["aforo"] for s in resultado.validas}
    assert nombres_cargados == aforos_esperados
    for s in resultado.validas:
        assert s["estado"] == "activa"


def test_loader_tolera_registros_inconsistentes(tmp_path: Path):
    """Prueba que el loader descarte registros corruptos sin detener la carga de las válidas."""
    csv_corrupto = tmp_path / "salas_inconsistentes.csv"
    contenido = (
        "nombre,aforo,estado\n"
        "Sala Valida 1,20,activa\n"
        ",15,activa\n"  # Nombre vacío
        "   ,30,activa\n"  # Nombre espacios
        "Sala Aforo Negativo,-5,activa\n"  # Aforo negativo
        "Sala Aforo Cero,0,activa\n"  # Aforo cero
        "Sala Aforo Texto,veinte,activa\n"  # Aforo no numérico
        "sala valida 1,40,activa\n"  # Duplicado case-insensitive
        "Sala Estado Raro,15,estado_inexistente\n"  # Estado desconocido
        "Sala Sin Estado,50,\n"  # Estado vacío (debe normalizar a activa)
    )
    csv_corrupto.write_text(contenido, encoding="utf-8")

    resultado = cargar_salas_dataset(csv_corrupto)

    assert resultado.total_leidas == 9
    assert len(resultado.validas) == 2
    assert len(resultado.rechazadas) == 7

    nombres_validos = [s["nombre"] for s in resultado.validas]
    assert nombres_validos == ["Sala Valida 1", "Sala Sin Estado"]
    assert resultado.validas[1]["estado"] == "activa"

    motivos = [r["motivo"] for r in resultado.rechazadas]
    assert any("vacío" in m for m in motivos)
    assert any("duplicado" in m for m in motivos)
    assert any("Aforo inválido" in m for m in motivos)
    assert any("desconocido" in m for m in motivos)


def test_loader_soporta_formato_json(tmp_path: Path):
    """Valida que el loader pueda leer también estructuras JSON."""
    json_path = tmp_path / "salas.json"
    datos = [
        {"nombre": "Lab IA", "aforo": 18, "estado": "activa"},
        {"nombre": "Lab Cloud", "aforo": 22},
    ]
    json_path.write_text(json.dumps(datos), encoding="utf-8")

    resultado = cargar_salas_dataset(json_path)
    assert len(resultado.validas) == 2
    assert len(resultado.rechazadas) == 0
    assert resultado.validas[0]["nombre"] == "Lab IA"
    assert resultado.validas[1]["estado"] == "activa"


def test_loader_archivo_inexistente_lanza_error():
    with pytest.raises(FileNotFoundError):
        cargar_salas_dataset("ruta/inexistente/salas.csv")


def test_seed_salas_persiste_en_db_vacia(db: Session):
    """Verifica la persistencia de las 9 salas en base de datos limpia."""
    assert db.query(Sala).count() == 0

    resumen = seed_salas(db)

    assert resumen["status"] == "completado"
    assert resumen["creadas"] == 9
    assert resumen["rechazadas"] == 0
    assert db.query(Sala).count() == 9

    auditorio = db.query(Sala).filter(Sala.nombre == "Auditorio").first()
    assert auditorio is not None
    assert auditorio.aforo == 100


def test_seed_salas_es_idempotente(db: Session):
    """Verifica que si la base de datos ya contiene salas, el seed no duplica nada."""
    # Primera ejecución
    seed_salas(db)
    assert db.query(Sala).count() == 9

    # Segunda ejecución
    resumen2 = seed_salas(db)
    assert resumen2["status"] == "ya_inicializada"
    assert resumen2["creadas"] == 0
    assert resumen2["existentes"] == 9
    assert db.query(Sala).count() == 9


def test_seed_salas_con_archivo_inconsistente(db: Session, tmp_path: Path):
    """Verifica que el seed persista solo las válidas y reporte las corruptas."""
    archivo_mixto = tmp_path / "mixtas.csv"
    archivo_mixto.write_text(
        "nombre,aforo,estado\n"
        "Sala Alpha,10,activa\n"
        ",20,activa\n"
        "Sala Beta,-1,activa\n"
        "Sala Gamma,15,activa\n",
        encoding="utf-8",
    )

    resumen = seed_salas(db, ruta_archivo=archivo_mixto)
    assert resumen["status"] == "completado"
    assert resumen["creadas"] == 2
    assert resumen["rechazadas"] == 2
    assert db.query(Sala).count() == 2


def test_seed_cli_main(monkeypatch, tmp_path: Path):
    """Verifica la ejecución del CLI del seed."""
    monkeypatch.setattr("sys.argv", ["seed.py"])
    codigo = main()
    assert codigo == 0

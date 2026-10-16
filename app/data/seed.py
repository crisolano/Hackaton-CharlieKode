import logging
import sys
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.data.loader import CargaDatasetResult, cargar_salas_dataset
from app.models import Sala

logger = logging.getLogger(__name__)

RUTA_DATASET_DEFAULT = Path(__file__).resolve().parent.parent.parent / "datos" / "salas.csv"


def seed_salas(
    db: Session, ruta_archivo: Path | str | None = None
) -> dict[str, Any]:
    """
    Carga las salas desde el dataset en la base de datos de manera idempotente.
    Solo realiza la inserción si la tabla de salas está vacía.

    Registra en log las salas cargadas y las filas rechazadas.
    Retorna un diccionario con el resumen de la operación.
    """
    total_existentes = db.query(Sala).count()
    if total_existentes > 0:
        logger.info(
            f"Seed de salas omitido: base de datos con {total_existentes} salas registradas."
        )
        return {
            "status": "ya_inicializada",
            "creadas": 0,
            "existentes": total_existentes,
            "rechazadas": 0,
        }

    archivo = Path(ruta_archivo) if ruta_archivo else RUTA_DATASET_DEFAULT
    logger.info(f"Iniciando seed de salas desde: {archivo}")

    resultado: CargaDatasetResult = cargar_salas_dataset(archivo)

    # Reportar registros inconsistentes o rechazados
    if resultado.rechazadas:
        logger.warning(
            f"Se encontraron {len(resultado.rechazadas)} registros inconsistentes en el dataset:"
        )
        for r in resultado.rechazadas:
            logger.warning(
                f"  [Fila {r['indice']}] {r['motivo']}"
            )

    # Persistir las salas válidas
    salas_a_insertar = [
        Sala(
            nombre=s["nombre"],
            aforo=s["aforo"],
            estado=s["estado"],
        )
        for s in resultado.validas
    ]

    db.add_all(salas_a_insertar)
    db.commit()

    logger.info(
        f"Seed de salas completado exitosamente: {len(salas_a_insertar)} salas insertadas."
    )

    return {
        "status": "completado",
        "creadas": len(salas_a_insertar),
        "rechazadas": len(resultado.rechazadas),
        "total_leidas": resultado.total_leidas,
    }


def main() -> int:
    """Punto de entrada CLI para ejecutar el seed: python -m app.data.seed"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Verificando y creando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        resumen = seed_salas(db)
        logger.info(f"Resultado del seed: {resumen}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

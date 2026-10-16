import csv
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import SalaEstado

logger = logging.getLogger(__name__)


@dataclass
class CargaDatasetResult:
    """Resultado estructurado de la lectura y normalización del dataset de salas."""

    validas: list[dict[str, Any]] = field(default_factory=list)
    rechazadas: list[dict[str, Any]] = field(default_factory=list)
    total_leidas: int = 0


def cargar_salas_dataset(ruta_archivo: Path | str) -> CargaDatasetResult:
    """
    Carga y normaliza el dataset de salas desde un archivo CSV o JSON.

    Tolera y descarta registros inconsistentes:
    - Fila sin campo nombre o nombre vacío tras strip.
    - Fila con aforo no convertible a entero o menor o igual a cero.
    - Nombre de sala duplicado (comparación insensible a mayúsculas/minúsculas).
    - Estado no válido (se normaliza al valor por defecto o se rechaza si es desconocido).

    Retorna un CargaDatasetResult con las filas válidas y las filas rechazadas junto a su motivo.
    """
    path = Path(ruta_archivo)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de datos: {path}")

    registros_crudos: list[dict[str, Any]] = []

    if path.suffix.lower() == ".json":
        with open(path, encoding="utf-8") as f:
            contenido = json.load(f)
            if isinstance(contenido, list):
                registros_crudos = contenido
            elif isinstance(contenido, dict) and "salas" in contenido:
                registros_crudos = contenido["salas"]
            else:
                registros_crudos = [contenido]
    else:
        # Por defecto procesar como CSV (usando delimitador por sniffing o coma)
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            registros_crudos = list(reader)

    resultado = CargaDatasetResult(total_leidas=len(registros_crudos))
    nombres_registrados: set[str] = set()

    estados_validos = {e.value for e in SalaEstado}

    for idx, reg in enumerate(registros_crudos, start=1):
        # Normalizar claves a minúsculas para robustez
        fila = {str(k).strip().lower(): v for k, v in reg.items() if k is not None}

        # 1. Validar presencia y valor de 'nombre'
        nombre_crudo = fila.get("nombre")
        if not nombre_crudo or not str(nombre_crudo).strip():
            resultado.rechazadas.append(
                {
                    "indice": idx,
                    "fila": reg,
                    "motivo": "El nombre de la sala está vacío o no fue especificado",
                }
            )
            continue

        nombre_normalizado = str(nombre_crudo).strip()
        nombre_clave = nombre_normalizado.lower()

        # 2. Validar nombres duplicados en el mismo dataset
        if nombre_clave in nombres_registrados:
            resultado.rechazadas.append(
                {
                    "indice": idx,
                    "fila": reg,
                    "motivo": f"Nombre de sala duplicado: '{nombre_normalizado}'",
                }
            )
            continue

        # 3. Validar aforo
        aforo_crudo = fila.get("aforo")
        try:
            aforo = int(aforo_crudo)
            if aforo <= 0:
                raise ValueError("El aforo debe ser mayor a cero")
        except (ValueError, TypeError):
            resultado.rechazadas.append(
                {
                    "indice": idx,
                    "fila": reg,
                    "motivo": f"Aforo inválido: '{aforo_crudo}' (debe ser un entero positivo > 0)",
                }
            )
            continue

        # 4. Validar o asignar estado
        estado_crudo = fila.get("estado")
        if estado_crudo:
            estado = str(estado_crudo).strip().lower()
            if estado not in estados_validos:
                resultado.rechazadas.append(
                    {
                        "indice": idx,
                        "fila": reg,
                        "motivo": f"Estado de sala desconocido: '{estado_crudo}'",
                    }
                )
                continue
        else:
            estado = SalaEstado.ACTIVA.value

        nombres_registrados.add(nombre_clave)
        resultado.validas.append(
            {
                "nombre": nombre_normalizado,
                "aforo": aforo,
                "estado": estado,
            }
        )

    return resultado

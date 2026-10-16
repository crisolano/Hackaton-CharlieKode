import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def test_importar_errors_no_carga_fastapi_ni_starlette():
    """Las reglas importan app.core.errors: no debe arrastrar el framework web."""
    codigo = (
        "import sys\n"
        "import app.core.errors\n"
        "cargados = [m for m in ('fastapi', 'starlette') if m in sys.modules]\n"
        "assert not cargados, cargados\n"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr

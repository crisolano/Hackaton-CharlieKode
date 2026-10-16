import logging
from types import SimpleNamespace

from app.core import logging_config


def _logging_falso(monkeypatch, handlers):
    """Sustituye solo el nombre `logging` dentro de logging_config (no el módulo global)."""
    llamadas = []
    falso = SimpleNamespace(
        INFO=logging.INFO,
        getLogger=lambda *args: SimpleNamespace(handlers=handlers),
        basicConfig=lambda **kwargs: llamadas.append(kwargs),
    )
    monkeypatch.setattr(logging_config, "logging", falso)
    return llamadas


def test_setup_logging_configura_cuando_el_root_no_tiene_handlers(monkeypatch):
    llamadas = _logging_falso(monkeypatch, handlers=[])
    logging_config.setup_logging()
    assert len(llamadas) == 1
    assert llamadas[0]["format"] == logging_config.LOG_FORMAT


def test_setup_logging_respeta_una_configuracion_existente(monkeypatch):
    llamadas = _logging_falso(monkeypatch, handlers=[object()])
    logging_config.setup_logging()
    assert llamadas == []

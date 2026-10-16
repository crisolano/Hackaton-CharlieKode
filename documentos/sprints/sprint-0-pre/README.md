# Pre-sprint (0:00-0:15) — Los tres juntos

**Meta:** esqueleto del proyecto listo para trabajar en paralelo sin conflictos.

- [ ] Verificar `.gitignore` (incluye `.env`) y `.env.example` en el primer commit.
- [ ] Crear entorno virtual e instalar `requirements.txt`; confirmar `ruff` y `pytest`.
- [ ] `app/main.py` mínimo con `GET /health` y arranque con `uvicorn app.main:app --reload`.
- [ ] `app/core/config.py` (lee `.env`) y `app/core/database.py` (engine y sesión desde `DATABASE_URL`).
- [ ] `app/core/errors.py`: excepciones de dominio y códigos (`AFORO_EXCEDIDO`, `SALA_OCUPADA`, `RECURSO_NO_DISPONIBLE`).
- [ ] Enumeraciones compartidas (estados, categorías, prioridades, rutas) y códigos HTTP de error según [04-guia-desarrollo.md](../../04-guia-desarrollo.md); confirmar los valores marcados.
- [ ] README raíz mínimo (nombre, integrantes, cómo correr); Dev 3 lo completa en el Sprint 3.
- [ ] Acordar modelo de datos y contrato de API ([01-arquitectura.md](../../01-arquitectura.md), secciones 6 y 8).
- [ ] Crear la rama `develop` desde `main` y publicarla; proteger `main` y `develop` (ver [03-gitflow.md](../../03-gitflow.md)).
- [ ] Cada dev crea su primera rama `feature/<dev>-<tema>` desde `develop`.
- [ ] Revisar el dataset oficial apenas llegue y guardarlo en `datos/`.

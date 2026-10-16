# Pre-sprint (0:00-0:15) — Los tres juntos

**Meta:** esqueleto del proyecto listo para trabajar en paralelo sin conflictos.

- [ ] Verificar `.gitignore` (incluye `.env`) y `.env.example` en el primer commit.
- [ ] Crear entorno virtual e instalar `requirements.txt`; confirmar `ruff` y `pytest`.
- [ ] `app/main.py` mínimo con `GET /health` y arranque con `uvicorn app.main:app --reload`.
- [ ] `app/core/config.py` (lee `.env`) y `app/core/database.py` (engine y sesión desde `DATABASE_URL`).
- [ ] `app/core/errors.py`: excepciones de dominio y códigos (`AFORO_EXCEDIDO`, `SALA_OCUPADA`, `RECURSO_NO_DISPONIBLE`).
- [ ] Acordar modelo de datos y contrato de API ([01-arquitectura.md](../../01-arquitectura.md), secciones 6 y 8).
- [ ] Crear las ramas `dev1/...`, `dev2/...`, `dev3/...` y hacer el primer commit en `main`.
- [ ] Revisar el dataset oficial apenas llegue y guardarlo en `datos/`.

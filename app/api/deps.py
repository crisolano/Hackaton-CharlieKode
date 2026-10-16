from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

# Sesión de base de datos inyectada en los routers; las pruebas la reemplazan
# con app.dependency_overrides[get_db].
DbSession = Annotated[Session, Depends(get_db)]

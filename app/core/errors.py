from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# Este módulo lo importan las reglas y los servicios (capas puras): no debe cargar
# FastAPI ni Starlette al importarse. Esos imports viven dentro de
# setup_exception_handlers().
if TYPE_CHECKING:
    from fastapi import FastAPI, Request
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

# Códigos HTTP del contrato (guía de desarrollo, sección 5)
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE = 422
HTTP_INTERNAL_ERROR = 500

# Mensajes y plantillas centralizadas (para facilitar cambios en la defensa)
ERROR_MESSAGES = {
    "AFORO_EXCEDIDO": "El aforo solicitado excede la capacidad máxima de la sala.",
    "SALA_OCUPADA": "La sala ya se encuentra reservada en el horario solicitado.",
    "RECURSO_NO_DISPONIBLE": "El recurso solicitado se encuentra inhabilitado o no disponible.",
    "NO_ENCONTRADO": "El recurso solicitado no fue encontrado.",
    "DATOS_INVALIDOS": "Los datos proporcionados no son válidos.",
    "ERROR_INTERNO": "Ocurrió un error interno en el servidor.",
}

ERROR_TEMPLATES = {
    "AFORO_EXCEDIDO": "La sala {sala} admite {aforo} personas y se pidieron {asistentes}.",
    "SALA_OCUPADA": "La sala {sala} ya está reservada entre {inicio} y {fin}.",
    "RECURSO_NO_DISPONIBLE": "El recurso {recurso} con id {id} no se encuentra disponible.",
    "NO_ENCONTRADO": "No existe {recurso} con id {id}.",
}

MSG_ERROR_RANGO_HORARIO = "La fecha de inicio debe ser anterior a la fecha de fin."
MSG_ERROR_TIMEZONE = "Las fechas de reserva deben ser en hora local sin zona horaria (naive)."


class AppException(Exception):
    def __init__(
        self,
        codigo: str,
        mensaje: str | None = None,
        status_code: int = HTTP_BAD_REQUEST,
        detalles: Any = None,
    ):
        self.codigo = codigo
        self.mensaje = mensaje or ERROR_MESSAGES.get(codigo, "Error en la operación.")
        self.status_code = status_code
        self.detalles = detalles
        super().__init__(self.mensaje)


class AforoExcedido(AppException):
    def __init__(
        self,
        sala: str | None = None,
        aforo: int | None = None,
        asistentes: int | None = None,
        mensaje: str | None = None,
        detalles: Any = None,
    ):
        if mensaje is None and sala is not None and aforo is not None and asistentes is not None:
            mensaje = ERROR_TEMPLATES["AFORO_EXCEDIDO"].format(
                sala=sala, aforo=aforo, asistentes=asistentes
            )
        super().__init__(
            codigo="AFORO_EXCEDIDO",
            mensaje=mensaje or ERROR_MESSAGES["AFORO_EXCEDIDO"],
            status_code=HTTP_UNPROCESSABLE,
            detalles=detalles,
        )


class SalaOcupada(AppException):
    def __init__(
        self,
        sala: str | None = None,
        inicio: Any = None,
        fin: Any = None,
        mensaje: str | None = None,
        detalles: Any = None,
    ):
        if mensaje is None and sala is not None and inicio is not None and fin is not None:
            mensaje = ERROR_TEMPLATES["SALA_OCUPADA"].format(sala=sala, inicio=inicio, fin=fin)
        super().__init__(
            codigo="SALA_OCUPADA",
            mensaje=mensaje or ERROR_MESSAGES["SALA_OCUPADA"],
            status_code=HTTP_CONFLICT,
            detalles=detalles,
        )


class RecursoNoDisponible(AppException):
    def __init__(
        self,
        recurso: str | None = None,
        id: Any = None,
        mensaje: str | None = None,
        detalles: Any = None,
    ):
        if mensaje is None and recurso is not None and id is not None:
            mensaje = ERROR_TEMPLATES["RECURSO_NO_DISPONIBLE"].format(recurso=recurso, id=id)
        super().__init__(
            codigo="RECURSO_NO_DISPONIBLE",
            mensaje=mensaje or ERROR_MESSAGES["RECURSO_NO_DISPONIBLE"],
            status_code=HTTP_CONFLICT,
            detalles=detalles,
        )


class NoEncontrado(AppException):
    def __init__(
        self,
        recurso: str | None = None,
        id: Any = None,
        mensaje: str | None = None,
        detalles: Any = None,
    ):
        if mensaje is None and recurso is not None and id is not None:
            mensaje = ERROR_TEMPLATES["NO_ENCONTRADO"].format(recurso=recurso, id=id)
        super().__init__(
            codigo="NO_ENCONTRADO",
            mensaje=mensaje or ERROR_MESSAGES["NO_ENCONTRADO"],
            status_code=HTTP_NOT_FOUND,
            detalles=detalles,
        )


class DatosInvalidos(AppException):
    def __init__(self, mensaje: str | None = None, detalles: Any = None):
        super().__init__(
            codigo="DATOS_INVALIDOS",
            mensaje=mensaje or ERROR_MESSAGES["DATOS_INVALIDOS"],
            status_code=HTTP_UNPROCESSABLE,
            detalles=detalles,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    from fastapi.exception_handlers import http_exception_handler as default_http_handler
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        content = {
            "ok": False,
            "codigo": exc.codigo,
            "mensaje": exc.mensaje,
        }
        if exc.detalles is not None:
            content["detalles"] = exc.detalles
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_UNPROCESSABLE,
            content={
                "ok": False,
                "codigo": "DATOS_INVALIDOS",
                "mensaje": ERROR_MESSAGES["DATOS_INVALIDOS"],
                "detalles": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Solo 404 y 5xx tienen código propio en el contrato (guía, sección 5);
        # el resto de errores HTTP conserva el comportamiento por defecto.
        if exc.status_code == HTTP_NOT_FOUND:
            codigo = "NO_ENCONTRADO"
        elif exc.status_code >= HTTP_INTERNAL_ERROR:
            codigo = "ERROR_INTERNO"
            logger.error(
                "Error HTTP %s en %s %s",
                exc.status_code,
                request.method,
                request.url.path,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
        else:
            return await default_http_handler(request, exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"ok": False, "codigo": codigo, "mensaje": ERROR_MESSAGES[codigo]},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Error no controlado en %s %s",
            request.method,
            request.url.path,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=HTTP_INTERNAL_ERROR,
            content={
                "ok": False,
                "codigo": "ERROR_INTERNO",
                "mensaje": ERROR_MESSAGES["ERROR_INTERNO"],
            },
        )

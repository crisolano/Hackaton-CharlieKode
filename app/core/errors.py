from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Mensajes y textos centralizados (para facilitar cambios en la defensa)
ERROR_MESSAGES = {
    "AFORO_EXCEDIDO": "El aforo solicitado excede la capacidad máxima de la sala.",
    "SALA_OCUPADA": "La sala ya se encuentra reservada en el horario solicitado.",
    "RECURSO_NO_DISPONIBLE": "El recurso solicitado se encuentra inhabilitado o no disponible.",
    "NO_ENCONTRADO": "El recurso solicitado no fue encontrado.",
    "DATOS_INVALIDOS": "Los datos proporcionados no son válidos.",
    "ERROR_INTERNO": "Ocurrió un error interno en el servidor.",
}


class AppException(Exception):
    def __init__(
        self,
        codigo: str,
        mensaje: str | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detalles: Any = None,
    ):
        self.codigo = codigo
        self.mensaje = mensaje or ERROR_MESSAGES.get(codigo, "Error en la operación.")
        self.status_code = status_code
        self.detalles = detalles
        super().__init__(self.mensaje)


class AforoExcedido(AppException):
    def __init__(self, mensaje: str | None = None, detalles: Any = None):
        super().__init__(
            codigo="AFORO_EXCEDIDO",
            mensaje=mensaje or ERROR_MESSAGES["AFORO_EXCEDIDO"],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detalles=detalles,
        )


class SalaOcupada(AppException):
    def __init__(self, mensaje: str | None = None, detalles: Any = None):
        super().__init__(
            codigo="SALA_OCUPADA",
            mensaje=mensaje or ERROR_MESSAGES["SALA_OCUPADA"],
            status_code=status.HTTP_409_CONFLICT,
            detalles=detalles,
        )


class RecursoNoDisponible(AppException):
    def __init__(self, mensaje: str | None = None, detalles: Any = None):
        super().__init__(
            codigo="RECURSO_NO_DISPONIBLE",
            mensaje=mensaje or ERROR_MESSAGES["RECURSO_NO_DISPONIBLE"],
            status_code=status.HTTP_409_CONFLICT,
            detalles=detalles,
        )


class NoEncontrado(AppException):
    def __init__(self, mensaje: str | None = None, detalles: Any = None):
        super().__init__(
            codigo="NO_ENCONTRADO",
            mensaje=mensaje or ERROR_MESSAGES["NO_ENCONTRADO"],
            status_code=status.HTTP_404_NOT_FOUND,
            detalles=detalles,
        )


class DatosInvalidos(AppException):
    def __init__(self, mensaje: str | None = None, detalles: Any = None):
        super().__init__(
            codigo="DATOS_INVALIDOS",
            mensaje=mensaje or ERROR_MESSAGES["DATOS_INVALIDOS"],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detalles=detalles,
        )


def setup_exception_handlers(app: FastAPI) -> None:
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "ok": False,
                "codigo": "DATOS_INVALIDOS",
                "mensaje": ERROR_MESSAGES["DATOS_INVALIDOS"],
                "detalles": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "ok": False,
                "codigo": "ERROR_INTERNO",
                "mensaje": ERROR_MESSAGES["ERROR_INTERNO"],
            },
        )

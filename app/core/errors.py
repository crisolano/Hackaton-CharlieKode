from typing import Any

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
        status_code: int = 400,
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
            status_code=422,
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
            status_code=409,
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
            status_code=409,
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
            status_code=404,
            detalles=detalles,
        )


class DatosInvalidos(AppException):
    def __init__(self, mensaje: str | None = None, detalles: Any = None):
        super().__init__(
            codigo="DATOS_INVALIDOS",
            mensaje=mensaje or ERROR_MESSAGES["DATOS_INVALIDOS"],
            status_code=422,
            detalles=detalles,
        )


def setup_exception_handlers(app: Any) -> None:
    from fastapi import Request
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse

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
            status_code=422,
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
            status_code=500,
            content={
                "ok": False,
                "codigo": "ERROR_INTERNO",
                "mensaje": ERROR_MESSAGES["ERROR_INTERNO"],
            },
        )

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response

from app.core.errors import ERROR_MESSAGES, AppException
from app.web.routes import templates

HTMX_HEADER = "HX-Request"


def es_peticion_htmx(request: Request) -> bool:
    return request.headers.get(HTMX_HEADER) == "true"


def _parcial_error(request: Request, codigo: str, mensaje: str, status_code: int) -> Response:
    return templates.TemplateResponse(
        request,
        "partials/error.html",
        {"codigo": codigo, "mensaje": mensaje},
        status_code=status_code,
    )


def setup_htmx_error_handlers(app: FastAPI) -> None:
    """Parcial HTML para peticiones HTMX; el resto sigue recibiendo el JSON de core."""
    json_app_handler = app.exception_handlers[AppException]
    json_validation_handler = app.exception_handlers[RequestValidationError]

    async def app_exception_handler(request: Request, exc: AppException) -> Response:
        if es_peticion_htmx(request):
            return _parcial_error(request, exc.codigo, exc.mensaje, exc.status_code)
        return await json_app_handler(request, exc)

    async def validation_handler(request: Request, exc: RequestValidationError) -> Response:
        if es_peticion_htmx(request):
            # Solo el mensaje general: los datos enviados (exc.errors()) no se muestran.
            return _parcial_error(
                request, "DATOS_INVALIDOS", ERROR_MESSAGES["DATOS_INVALIDOS"], 422
            )
        return await json_validation_handler(request, exc)

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)

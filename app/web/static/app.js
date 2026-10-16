// HTMX no intercambia por defecto las respuestas 4xx; los parciales de error
// de la app (400, 409, 422) deben mostrarse en pantalla.
document.body.addEventListener("htmx:beforeSwap", (event) => {
  const status = event.detail.xhr.status;
  if (status >= 400 && status < 500) {
    event.detail.shouldSwap = true;
    event.detail.isError = false;
  }
});

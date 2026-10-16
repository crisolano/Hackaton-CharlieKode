// Comportamiento de la interfaz sobre HTMX. Los textos que ve la persona usuaria
// vienen del HTML (atributos data-*) o del servidor; aquí no se escriben mensajes.

const ALERTA_ERROR_ICONO =
  '<svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
  'stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/>' +
  '<path d="M12 7.5v5.5m0 3h.01"/></svg>';

const raiz = document.documentElement;

// ---------------------------------------------------------------- movimiento

function movimientoReducido() {
  return (
    raiz.dataset.movimiento === "off" ||
    (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)
  );
}

// Lleva el aviso a la vista sin saltos bruscos (y sin animar si se pidió menos movimiento).
function revelarAviso(destino) {
  const aviso = destino && destino.querySelector(".alert");
  if (!aviso || aviso.classList.contains("alert-info")) return;
  aviso.scrollIntoView({ block: "nearest", behavior: movimientoReducido() ? "auto" : "smooth" });
}

// Botón "Pausar animaciones" (WCAG 2.2.2). La preferencia se recuerda si hay localStorage.
function aplicarMovimiento(apagado) {
  if (apagado) raiz.dataset.movimiento = "off";
  else delete raiz.dataset.movimiento;
  const boton = document.getElementById("btn-movimiento");
  if (!boton) return;
  boton.setAttribute("aria-pressed", String(apagado));
  boton.textContent = apagado ? boton.dataset.textoReanudar : boton.dataset.textoPausar;
}

function iniciarBotonMovimiento() {
  const boton = document.getElementById("btn-movimiento");
  if (!boton) return;
  aplicarMovimiento(raiz.dataset.movimiento === "off");
  boton.addEventListener("click", () => {
    const apagar = raiz.dataset.movimiento !== "off";
    aplicarMovimiento(apagar);
    try {
      if (apagar) localStorage.setItem("movimiento", "off");
      else localStorage.removeItem("movimiento");
    } catch (e) {
      /* sin almacenamiento: la preferencia solo vale para esta visita */
    }
  });
}

// Con la pestaña oculta se pausan las animaciones (el CSS usa el atributo).
document.addEventListener("visibilitychange", () => {
  raiz.toggleAttribute("data-oculta", document.hidden);
});

// ---------------------------------------------------------------- avisos

function mostrarAviso(destino, clase, texto, rol) {
  if (!destino || !texto) return;
  const caja = document.createElement("div");
  caja.className = "alert " + clase;
  caja.setAttribute("role", rol);
  caja.innerHTML = clase === "alert-error" ? ALERTA_ERROR_ICONO : "";
  const parrafo = document.createElement("p");
  parrafo.textContent = texto;
  caja.appendChild(parrafo);
  destino.replaceChildren(caja);
  revelarAviso(destino);
}

function destinoDe(evento) {
  return evento.detail.target || document.getElementById("resultado");
}

// HTMX no intercambia por defecto las respuestas 4xx/5xx. Los parciales HTML de error de la
// app (400, 409, 422, 503) deben verse en pantalla; una respuesta que no sea HTML (por ejemplo
// un 500 en JSON) no se pinta tal cual: se muestra el mensaje genérico del servidor.
document.body.addEventListener("htmx:beforeSwap", (evento) => {
  const xhr = evento.detail.xhr;
  if (xhr.status < 400) return;
  const tipo = xhr.getResponseHeader("Content-Type") || "";
  if (tipo.includes("text/html")) {
    evento.detail.shouldSwap = true;
    evento.detail.isError = false;
  } else {
    evento.detail.shouldSwap = false;
    const destino = destinoDe(evento);
    mostrarAviso(destino, "alert-error", destino && destino.dataset.errorGenerico, "alert");
  }
});

// Sin conexión o tiempo agotado: HTMX no recibe respuesta alguna.
["htmx:sendError", "htmx:timeout"].forEach((nombre) => {
  document.body.addEventListener(nombre, (evento) => {
    const destino = destinoDe(evento);
    mostrarAviso(destino, "alert-error", destino && destino.dataset.errorRed, "alert");
  });
});

// ---------------------------------------------------------------- formulario

function limpiarInvalidos(formulario) {
  formulario.querySelectorAll("[aria-invalid]").forEach((campo) => campo.removeAttribute("aria-invalid"));
}

// Estado de carga anunciado a lectores de pantalla (el anillo del botón es solo visual).
document.body.addEventListener("htmx:beforeRequest", (evento) => {
  const origen = evento.detail.elt;
  if (origen.tagName === "FORM") limpiarInvalidos(origen);
  const texto = origen.dataset && origen.dataset.mensajeCarga;
  if (texto) mostrarAviso(destinoDe(evento), "alert-info", texto, "status");
});

// Tras pintar el resultado: se lleva a la vista y, si el servidor indica qué campo falló,
// se marca como inválido y se enfoca el primero.
document.body.addEventListener("htmx:afterSwap", (evento) => {
  const destino = evento.detail.target;
  if (!destino || destino.id !== "resultado") return;
  const aviso = destino.querySelector("[data-campo]");
  if (aviso) {
    const campos = aviso.dataset.campo
      .split(" ")
      .map((nombre) => document.getElementById(nombre))
      .filter(Boolean);
    campos.forEach((campo) => campo.setAttribute("aria-invalid", "true"));
    if (campos.length) campos[0].focus({ preventScroll: true });
  }
  revelarAviso(destino);
});

// Al editar un campo marcado, deja de estar marcado.
["input", "change"].forEach((nombre) => {
  document.addEventListener(nombre, (evento) => {
    const campo = evento.target;
    if (campo && campo.getAttribute && campo.getAttribute("aria-invalid")) campo.removeAttribute("aria-invalid");
  });
});

// Tras una operación correcta se limpia el formulario y la ayuda de aforo. Se mira el código
// HTTP real (no `successful`, que HTMX da por bueno al permitir pintar los errores 4xx):
// si la reserva se rechaza, la persona conserva lo que escribió para corregirlo.
document.body.addEventListener("htmx:afterRequest", (evento) => {
  const origen = evento.detail.elt;
  const estado = evento.detail.xhr ? evento.detail.xhr.status : 0;
  if (estado >= 200 && estado < 400 && origen.hasAttribute && origen.hasAttribute("data-limpiar-al-exito")) {
    origen.reset();
    actualizarAyudaAforo();
    actualizarLimitesFechas();
  }
});

// Ayuda y tope de asistentes según la sala elegida (mejora progresiva: el servidor valida igualmente).
function actualizarAyudaAforo() {
  const selector = document.getElementById("sala_id");
  const ayuda = document.getElementById("ayuda-aforo");
  const asistentes = document.getElementById("asistentes");
  if (!selector) return;
  const opcion = selector.options[selector.selectedIndex];
  const aforo = opcion && opcion.dataset.aforo;
  if (ayuda) {
    ayuda.textContent = aforo
      ? "Aforo máximo de esta sala: " + aforo + " personas."
      : "Elige una sala para ver su aforo máximo.";
  }
  if (asistentes) {
    if (aforo) asistentes.max = aforo;
    else asistentes.removeAttribute("max");
  }
}

function dosCifras(n) {
  return String(n).padStart(2, "0");
}

// Valor de <input type="datetime-local"> para un instante, en hora local.
function formatoLocal(fecha) {
  return (
    fecha.getFullYear() + "-" + dosCifras(fecha.getMonth() + 1) + "-" + dosCifras(fecha.getDate()) +
    "T" + dosCifras(fecha.getHours()) + ":" + dosCifras(fecha.getMinutes())
  );
}

// El inicio no puede ser anterior a ahora y el fin no puede ser anterior al inicio.
function actualizarLimitesFechas() {
  const inicio = document.getElementById("inicio");
  const fin = document.getElementById("fin");
  if (!inicio) return;
  inicio.min = formatoLocal(new Date());
  if (fin) fin.min = inicio.value || inicio.min;
}

document.addEventListener("change", (evento) => {
  if (!evento.target) return;
  if (evento.target.id === "sala_id") actualizarAyudaAforo();
  if (evento.target.id === "inicio") actualizarLimitesFechas();
});
document.addEventListener("focusin", (evento) => {
  if (evento.target && evento.target.id === "inicio") actualizarLimitesFechas();
});

// Botón "Reservar esta sala" de cada tarjeta: preselecciona la sala en el formulario.
document.addEventListener("click", (evento) => {
  const enlace = evento.target.closest && evento.target.closest("[data-elegir-sala]");
  if (!enlace) return;
  const selector = document.getElementById("sala_id");
  if (!selector) return;
  selector.value = enlace.dataset.elegirSala;
  actualizarAyudaAforo();
  selector.focus({ preventScroll: true });
});

iniciarBotonMovimiento();
actualizarAyudaAforo();
actualizarLimitesFechas();

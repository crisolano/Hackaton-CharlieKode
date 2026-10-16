// Aparición discreta de secciones al hacer scroll (mejora progresiva, sin librerías).
// - Sin JS o sin IntersectionObserver no se oculta nada.
// - Solo se ocultan los objetivos que al cargar están por debajo del pliegue, para evitar
//   parpadeos en lo que ya se ve.
// - Cada elemento se revela una sola vez (se deja de observar tras revelarlo).
// - Nunca se aplica a zonas que HTMX reemplaza, a campos del formulario, a filas de tabla
//   ni a elementos con la clase .entra (ya tienen su entrada inicial).
// - Con prefers-reduced-motion o data-movimiento="off" el contenido aparece directamente.
(function () {
  "use strict";

  var raiz = document.documentElement;
  var OBJETIVOS = "main section, main [data-revelar]";
  var EXCLUIDOS = "#resultado, #salas-disponibilidad, #reservas";
  var CAMPOS = "input, select, textarea, button, label, fieldset, form, tr, td, th, tbody, thead, table";

  if (!("IntersectionObserver" in window) || !document.querySelector) return;

  function sinMovimiento() {
    return (
      raiz.dataset.movimiento === "off" ||
      (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)
    );
  }

  if (sinMovimiento()) return;

  function excluido(el) {
    if (el.classList.contains("entra")) return true;
    if (el.matches(CAMPOS)) return true;
    // Dentro (o igual) de una zona que HTMX reemplaza: se reiniciaría en cada swap.
    if (el.closest(EXCLUIDOS)) return true;
    return false;
  }

  // Si la URL apunta a un ancla (/salas#reservar) no se oculta lo que la contiene.
  function contieneAncla(el) {
    var id = window.location.hash ? decodeURIComponent(window.location.hash.slice(1)) : "";
    if (!id) return false;
    var destino = document.getElementById(id);
    return !!destino && (el === destino || el.contains(destino) || destino.contains(el));
  }

  var alto = window.innerHeight || raiz.clientHeight;
  var pendientes = [];

  Array.prototype.forEach.call(document.querySelectorAll(OBJETIVOS), function (el) {
    if (excluido(el) || contieneAncla(el)) return;
    // Evita animaciones anidadas: si un ancestro ya es objetivo pendiente, se omite.
    for (var i = 0; i < pendientes.length; i++) {
      if (pendientes[i].contains(el)) return;
    }
    if (el.getBoundingClientRect().top < alto) return; // visible al cargar: no se toca
    pendientes.push(el);
  });

  if (!pendientes.length) return;

  function limpiar(el) {
    el.classList.remove("revelar-transicion");
  }

  function revelar(el) {
    if (!el.classList.contains("revelar-oculto")) return;
    el.classList.add("revelar-transicion");
    el.classList.remove("revelar-oculto");
    el.addEventListener("transitionend", function fin(evento) {
      if (evento.target !== el) return;
      el.removeEventListener("transitionend", fin);
      limpiar(el);
    });
    // Por si no hay transición (movimiento reducido activado entre medias).
    window.setTimeout(function () {
      limpiar(el);
    }, 600);
  }

  var observador = new IntersectionObserver(
    function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        observador.unobserve(entrada.target);
        revelar(entrada.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
  );

  function revelarTodo() {
    pendientes.forEach(function (el) {
      observador.unobserve(el);
      el.classList.remove("revelar-oculto", "revelar-transicion");
    });
    observador.disconnect();
  }

  raiz.classList.add("js-revelar");
  pendientes.forEach(function (el) {
    el.classList.add("revelar-oculto");
    observador.observe(el);
  });

  // Si el foco (teclado) entra en algo aún oculto, se muestra de inmediato.
  document.addEventListener("focusin", function (evento) {
    var el = evento.target && evento.target.closest && evento.target.closest(".revelar-oculto");
    if (el) {
      observador.unobserve(el);
      el.classList.remove("revelar-oculto");
    }
  });

  // Botón "Pausar animaciones" (pone data-movimiento="off" en <html>): revela lo pendiente.
  if ("MutationObserver" in window) {
    new MutationObserver(function () {
      if (raiz.dataset.movimiento === "off") revelarTodo();
    }).observe(raiz, { attributes: true, attributeFilter: ["data-movimiento"] });
  }

  // Cambio de preferencia del sistema durante la visita.
  if (window.matchMedia) {
    var consulta = window.matchMedia("(prefers-reduced-motion: reduce)");
    var alCambiar = function () {
      if (consulta.matches) revelarTodo();
    };
    if (consulta.addEventListener) consulta.addEventListener("change", alCambiar);
    else if (consulta.addListener) consulta.addListener(alCambiar);
  }
})();

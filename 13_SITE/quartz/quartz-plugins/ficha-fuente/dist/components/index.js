/**
 * Componentes propios del sitio "Metodología Xavi Ruyra".
 *
 * Tres piezas:
 *  - FichaFuente: cabecera de una nota con su trazabilidad (tipo, confianza,
 *    estado, fuente en vídeo con minuto) y botón para copiar la cita.
 *  - PanelAvance: panel de progreso para las páginas índice (cuántas notas
 *    hay, cuántos fotogramas están anotados, qué falta).
 *  - Anotaciones: comentarios por sección, sin cuenta.
 *
 * Todo se renderiza en el servidor salvo la lista de anotaciones, que es
 * cliente: no hay base de datos ni servicio externo obligatorio.
 */

import { h, Fragment } from "preact"

// ---------------------------------------------------------------------------
// Utilidades
// ---------------------------------------------------------------------------

const c = (...x) => x.filter(Boolean).join(" ")

function fechaLarga(v) {
  if (!v) return ""
  const d = String(v)
  // Acepta "2026-11-15" o ISO completo.
  const m = d.match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (!m) return d
  const meses = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
  ]
  return `${Number(m[3])} de ${meses[Number(m[2]) - 1]} de ${m[1]}`
}

/** "6:11" o "06:11" -> segundos. Devuelve null si no es un minuto válido. */
function aSegundos(ts) {
  if (ts === undefined || ts === null || ts === "") return null
  const s = String(ts).trim()
  let m = s.match(/^(\d+):(\d{1,2})$/)
  if (m) return Number(m[1]) * 60 + Number(m[2])
  m = s.match(/^(\d+)$/)
  if (m) return Number(m[1])
  return null
}

function urlYoutube(video, ts) {
  if (!video) return null
  const seg = aSegundos(ts)
  const base = `https://www.youtube.com/watch?v=${encodeURIComponent(video)}`
  return seg === null ? base : `${base}&t=${seg}s`
}

const TIPOS = {
  concepto: "Concepto",
  regla: "Regla",
  operacion: "Operación",
  cambio: "Cambio metodológico",
  pregunta: "Pregunta abierta",
  bootcamp: "Clase del bootcamp",
  portada: "Portada",
  indice: "Índice",
}

function etiquetaTipo(t) {
  return TIPOS[String(t || "").toLowerCase()] || (t ? String(t) : "")
}


// ---------------------------------------------------------------------------
// FichaFuente — cabecera trazable de cada nota
// ---------------------------------------------------------------------------

const FichaFuente = () => {
  const Ficha = ({ fileData, displayClass }) => {
    const fm = fileData?.frontmatter || {}
    const tipo = fm.tipo
    // La portada y los índices no son "notas": no llevan ficha de fuente.
    if (!tipo || tipo === "portada" || tipo === "indice") return null

    const video = fm.video || fm.fuente_video || ""
    const ts = fm.timestamp || fm.fuente_timestamp || ""
    const yt = urlYoutube(video, ts)
    const conf = fm.confianza || ""
    const estado = fm.estado || ""
    const cat = fm.categoria || ""
    const dia = fm.dia

    const chips = []
    if (tipo) chips.push({ k: "tipo", v: etiquetaTipo(tipo) })
    if (dia) chips.push({ k: "dia", v: `Día ${dia}` })
    if (cat) chips.push({ k: "cat", v: cat })
    if (conf) chips.push({ k: "conf", v: conf })
    if (estado) chips.push({ k: "est", v: estado })
    if (fm.version) chips.push({ k: "ver", v: `v${fm.version}` })

    const cita = [
      fm.title || fm.titulo || fileData?.frontmatter?.title || "",
      video ? `— ${video}${ts ? ` @ ${ts}` : ""}` : "",
    ]
      .filter(Boolean)
      .join(" ")

    return h(
      "section",
      { class: c("xr-ficha", displayClass), "data-tipo": tipo },
      h(
        "div",
        { class: "xr-ficha-chips" },
        chips.map((ch) =>
          h("span", { class: `xr-chip xr-chip-${ch.k}`, key: ch.k + ch.v }, ch.v),
        ),
      ),
      video
        ? h(
            "div",
            { class: "xr-ficha-fuente" },
            h("span", { class: "xr-ficha-fuente-etq" }, "Fuente"),
            yt
              ? h(
                  "a",
                  {
                    class: "xr-boton xr-boton-fuente",
                    href: yt,
                    target: "_blank",
                    rel: "noopener noreferrer",
                  },
                  h("span", { class: "xr-play", "aria-hidden": "true" }),
                  `Ver en YouTube${ts ? ` · ${ts}` : ""}`,
                )
              : h("span", null, video),
            h(
              "button",
              {
                class: "xr-boton xr-boton-cita",
                type: "button",
                "data-cita": cita,
                title: "Copia la referencia para citarla fuera del sitio",
              },
              "Copiar cita",
            ),
          )
        : null,
      fm.aviso
        ? h("p", { class: "xr-ficha-aviso" }, String(fm.aviso))
        : null,
    )
  }

  Ficha.css = `
.xr-ficha {
  margin: 0 0 1.75rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--lightgray);
  border-radius: 10px;
  background: var(--xr-surface, var(--light));
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.xr-ficha-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.xr-chip {
  font-size: 0.74rem;
  line-height: 1.5;
  padding: 0.12rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--lightgray);
  color: var(--darkgray);
  letter-spacing: 0.01em;
  white-space: nowrap;
}
.xr-chip-tipo { background: var(--xr-accent-soft, var(--highlight)); color: var(--dark); border-color: transparent; font-weight: 600; }
.xr-chip-cat { border-color: var(--secondary); color: var(--secondary); }
.xr-chip-conf, .xr-chip-est { font-family: var(--codeFont, monospace); font-size: 0.7rem; }
.xr-ficha-fuente { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; font-size: 0.86rem; }
.xr-ficha-fuente-etq { color: var(--gray); text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.68rem; }
.xr-boton {
  font: inherit;
  font-size: 0.82rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.7rem;
  border-radius: 8px;
  border: 1px solid var(--lightgray);
  background: transparent;
  color: var(--dark);
  cursor: pointer;
  text-decoration: none;
  transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
}
.xr-boton:hover { background: var(--highlight); }
.xr-boton:active { transform: translateY(1px); }
.xr-boton-fuente { border-color: var(--secondary); color: var(--secondary); font-weight: 600; }
.xr-boton-cita { color: var(--darkgray); }
.xr-boton-cita[data-hecho="1"] { color: var(--tertiary); border-color: var(--tertiary); }
.xr-play {
  width: 0; height: 0;
  border-style: solid;
  border-width: 4px 0 4px 7px;
  border-color: transparent transparent transparent currentColor;
  display: inline-block;
}
.xr-ficha-aviso {
  margin: 0;
  font-size: 0.82rem;
  color: var(--darkgray);
  background: var(--xr-warn-soft, transparent);
  border-radius: 7px;
  padding: 0.45rem 0.65rem;
}
`

  Ficha.afterDOMLoaded = `
(function () {
  if (window.__xrFicha) return;
  window.__xrFicha = true;

  var RAIZ = document.documentElement;
  var reducido = window.matchMedia("(prefers-reduced-motion: reduce)");

  // --- 1. Botón «Copiar cita» -------------------------------------------
  function initFicha() {
    document.querySelectorAll(".xr-boton-cita").forEach(function (b) {
      if (b.dataset.listo) return;
      b.dataset.listo = "1";
      b.addEventListener("click", function () {
        var t = b.getAttribute("data-cita") || "";
        var hecho = function () {
          b.dataset.hecho = "1";
          var prev = b.textContent;
          b.textContent = "Copiado";
          setTimeout(function () { b.textContent = prev; b.dataset.hecho = "0"; }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(t).then(hecho).catch(function () {});
        } else {
          var ta = document.createElement("textarea");
          ta.value = t; document.body.appendChild(ta); ta.select();
          try { document.execCommand("copy"); hecho(); } catch (e) {}
          document.body.removeChild(ta);
        }
      });
    });
  }

  // --- 2. Transición al cambiar de página --------------------------------
  //
  // Quartz navega sin recargar (SPA) y sustituye el contenido de golpe: el
  // salto es seco y no se distingue de un parpadeo. Aquí se marca la raíz para
  // que el contenido nuevo entre con un movimiento corto.
  //
  // Se usa el evento «prenav», no «nav», para saber si esto es una navegación
  // de verdad. «nav» también se emite en la carga inicial —y además antes de
  // que este script registre su listener—, así que con «nav» la primera
  // navegación real se confundía con la inicial y no se animaba nunca.
  // «prenav» solo se emite cuando alguien ha pulsado un enlace: es la señal
  // exacta.
  var voyANavegar = false;
  document.addEventListener("prenav", function () { voyANavegar = true; });

  function marcarEntrada() {
    if (!voyANavegar) return;      // carga inicial: aparece ya puesta
    voyANavegar = false;
    if (reducido.matches) return;  // el sistema pide menos movimiento
    RAIZ.classList.remove("xr-navegando");
    // Forzar recálculo para que la animación vuelva a empezar.
    void RAIZ.offsetWidth;
    RAIZ.classList.add("xr-navegando");
    clearTimeout(marcarEntrada._t);
    marcarEntrada._t = setTimeout(function () {
      RAIZ.classList.remove("xr-navegando");
    }, 450);
  }

  // --- 3. Sección que se está leyendo ------------------------------------
  //
  // El índice de la derecha no marcaba ninguna sección: en una nota de 2 800 px
  // no había forma de saber por dónde ibas. Se marca la última sección cuyo
  // encabezado ya ha pasado por arriba.
  var tocObs = null;
  function initToc() {
    var enlaces = [].slice.call(
      document.querySelectorAll('.toc-content a[href^="#"]')
    );
    if (!enlaces.length) return;

    var mapa = {};
    enlaces.forEach(function (a) {
      var id = decodeURIComponent(a.getAttribute("href").slice(1));
      var li = a.closest("li");
      if (id && li) mapa[id] = li;
    });

    var secciones = Object.keys(mapa)
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    if (!secciones.length) return;

    var actual = null;
    function pintar() {
      var y = window.scrollY + 120;
      var elegida = null;
      for (var i = 0; i < secciones.length; i++) {
        if (secciones[i].getBoundingClientRect().top + window.scrollY <= y) {
          elegida = secciones[i].id;
        }
      }
      if (elegida === actual) return;
      actual = elegida;
      Object.keys(mapa).forEach(function (id) {
        if (id === elegida) mapa[id].setAttribute("data-xr-actual", "");
        else mapa[id].removeAttribute("data-xr-actual");
      });
    }

    var pendiente = false;
    function alScroll() {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(function () { pendiente = false; pintar(); });
    }

    window.addEventListener("scroll", alScroll, { passive: true });
    if (window.addCleanup) window.addCleanup(function () {
      window.removeEventListener("scroll", alScroll);
    });
    pintar();
  }

  function init() {
    initFicha();
    initToc();
  }

  document.addEventListener("nav", function () { marcarEntrada(); init(); });
  document.addEventListener("render", init);
  init();
})();
`

  return Ficha
}


export { FichaFuente }

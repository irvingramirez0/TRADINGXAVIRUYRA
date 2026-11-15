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
  border-left: 3px solid var(--xr-warn, #c98a00);
  padding-left: 0.6rem;
}
`

  Ficha.afterDOMLoaded = `
(function () {
  if (window.__xrFicha) return;
  window.__xrFicha = true;
  function init() {
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
  document.addEventListener("nav", init);
  document.addEventListener("render", init);
  init();
})();
`

  return Ficha
}


export { FichaFuente }

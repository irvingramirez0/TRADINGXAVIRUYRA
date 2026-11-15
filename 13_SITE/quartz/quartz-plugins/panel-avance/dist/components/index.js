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
// PanelAvance — progreso y estado del proyecto
// ---------------------------------------------------------------------------

const PanelAvance = () => {
  const Panel = ({ fileData, displayClass }) => {
    const fm = fileData?.frontmatter || {}
    const p = fm.panel
    if (!p || typeof p !== "object") return null

    const bloques = Array.isArray(p.bloques) ? p.bloques : []
    const barras = Array.isArray(p.barras) ? p.barras : []

    return h(
      "section",
      { class: c("xr-panel", displayClass) },
      p.titulo ? h("h2", { class: "xr-panel-titulo" }, p.titulo) : null,
      bloques.length
        ? h(
            "div",
            { class: "xr-panel-cifras" },
            bloques.map((b) =>
              h(
                "div",
                { class: "xr-cifra", key: b.etiqueta },
                h("span", { class: "xr-cifra-num" }, String(b.valor)),
                h("span", { class: "xr-cifra-etq" }, b.etiqueta),
                b.nota ? h("span", { class: "xr-cifra-nota" }, b.nota) : null,
              ),
            ),
          )
        : null,
      barras.length
        ? h(
            "div",
            { class: "xr-panel-barras" },
            barras.map((b) => {
              const total = Number(b.total) || 0
              const hecho = Number(b.hecho) || 0
              const pct = total > 0 ? Math.round((hecho / total) * 100) : 0
              return h(
                "div",
                { class: "xr-barra", key: b.etiqueta },
                h(
                  "div",
                  { class: "xr-barra-cab" },
                  h("span", null, b.etiqueta),
                  h("span", { class: "xr-barra-val" }, `${hecho} / ${total}`),
                ),
                h(
                  "div",
                  {
                    class: "xr-barra-pista",
                    role: "progressbar",
                    "aria-valuenow": String(pct),
                    "aria-valuemin": "0",
                    "aria-valuemax": "100",
                    "aria-label": b.etiqueta,
                  },
                  h("div", { class: "xr-barra-relleno", style: `width:${pct}%` }),
                ),
                b.nota ? h("span", { class: "xr-barra-nota" }, b.nota) : null,
              )
            }),
          )
        : null,
      p.pie ? h("p", { class: "xr-panel-pie" }, p.pie) : null,
    )
  }

  Panel.css = `
.xr-panel {
  margin: 0 0 2rem;
  padding: 1.15rem 1.25rem;
  border: 1px solid var(--lightgray);
  border-radius: 12px;
  background: var(--xr-surface, var(--light));
}
.xr-panel-titulo {
  margin: 0 0 0.9rem;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--gray);
  font-weight: 600;
}
.xr-panel-cifras {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.9rem;
  margin-bottom: 1.1rem;
}
.xr-cifra { display: flex; flex-direction: column; gap: 0.1rem; }
.xr-cifra-num { font-size: 1.7rem; line-height: 1.05; font-weight: 700; color: var(--dark); font-variant-numeric: tabular-nums; }
.xr-cifra-etq { font-size: 0.76rem; color: var(--darkgray); }
.xr-cifra-nota { font-size: 0.7rem; color: var(--gray); }
.xr-panel-barras { display: flex; flex-direction: column; gap: 0.75rem; }
.xr-barra-cab { display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--darkgray); margin-bottom: 0.25rem; }
.xr-barra-val { font-variant-numeric: tabular-nums; color: var(--gray); }
.xr-barra-pista { height: 7px; border-radius: 999px; background: var(--lightgray); overflow: hidden; }
.xr-barra-relleno { height: 100%; border-radius: 999px; background: var(--secondary); }
.xr-barra-nota { font-size: 0.7rem; color: var(--gray); }
.xr-panel-pie { margin: 0.9rem 0 0; font-size: 0.78rem; color: var(--gray); }
@media (max-width: 800px) {
  .xr-cifra-num { font-size: 1.4rem; }
}
`

  return Panel
}


export { PanelAvance }

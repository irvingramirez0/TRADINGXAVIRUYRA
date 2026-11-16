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
// Anotaciones — comentarios por sección, sin cuenta
// ---------------------------------------------------------------------------

const Anotaciones = () => {
  const Comp = ({ fileData, displayClass, cfg }) => {
    const fm = fileData?.frontmatter || {}
    if (fm.anotaciones === false || fm.anotaciones === "false") return null
    const slug = String(fileData?.slug || "")
    // El índice y las páginas de servicio no llevan anotaciones.
    if (slug === "index" || slug.startsWith("tags/")) return null

    return h(
      "section",
      {
        class: c("xr-anot", displayClass),
        id: "anotaciones",
        "data-nota": slug,
        "data-endpoint": fm.endpoint_anotaciones || "",
        "aria-labelledby": "xr-anot-titulo",
      },
      h(
        "div",
        { class: "xr-anot-cab" },
        h(
          "div",
          null,
          h("h2", { id: "xr-anot-titulo", class: "xr-anot-titulo" }, "Anotaciones"),
          h(
            "p",
            { class: "xr-anot-sub" },
            "Comentarios anclados a una sección. No hace falta cuenta.",
          ),
        ),
        h(
          "div",
          { class: "xr-anot-contador", id: "xr-anot-contador", hidden: true },
          h("span", { id: "xr-anot-num" }, "0"),
          " anotaciones",
        ),
      ),
      h("div", { class: "xr-anot-recibida", id: "xr-anot-recibida", hidden: true }),
      h("div", { class: "xr-anot-lista", id: "xr-anot-lista", role: "list" }),
      h(
        "p",
        { class: "xr-anot-vacio", id: "xr-anot-vacio" },
        "Todavía no hay anotaciones en esta nota. Las que escribas quedan guardadas en este navegador y puedes compartirlas con el botón de enlace.",
      ),
      h(
        "form",
        { class: "xr-anot-form", id: "xr-anot-form", novalidate: true },
        h(
          "div",
          { class: "xr-anot-fila" },
          h(
            "label",
            { class: "xr-anot-campo" },
            h("span", null, "Sección"),
            h("select", { id: "xr-anot-seccion", name: "seccion" }),
          ),
          h(
            "label",
            { class: "xr-anot-campo" },
            h("span", null, "Tu nombre (opcional)"),
            h("input", {
              id: "xr-anot-autor",
              name: "autor",
              type: "text",
              maxlength: 40,
              autocomplete: "nickname",
              placeholder: "Anónimo",
            }),
          ),
        ),
        h(
          "label",
          { class: "xr-anot-campo" },
          h("span", null, "Anotación"),
          h("textarea", {
            id: "xr-anot-texto",
            name: "texto",
            rows: 3,
            required: true,
            maxlength: 2000,
            placeholder: "Duda, corrección, matiz o ejemplo. Cita si puedes.",
          }),
        ),
        h(
          "div",
          { class: "xr-anot-acciones" },
          h("button", { class: "xr-boton xr-boton-primario", type: "submit" }, "Publicar anotación"),
          h("button", { class: "xr-boton", type: "button", id: "xr-anot-exportar" }, "Exportar"),
          h("label", { class: "xr-boton xr-anot-importar" }, "Importar", h("input", {
            type: "file",
            id: "xr-anot-importar-input",
            accept: "application/json,.json",
            hidden: true,
          })),
          h(
            "span",
            { class: "xr-anot-estado", id: "xr-anot-estado", role: "status", "aria-live": "polite" },
          ),
        ),
      ),
      h(
        "p",
        { class: "xr-anot-pie" },
        fm.endpoint_anotaciones
          ? "Las anotaciones se guardan en el servidor compartido del sitio: cualquiera que abra esta página las verá."
          : "Las anotaciones se guardan en este navegador. El botón «enlace para compartir» crea una dirección que lleva la anotación dentro: quien la abra la verá y podrá guardarla, sin cuenta.",
      ),
      fm.endpoint_anotaciones
        ? null
        : h(
            "p",
            { class: "xr-anot-pie" },
            "Lo que no hay es un muro público: las anotaciones no aparecen solas a los demás, se comparten una a una por enlace. Para eso hace falta un punto de guardado compartido, documentado en el LEEME.",
          ),
    )
  }
  Comp.css = `
.xr-anot {
  margin: 2.75rem 0 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--lightgray);
}
.xr-anot-cab { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.xr-anot-titulo { margin: 0; font-size: 1.25rem; }
.xr-anot-sub { margin: 0.15rem 0 1rem; font-size: 0.82rem; color: var(--gray); }
.xr-anot-contador { font-size: 0.76rem; color: var(--gray); font-variant-numeric: tabular-nums; }
.xr-anot-lista { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 0.5rem; }
.xr-anot-recibida {
  border: 1px solid var(--secondary);
  border-radius: 9px;
  padding: 0.7rem 0.85rem;
  margin-bottom: 1rem;
  background: var(--xr-accent-soft);
}
.xr-anot-recibida[hidden] { display: none; }
.xr-anot-recibida .xr-anot-acciones { margin-top: 0.6rem; }
.xr-anot-vacio { font-size: 0.85rem; color: var(--gray); margin: 0 0 1.1rem; }
.xr-anot-item {
  border: 1px solid var(--lightgray);
  border-radius: 8px;
  padding: 0.65rem 0.8rem;
  background: var(--xr-surface, var(--light));
  transition: border-color 120ms ease, box-shadow 120ms ease;
}
.xr-anot-item:hover {
  border-color: color-mix(in srgb, var(--secondary) 40%, var(--lightgray));
  box-shadow: 0 2px 10px -6px rgb(0 0 0 / 0.25);
}
/* Anotación recién añadida: se asienta, para que se vea que entró. */
@keyframes xr-anot-entra {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: none; }
}
.xr-anot-item[data-nueva="1"] { animation: xr-anot-entra 200ms cubic-bezier(0.16, 1, 0.3, 1) both; }
/* La de otro sitio se marca con un tinte, no con una barra de color: una barra
   lateral de 3 px es el adorno por defecto de la categoría. */
.xr-anot-item[data-destino="1"] { background: var(--xr-warn-soft, transparent); border-color: color-mix(in srgb, var(--xr-warn, #c98a00) 45%, var(--lightgray)); }
.xr-anot-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 0.45rem; font-size: 0.72rem; color: var(--gray); margin-bottom: 0.3rem; }
.xr-anot-autor { font-weight: 600; color: var(--darkgray); }
.xr-anot-sec {
  color: var(--secondary);
  text-decoration: none;
  border-bottom: 1px dotted var(--secondary);
}
.xr-anot-texto { font-size: 0.9rem; color: var(--darkgray); white-space: pre-wrap; overflow-wrap: anywhere; }
.xr-anot-item-acc { display: flex; gap: 0.4rem; margin-top: 0.45rem; opacity: 0.55; transition: opacity 120ms ease; }
.xr-anot-item:hover .xr-anot-item-acc, .xr-anot-item:focus-within .xr-anot-item-acc { opacity: 1; }
.xr-anot-mini {
  font: inherit; font-size: 0.7rem; background: none; border: 0; color: var(--gray);
  cursor: pointer; padding: 0.1rem 0.25rem; border-radius: 5px;
}
.xr-anot-mini:hover { background: var(--highlight); color: var(--dark); }
.xr-anot-form {
  margin-top: 1.1rem;
  padding: 1rem;
  border: 1px solid var(--lightgray);
  border-radius: 10px;
  background: var(--xr-surface, var(--light));
  display: flex; flex-direction: column; gap: 0.7rem;
}
.xr-anot-fila { display: flex; gap: 0.7rem; flex-wrap: wrap; }
.xr-anot-campo { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.74rem; color: var(--gray); flex: 1 1 180px; }
/* flex-basis en una columna es ALTURA, no anchura.
   Los campos que cuelgan directamente del formulario (que es
   flex-direction: column) salían de 180 px de alto y el formulario ocupaba
   media pantalla. Y no bastaba con corregir el escritorio: en móvil
   .xr-anot-fila pasa a columna, así que sus dos campos volvían a heredar el
   180px de altura. Se anula en los dos sitios donde el eje es vertical. */
.xr-anot-form > .xr-anot-campo,
.xr-anot-fila > .xr-anot-campo { flex: 0 0 auto; }
.xr-anot-campo select, .xr-anot-campo input, .xr-anot-campo textarea {
  font: inherit; font-size: 0.88rem; color: var(--dark);
  background: var(--light); border: 1px solid var(--lightgray); border-radius: 7px;
  padding: 0.42rem 0.55rem; width: 100%; box-sizing: border-box;
}
.xr-anot-campo textarea { resize: vertical; min-height: 4.2rem; }
.xr-anot-campo select:focus, .xr-anot-campo input:focus, .xr-anot-campo textarea:focus {
  outline: 2px solid var(--xr-accent, var(--secondary)); outline-offset: 1px; border-color: transparent;
}
.xr-anot-acciones { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; }
.xr-boton-primario { background: var(--secondary); border-color: var(--secondary); color: var(--light); font-weight: 600; }
.xr-boton-primario:hover { background: var(--dark); border-color: var(--dark); color: var(--light); }
.xr-anot-importar { cursor: pointer; }
.xr-anot-estado { font-size: 0.74rem; color: var(--tertiary); }
.xr-anot-pie { margin: 0.9rem 0 0; font-size: 0.74rem; color: var(--gray); line-height: 1.5; }
.xr-anot-ancla {
  margin-left: 0.35rem; font-size: 0.7rem; font-weight: 400; opacity: 0;
  border: 0; background: none; color: var(--gray); cursor: pointer;
  transition: opacity 120ms ease;
}
h2:hover > .xr-anot-ancla, h3:hover > .xr-anot-ancla, .xr-anot-ancla:focus { opacity: 1; }
@media (max-width: 800px) {
  .xr-anot-fila { flex-direction: column; }
}
`

  Comp.afterDOMLoaded = `
(function () {
  if (window.__xrAnot) return;
  window.__xrAnot = true;

  function clave(nota) { return "xr:anot:" + nota; }
  function leer(nota) {
    try {
      var raw = localStorage.getItem(clave(nota));
      var v = raw ? JSON.parse(raw) : [];
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  function guardar(nota, lista) {
    try { localStorage.setItem(clave(nota), JSON.stringify(lista)); return true; }
    catch (e) { return false; }
  }
  // Enlace compartible: la anotación viaja dentro de la propia URL, comprimida
  // y codificada en base64url. Cualquiera que abra el enlace la ve, sin cuenta
  // y sin servidor: el dato está en el enlace, no en una base de datos.
  //
  // Coste honesto: la dirección queda larga (~200 caracteres para una
  // anotación normal) y sigue siendo un enlace, no un muro público donde
  // aparezcan solas las anotaciones de los demás.
  function aBase64Url(txt) {
    var bytes = new TextEncoder().encode(txt);
    var bin = "";
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin).split("+").join("-").split("/").join("_").split("=").join("");
  }

  function deBase64Url(txt) {
    var b = txt.split("-").join("+").split("_").join("/");
    while (b.length % 4) b += "=";
    var bin = atob(b);
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }

  function enlaceDe(a) {
    var datos = { t: a.texto, n: a.autor || "", s: a.seccion || "", st: a.seccionTexto || "" };
    return location.origin + location.pathname + "#a=" + aBase64Url(JSON.stringify(datos));
  }

  function leerEnlace() {
    var h = location.hash || "";
    if (h.indexOf("#a=") !== 0) return null;
    try {
      var d = JSON.parse(deBase64Url(h.slice(3)));
      if (!d || !d.t) return null;
      return {
        id: "enlace-" + aBase64Url(d.t).slice(0, 12),
        ts: 0, autor: d.n || "", texto: d.t,
        seccion: d.s || "", seccionTexto: d.st || "",
        compartida: true,
      };
    } catch (e) { return null; }
  }

  function uid() {
    return "a" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }
  function fecha(ts) {
    try {
      return new Date(ts).toLocaleString("es-ES", {
        day: "2-digit", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      });
    } catch (e) { return ""; }
  }

  function secciones(root) {
    var out = [{ id: "", texto: "Nota completa" }];
    root.querySelectorAll("h2[id], h3[id]").forEach(function (h) {
      var t = (h.textContent || "").trim();
      if (!t) return;
      if (h.closest(".xr-anot")) return;
      out.push({ id: h.id, texto: t });
    });
    return out;
  }

  function pintar(contenedor, lista, nota, nueva) {
    contenedor.innerHTML = "";
    var orden = lista.slice().sort(function (a, b) { return a.ts - b.ts; });
    orden.forEach(function (a) {
      var item = document.createElement("div");
      item.className = "xr-anot-item";
      item.setAttribute("role", "listitem");
      item.id = "anot-" + a.id;
      if (a.destino) item.dataset.destino = "1";
      // La que se acaba de escribir entra con un movimiento corto; el resto de
      // la lista ya estaba y no debe volver a animarse.
      if (nueva && a.id === nueva) item.dataset.nueva = "1";
      var meta = document.createElement("div");
      meta.className = "xr-anot-meta";
      var autor = document.createElement("span");
      autor.className = "xr-anot-autor";
      autor.textContent = a.autor || "Anónimo";
      meta.appendChild(autor);
      var cuando = document.createElement("span");
      cuando.textContent = fecha(a.ts);
      meta.appendChild(cuando);
      if (a.seccionTexto) {
        var sec = document.createElement(a.seccion ? "a" : "span");
        sec.className = "xr-anot-sec";
        sec.textContent = "§ " + a.seccionTexto;
        if (a.seccion) sec.href = "#" + a.seccion;
        meta.appendChild(sec);
      }
      item.appendChild(meta);
      var txt = document.createElement("div");
      txt.className = "xr-anot-texto";
      txt.textContent = a.texto;
      item.appendChild(txt);
      var acc = document.createElement("div");
      acc.className = "xr-anot-item-acc";
      var bEnlace = document.createElement("button");
      bEnlace.className = "xr-anot-mini";
      bEnlace.type = "button";
      bEnlace.textContent = "copiar enlace";
      bEnlace.textContent = "enlace para compartir";
      bEnlace.addEventListener("click", function () {
        copiar(enlaceDe(a), bEnlace, "enlace copiado");
      });
      var bCita = document.createElement("button");
      bCita.className = "xr-anot-mini";
      bCita.type = "button";
      bCita.textContent = "copiar texto";
      bCita.addEventListener("click", function () {
        copiar("«" + a.texto + "» — " + (a.autor || "Anónimo") + ", " + nota, bCita, "copiado");
      });
      var bBorrar = document.createElement("button");
      bBorrar.className = "xr-anot-mini";
      bBorrar.type = "button";
      bBorrar.textContent = "borrar";
      bBorrar.addEventListener("click", function () {
        if (!confirm("¿Borrar esta anotación de este navegador?")) return;
        var nueva = leer(nota).filter(function (x) { return x.id !== a.id; });
        guardar(nota, nueva);
        pintar(contenedor, nueva, nota);
        actualizarContador(nueva);
      });
      acc.appendChild(bEnlace);
      acc.appendChild(bCita);
      acc.appendChild(bBorrar);
      item.appendChild(acc);
      contenedor.appendChild(item);
    });
  }

  function copiar(texto, boton, ok) {
    var listo = function () {
      var prev = boton.textContent;
      boton.textContent = ok;
      setTimeout(function () { boton.textContent = prev; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(listo).catch(function () {});
    } else {
      var ta = document.createElement("textarea");
      ta.value = texto; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); listo(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }

  function actualizarContador(lista) {
    var num = document.getElementById("xr-anot-num");
    var cont = document.getElementById("xr-anot-contador");
    var vacio = document.getElementById("xr-anot-vacio");
    if (num) num.textContent = String(lista.length);
    if (cont) cont.hidden = lista.length === 0;
    if (vacio) vacio.hidden = lista.length > 0;
  }

  // Guardado compartido opcional.
  //
  // Si la nota declara endpoint_anotaciones en el frontmatter, las
  // anotaciones viajan a un servidor propio además de al navegador. El sitio
  // no trae uno porque un servicio público anónimo no garantiza permanencia y
  // prometerlo sería mentir: cuando no hay endpoint, todo se queda en local y
  // la interfaz lo dice con todas las letras.
  function endpoint(root) {
    var e = (root.getAttribute("data-endpoint") || "").trim();
    // Se comprueba con indexOf en vez de un regex: dentro de una plantilla de
    // JS, las barras invertidas del regex se pierden y el patrón queda roto.
    return e.indexOf("http://") === 0 || e.indexOf("https://") === 0 ? e : "";
  }

  function enviar(url, lista, estado) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nota: document.body.dataset.nota || location.pathname, anotaciones: lista }),
    }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return true;
    }).catch(function (e) {
      if (estado) estado.textContent = "No se pudo enviar al servidor compartido; queda guardada en este navegador.";
      return false;
    });
  }

  function init() {
    var root = document.querySelector(".xr-anot");
    if (!root || root.dataset.iniciado === "1") return;
    root.dataset.iniciado = "1";
    var nota = root.getAttribute("data-nota") || location.pathname;
    var lista = leer(nota);
    var contenedor = root.querySelector("#xr-anot-lista");
    var select = root.querySelector("#xr-anot-seccion");
    var form = root.querySelector("#xr-anot-form");
    var estado = root.querySelector("#xr-anot-estado");
    var articulo = document.querySelector("article") || document.body;

    // Secciones disponibles.
    var secs = secciones(articulo);
    secs.forEach(function (s) {
      var o = document.createElement("option");
      o.value = s.id;
      o.textContent = s.texto;
      select.appendChild(o);
    });

    // Botón para anotar junto a cada encabezado.
    articulo.querySelectorAll("h2[id], h3[id]").forEach(function (h) {
      if (h.closest(".xr-anot") || h.querySelector(".xr-anot-ancla")) return;
      var b = document.createElement("button");
      b.className = "xr-anot-ancla";
      b.type = "button";
      b.title = "Anotar en esta sección";
      b.textContent = "✎ anotar";
      b.addEventListener("click", function () {
        select.value = h.id;
        document.getElementById("anotaciones").scrollIntoView({ behavior: "smooth" });
        var ta = document.getElementById("xr-anot-texto");
        if (ta) setTimeout(function () { ta.focus(); }, 350);
      });
      h.appendChild(b);
    });

    // Si la URL trae una anotación compartida, se ofrece guardarla.
    var recibida = leerEnlace();
    var cajaRecibida = root.querySelector("#xr-anot-recibida");
    if (recibida && cajaRecibida) {
      var yaEsta = lista.some(function (x) { return x.texto === recibida.texto && x.autor === recibida.autor; });
      if (!yaEsta) {
        cajaRecibida.hidden = false;
        cajaRecibida.innerHTML = "";
        var titulo = document.createElement("div");
        titulo.className = "xr-anot-meta";
        titulo.innerHTML = '<span class="xr-anot-autor">Anotación compartida</span>';
        cajaRecibida.appendChild(titulo);
        var cuerpo = document.createElement("div");
        cuerpo.className = "xr-anot-texto";
        cuerpo.textContent = recibida.texto;
        cajaRecibida.appendChild(cuerpo);
        var pie = document.createElement("div");
        pie.className = "xr-anot-meta";
        if (recibida.autor) {
          var q = document.createElement("span");
          q.textContent = "de " + recibida.autor;
          pie.appendChild(q);
        }
        if (recibida.seccionTexto) {
          var sec = document.createElement("a");
          sec.className = "xr-anot-sec";
          sec.href = "#" + recibida.seccion;
          sec.textContent = "§ " + recibida.seccionTexto;
          pie.appendChild(sec);
        }
        cajaRecibida.appendChild(pie);
        var acc = document.createElement("div");
        acc.className = "xr-anot-acciones";
        var bGuardar = document.createElement("button");
        bGuardar.className = "xr-boton xr-boton-primario";
        bGuardar.type = "button";
        bGuardar.textContent = "Guardar en este navegador";
        bGuardar.addEventListener("click", function () {
          var n = leer(nota);
          recibida.id = uid();
          recibida.ts = new Date().getTime();
          recibida.compartida = false;
          n.push(recibida);
          guardar(nota, n);
          cajaRecibida.hidden = true;
          pintar(contenedor, n, nota);
          actualizarContador(n);
        });
        var bCerrar = document.createElement("button");
        bCerrar.className = "xr-boton";
        bCerrar.type = "button";
        bCerrar.textContent = "Descartar";
        bCerrar.addEventListener("click", function () { cajaRecibida.hidden = true; });
        acc.appendChild(bGuardar);
        acc.appendChild(bCerrar);
        cajaRecibida.appendChild(acc);
      }
    }

    pintar(contenedor, lista, nota);
    actualizarContador(lista);

    // Si hay servidor compartido, se mezclan sus anotaciones con las locales.
    var urlCompartida = endpoint(root);
    if (urlCompartida) {
      fetch(urlCompartida + (urlCompartida.indexOf("?") === -1 ? "?" : "&") + "nota=" + encodeURIComponent(nota))
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          var remotas = (d && (d.anotaciones || d)) || [];
          if (!Array.isArray(remotas) || !remotas.length) return;
          var vistas = {};
          lista.forEach(function (x) { vistas[x.id] = 1; });
          remotas.forEach(function (x) { if (x && x.texto && !vistas[x.id]) lista.push(x); });
          guardar(nota, lista);
          pintar(contenedor, lista, nota);
          actualizarContador(lista);
        })
        .catch(function () {});
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var texto = (document.getElementById("xr-anot-texto").value || "").trim();
      if (!texto) {
        estado.textContent = "Escribe algo antes de publicar.";
        return;
      }
      var autor = (document.getElementById("xr-anot-autor").value || "").trim();
      var seccion = select.value;
      var seccionTexto = select.options[select.selectedIndex]
        ? select.options[select.selectedIndex].textContent
        : "";
      var nueva = leer(nota);
      var creada = {
        id: uid(), ts: Date.now(), autor: autor, texto: texto,
        seccion: seccion, seccionTexto: seccionTexto,
      };
      nueva.push(creada);
      if (!guardar(nota, nueva)) {
        estado.textContent = "No se pudo guardar (almacenamiento lleno o bloqueado).";
        return;
      }
      document.getElementById("xr-anot-texto").value = "";
      estado.textContent = "Anotación guardada en este navegador.";
      var url = endpoint(root);
      if (url) enviar(url, nueva, estado);
      pintar(contenedor, nueva, nota, creada.id);
      actualizarContador(nueva);
      setTimeout(function () { estado.textContent = ""; }, 3200);
    });

    root.querySelector("#xr-anot-exportar").addEventListener("click", function () {
      var datos = { nota: nota, exportado: new Date().toISOString(), anotaciones: leer(nota) };
      var blob = new Blob([JSON.stringify(datos, null, 1)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "anotaciones-" + nota.split("/").join("-") + ".json";
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1500);
    });

    root.querySelector("#xr-anot-importar-input").addEventListener("change", function (e) {
      var f = e.target.files && e.target.files[0];
      if (!f) return;
      var fr = new FileReader();
      fr.onload = function () {
        try {
          var d = JSON.parse(fr.result);
          var entrantes = d.anotaciones || d;
          if (!Array.isArray(entrantes)) throw new Error("formato");
          var actual = leer(nota);
          var ids = {};
          actual.forEach(function (x) { ids[x.id] = 1; });
          var n = 0;
          entrantes.forEach(function (x) {
            if (!x || !x.texto) return;
            if (ids[x.id]) return;
            actual.push({
              id: x.id || uid(), ts: x.ts || Date.now(),
              autor: x.autor || "", texto: x.texto,
              seccion: x.seccion || "", seccionTexto: x.seccionTexto || "",
            });
            n++;
          });
          guardar(nota, actual);
          pintar(contenedor, actual, nota);
          actualizarContador(actual);
          estado.textContent = n + " anotaciones importadas.";
        } catch (err) {
          estado.textContent = "El archivo no tiene el formato esperado.";
        }
      };
      fr.readAsText(f);
    });

    // Enlace directo a una anotación.
    if (location.hash.indexOf("#anot-") === 0) {
      var el = document.getElementById(location.hash.slice(1));
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.style.outline = "2px solid var(--secondary)";
      }
    }
  }

  document.addEventListener("nav", init);
  document.addEventListener("render", init);
  init();
})();
`

  return Comp
}

export { Anotaciones }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revisión asistida de las capturas publicadas.

Genera una hoja HTML con **todas** las imágenes que el sitio publica, cada una
con el concepto que ilustra, la definición, la anotación y los enlaces al vídeo.
Sirve para mirar el material de un tirón y marcar lo que no cuadra sin abrir
cincuenta pestañas.

Por qué existe
--------------
La regla del generador solo puede leer anotaciones: sabe si el texto nombra el
concepto o dice que no se ve, pero no puede distinguir una diapositiva de otro
tema de la que dice ser. Eso solo se ve mirando la imagen. Esta hoja hace esa
revisión barata:

1. `python 09_AUTOMATION/revisar_capturas.py`  → escribe la hoja
2. Abrir `09_AUTOMATION/.tmp/revision/index.html`
3. Marcar «descartar» en lo que no corresponda
4. Pulsar «Descargar veredictos» y pasarlos a
   `python 09_AUTOMATION/vetar_fotogramas.py --veredictos veredictos.json`

La hoja no decide nada: no hay veredicto automático.
"""

import base64
import json
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regenerar_vault import connect, confianza, mmss, slug, VAULT  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(VAULT, "media")
SALIDA = os.path.join(BASE, "09_AUTOMATION", ".tmp", "revision")


def datos(con):
    slugs = {slug(r["name"]): r for r in con.execute(
        "SELECT id, name, definition, how_identify, certainty, category FROM concepts")}
    filas = []
    for nombre in sorted(os.listdir(MEDIA)):
        if not nombre.endswith(".webp"):
            continue
        m = re.match(r"(.+)-(\d+)\.webp$", nombre)
        if not m:
            continue
        slug_c, fid = m.group(1), int(m.group(2))
        fr = con.execute("SELECT * FROM frames WHERE id=?", (fid,)).fetchone()
        if not fr:
            continue
        c = slugs.get(slug_c)
        v = con.execute("SELECT title, category FROM videos WHERE id=?", (fr["video_id"],)).fetchone()
        filas.append({
            "webp": nombre,
            "concepto": c["name"] if c else slug_c,
            "definicion": c["definition"] if c else "",
            "identificar": c["how_identify"] if c else "",
            "confianza": confianza(c["certainty"]) if c else "",
            "anotacion": fr["description"] or "",
            "video": fr["video_id"] or "",
            "video_titulo": v["title"] if v else "",
            "categoria": v["category"] if v else "",
            "ts": mmss(fr["timestamp_sec"]),
        })
    return filas


def html(filas):
    por_concepto = {}
    for f in filas:
        por_concepto.setdefault(f["concepto"], []).append(f)

    tarjetas = []
    for concepto in sorted(por_concepto):
        grupo = por_concepto[concepto]
        tarjetas.append(
            f'<h2 class="sec">{concepto} <span class="cuenta">{len(grupo)}</span></h2>'
        )
        tarjetas.append('<p class="def">' + (grupo[0]["definicion"] or "") + "</p>")
        if grupo[0]["identificar"]:
            tarjetas.append('<p class="ident"><b>Cómo se identifica:</b> '
                            + grupo[0]["identificar"] + "</p>")
        for f in grupo:
            ruta = os.path.join(MEDIA, f["webp"])
            with open(ruta, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            tarjetas.append(f"""
<figure class="cap" data-webp="{f['webp']}">
  <img src="data:image/webp;base64,{b64}" alt="{concepto}" loading="lazy">
  <figcaption>
    <div class="meta">
      <code>{f['webp']}</code>
      <span class="pill">{f['categoria'] or '—'}</span>
      <span class="pill">{f['ts']}</span>
      <a href="https://www.youtube.com/watch?v={f['video']}" target="_blank" rel="noopener">{f['video_titulo'][:60]}</a>
    </div>
    <p class="anot"><b>Anotación:</b> {f['anotacion'][:400]}</p>
    <div class="votos">
      <button type="button" data-v="muestra" class="b ok">Muestra el concepto</button>
      <button type="button" data-v="contexto" class="b mid">Solo contexto</button>
      <button type="button" data-v="descartar" class="b bad">Descartar</button>
    </div>
  </figcaption>
</figure>""")

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Revisión de capturas</title>
<style>
:root {{ color-scheme: light dark; }}
body {{ font: 15px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif; margin: 0; background:#111; color:#eee; }}
header {{ position: sticky; top:0; background:#181818; padding:.9rem 1.2rem; border-bottom:1px solid #333; z-index:5; display:flex; gap:1rem; align-items:center; flex-wrap:wrap }}
h1 {{ font-size: 1rem; margin:0; letter-spacing:.02em }}
main {{ padding: 1rem 1.2rem 6rem; max-width: 1100px; margin:0 auto }}
.sec {{ margin: 2rem 0 .3rem; font-size: 1.05rem; border-top:1px solid #333; padding-top:1.2rem }}
.cuenta {{ font-size:.7rem; background:#2a2a2a; padding:.1rem .45rem; border-radius:99px; color:#aaa; vertical-align:middle }}
.def {{ color:#bdbdbd; margin:.2rem 0 }}
.ident {{ color:#9e9e9e; font-size:.86rem; margin:.1rem 0 1rem }}
.cap {{ margin: 0 0 1.6rem; background:#1b1b1b; border:1px solid #2e2e2e; border-radius:10px; overflow:hidden }}
.cap img {{ display:block; width:100%; height:auto }}
figcaption {{ padding:.7rem .9rem .9rem }}
.meta {{ display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; font-size:.75rem; color:#9a9a9a }}
.meta code {{ background:#262626; padding:.1rem .35rem; border-radius:4px; color:#cfcfcf }}
.meta a {{ color:#7aa7d8; text-decoration:none }}
.pill {{ border:1px solid #3a3a3a; padding:0 .4rem; border-radius:99px }}
.anot {{ font-size:.82rem; color:#b9b9b9; margin:.5rem 0 .7rem }}
.votos {{ display:flex; gap:.5rem; flex-wrap:wrap }}
.b {{ font:inherit; font-size:.8rem; padding:.32rem .7rem; border-radius:7px; border:1px solid #3a3a3a; background:#232323; color:#ddd; cursor:pointer }}
.b:hover {{ background:#2c2c2c }}
.cap[data-veredicto="muestra"] {{ border-color:#2f7a58 }}
.cap[data-veredicto="muestra"] .b.ok {{ background:#2f7a58; border-color:#2f7a58; color:#fff }}
.cap[data-veredicto="contexto"] {{ border-color:#8a6d1f }}
.cap[data-veredicto="contexto"] .b.mid {{ background:#8a6d1f; border-color:#8a6d1f; color:#fff }}
.cap[data-veredicto="descartar"] {{ border-color:#a33 }}
.cap[data-veredicto="descartar"] .b.bad {{ background:#a33; border-color:#a33; color:#fff }}
.cap[data-veredicto="descartar"] img {{ opacity:.45 }}
#estado {{ font-size:.8rem; color:#9a9a9a }}
button.principal {{ font:inherit; font-size:.85rem; padding:.4rem .9rem; border-radius:8px; border:1px solid #4a7a5e; background:#2f7a58; color:#fff; cursor:pointer }}
</style></head>
<body>
<header>
  <h1>Revisión de capturas — {len(filas)} imágenes</h1>
  <span id="estado">0 marcadas</span>
  <button class="principal" id="descargar">Descargar veredictos</button>
</header>
<main>
<p style="color:#9a9a9a;font-size:.85rem">Mira cada captura y compara con la definición. Marca solo lo que hayas mirado; lo que dejes sin marcar se queda como está. El archivo que descargas se pasa a <code>vetar_fotogramas.py --veredictos</code>.</p>
{''.join(tarjetas)}
</main>
<script>
const votos = {{}};
const cajas = [...document.querySelectorAll('.cap')];
function refrescar() {{
  document.getElementById('estado').textContent = Object.keys(votos).length + ' marcadas';
}}
cajas.forEach(c => {{
  c.querySelectorAll('.b').forEach(b => {{
    b.addEventListener('click', () => {{
      const w = c.dataset.webp, v = b.dataset.v;
      if (votos[w] === v) {{ delete votos[w]; delete c.dataset.veredicto; }}
      else {{ votos[w] = v; c.dataset.veredicto = v; }}
      refrescar();
    }});
  }});
}});
document.getElementById('descargar').addEventListener('click', () => {{
  const salida = cajas.filter(c => votos[c.dataset.webp]).map(c => ({{
    webp: c.dataset.webp,
    veredicto: votos[c.dataset.webp],
    motivo: 'revisión visual (' + votos[c.dataset.webp] + ')',
  }}));
  const blob = new Blob([JSON.stringify(salida, null, 1)], {{type:'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'veredictos.json';
  a.click();
}});
</script>
</body></html>"""


def main():
    con = connect()
    filas = datos(con)
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, "index.html")
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(html(filas))
    tam = os.path.getsize(ruta) / (1024 * 1024)
    print(f"Capturas: {len(filas)}")
    print(f"Hoja:     {ruta}  ({tam:.1f} MB)")
    print("Ábrela en el navegador, marca lo que no cuadre y descarga los veredictos.")
    return 0


# --------------------------------------------------------------------------
# Tanda de conceptos sin imagen
# --------------------------------------------------------------------------

# Conceptos que no tienen ninguna ilustración y **sí** se pueden fotografiar.
# Quedan fuera a propósito:
#   - los de categoría NOT USED (RSI, MACD, Elliott…): Xavi declara que no los
#     usa, así que no hay nada suyo que ilustrar;
#   - los de psicología (Ego, FOMO, Revenge Trading…): no se ven en un gráfico.
CONCEPTOS_SIN_IMAGEN = [
    "PD Array",
    "Key Levels",
    "PDH / PDL (previous day high/low)",
    "Protected High / Low",
    "Rejection Block",
    "Cuentas de fondeo",
    "Sesión de Nueva York",
    "No News Monday",
    "Bank Holiday (festivo EE. UU.)",
]

# Palabras que, si aparecen en una anotación, hacen sospechar que el fotograma
# muestra el concepto. Son pistas para ordenar la revisión, no un veredicto: la
# hoja las marca y la persona decide.
PISTAS = {
    "PD Array": ["pd array", "array", "po3", "premium", "discount"],
    "Key Levels": ["key level", "nivel clave", "niveles", "liquidez", "fvg"],
    "PDH / PDL (previous day high/low)": ["pdh", "pdl", "previous day", "día anterior"],
    "Protected High / Low": ["protected", "protegido"],
    "Rejection Block": ["rejection", "rechazo"],
    "Cuentas de fondeo": ["fondeo", "prop firm", "evaluación", "payout"],
    "Sesión de Nueva York": ["nueva york", "new york", "ny ", "9:30", "9:45"],
    "No News Monday": ["no news", "lunes sin noticias"],
    "Bank Holiday (festivo EE. UU.)": ["bank holiday", "festivo", "holiday"],
}


def tanda(con, concepto_filtro=None):
    """Fotogramas de los vídeos del concepto que todavía no están anotados.

    El criterio: si una clase habla de «Key Levels» y tiene 12 fotogramas sin
    anotar, esos 12 son los candidatos —nadie los ha mirado todavía—. Lo que ya
    está anotado y no menciona el concepto se descarta: si la anotación
    describe otra cosa, mirarlo otra vez no lo va a convertir en prueba.
    """
    conceptos = concepto_filtro or CONCEPTOS_SIN_IMAGEN
    filas = []
    for nombre in conceptos:
        c = con.execute(
            "SELECT id, name, definition, how_identify, certainty, category "
            "FROM concepts WHERE name=?", (nombre,)
        ).fetchone()
        if not c:
            continue
        vids = [r[0] for r in con.execute(
            "SELECT DISTINCT video_id FROM evidence "
            "WHERE entity_type='concept' AND entity_id=?", (c["id"],)
        )]
        if not vids:
            continue
        marcas = ",".join("?" * len(vids))
        frames = con.execute(
            "SELECT * FROM frames WHERE video_id IN (" + marcas + ") "
            "AND lower(coalesce(description,'')) LIKE 'pendiente de anotaci%' "
            "ORDER BY video_id, timestamp_sec", vids
        ).fetchall()
        for fr in frames:
            v = con.execute(
                "SELECT title, category FROM videos WHERE id=?", (fr["video_id"],)
            ).fetchone()
            ruta_img = os.path.join(BASE, fr["path"]) if fr["path"] else None
            if not ruta_img or not os.path.exists(ruta_img):
                continue
            filas.append({
                "concepto": nombre,
                "definicion": c["definition"] or "",
                "identificar": c["how_identify"] or "",
                "anotacion": fr["description"] or "",
                "path": ruta_img,
                "frame_id": fr["id"],
                "video": fr["video_id"],
                "video_titulo": v["title"] if v else "",
                "categoria": v["category"] if v else "",
                "ts": mmss(fr["timestamp_sec"]),
                "pistas": PISTAS.get(nombre, []),
            })
    return filas


def html_tanda(filas):
    """Hoja de revisión que además permite ANOTAR, no solo vetar.

    Las capturas pendientes no tienen anotación: si solo se pudiera marcar
    «sirve / no sirve», se perdería lo que se ve en ellas. Aquí se escribe la
    descripción y la hoja genera el JSON que `vetar_fotogramas.py --anotar`
    acepta, para que la anotación entre a la base sin inventarla.
    """
    por_concepto = {}
    for f in filas:
        por_concepto.setdefault(f["concepto"], []).append(f)

    bloques = []
    for concepto in sorted(por_concepto):
        grupo = por_concepto[concepto]
        bloques.append(
            f'<h2 class="sec">{concepto} <span class="cuenta">{len(grupo)} sin revisar</span></h2>'
        )
        bloques.append('<p class="def">' + (grupo[0]["definicion"] or "") + "</p>")
        if grupo[0]["identificar"]:
            bloques.append('<p class="ident"><b>Cómo se identifica:</b> '
                           + grupo[0]["identificar"] + "</p>")
        pistas = ", ".join(grupo[0]["pistas"])
        if pistas:
            bloques.append(f'<p class="pistas">Pistas en la anotación: {pistas}</p>')
        for f in grupo:
            with open(f["path"], "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            ext = os.path.splitext(f["path"])[1].lstrip(".").lower()
            mime = "image/webp" if ext == "webp" else f"image/{ext}"
            bloques.append(f"""
<figure class="cap" data-frame="{f['frame_id']}" data-concepto="{concepto}">
  <img src="data:{mime};base64,{b64}" alt="frame {f['frame_id']}" loading="lazy">
  <figcaption>
    <div class="meta">
      <code>frame {f['frame_id']}</code>
      <span class="pill">{f['categoria'] or '—'}</span>
      <span class="pill">{f['ts']}</span>
      <a href="https://www.youtube.com/watch?v={f['video']}&t={int(f['ts'].split(':')[0])*60+int(f['ts'].split(':')[1]) if ':' in f['ts'] else 0}s" target="_blank" rel="noopener">{f['video_titulo'][:60]}</a>
    </div>
    <label class="campo">¿Qué se ve? (si no muestra el concepto, escribe «no»)
      <textarea rows="2" data-desc placeholder="Describe lo que ves en pantalla…"></textarea>
    </label>
    <div class="votos">
      <button type="button" class="b ok" data-v="muestra">Muestra el concepto</button>
      <button type="button" class="b no" data-v="descartar">No sirve</button>
    </div>
  </figcaption>
</figure>""")

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Tanda — conceptos sin imagen</title>
<style>
:root {{ color-scheme: light dark; }}
body {{ font: 15px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif; margin:0; background:#111; color:#eee }}
header {{ position:sticky; top:0; background:#181818; padding:.9rem 1.2rem; border-bottom:1px solid #333; z-index:5; display:flex; gap:1rem; align-items:center; flex-wrap:wrap }}
h1 {{ font-size:1rem; margin:0 }}
main {{ padding:1rem 1.2rem 6rem; max-width:1100px; margin:0 auto }}
.sec {{ margin:2rem 0 .3rem; font-size:1.05rem; border-top:1px solid #333; padding-top:1.2rem }}
.cuenta {{ font-size:.7rem; background:#2a2a2a; padding:.1rem .45rem; border-radius:99px; color:#aaa }}
.def {{ color:#bdbdbd; margin:.2rem 0 }}
.ident {{ color:#9e9e9e; font-size:.86rem; margin:.1rem 0 }}
.pistas {{ color:#6f8fa8; font-size:.8rem; margin:.2rem 0 1rem }}
.cap {{ margin:0 0 1.6rem; background:#1b1b1b; border:1px solid #2e2e2e; border-radius:10px; overflow:hidden }}
.cap img {{ display:block; width:100%; height:auto }}
figcaption {{ padding:.7rem .9rem .9rem }}
.meta {{ display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; font-size:.75rem; color:#9a9a9a }}
.meta code {{ background:#262626; padding:.1rem .35rem; border-radius:4px; color:#cfcfcf }}
.meta a {{ color:#7aa7d8; text-decoration:none }}
.pill {{ border:1px solid #3a3a3a; padding:0 .4rem; border-radius:99px }}
.campo {{ display:block; font-size:.78rem; color:#aaa; margin:.6rem 0 .5rem }}
textarea {{ width:100%; box-sizing:border-box; font:inherit; font-size:.85rem; background:#232323; color:#eee;
  border:1px solid #3a3a3a; border-radius:7px; padding:.4rem .55rem; margin-top:.25rem; resize:vertical }}
.votos {{ display:flex; gap:.5rem; flex-wrap:wrap }}
.b {{ font:inherit; font-size:.8rem; padding:.32rem .7rem; border-radius:7px; border:1px solid #3a3a3a; background:#232323; color:#ddd; cursor:pointer }}
.cap[data-veredicto="muestra"] {{ border-color:#2f7a58 }}
.cap[data-veredicto="muestra"] .b.ok {{ background:#2f7a58; border-color:#2f7a58; color:#fff }}
.cap[data-veredicto="descartar"] {{ border-color:#a33 }}
.cap[data-veredicto="descartar"] .b.no {{ background:#a33; border-color:#a33; color:#fff }}
#estado {{ font-size:.8rem; color:#9a9a9a }}
button.principal {{ font:inherit; font-size:.85rem; padding:.4rem .9rem; border-radius:8px; border:1px solid #4a7a5e; background:#2f7a58; color:#fff; cursor:pointer }}
</style></head>
<body>
<header>
  <h1>Tanda — {len(filas)} fotogramas sin revisar de {len(por_concepto)} conceptos</h1>
  <span id="estado">0 marcadas</span>
  <button class="principal" id="descargar">Descargar anotaciones</button>
</header>
<main>
<p style="color:#9a9a9a;font-size:.85rem">
Estos fotogramas están en clases que hablan del concepto y nadie los ha mirado.
Escribe <b>qué se ve</b> en los que sirvan; en los que no, pulsa «No sirve».
Lo que dejes en blanco se queda como está. El JSON que descargas entra con
<code>vetar_fotogramas.py --anotar archivo.json</code>.
</p>
{''.join(bloques)}
</main>
<script>
const cajas = [...document.querySelectorAll('.cap')];
const estado = {{}};
function refrescar() {{
  document.getElementById('estado').textContent =
    Object.keys(estado).length + ' marcadas de ' + cajas.length;
}}
cajas.forEach(c => {{
  const ta = c.querySelector('textarea');
  const botones = c.querySelectorAll('.b');
  botones.forEach(b => b.addEventListener('click', () => {{
    const v = b.dataset.v;
    const actual = c.dataset.veredicto;
    if (actual === v) {{ delete c.dataset.veredicto; delete estado[c.dataset.frame]; }}
    else {{ c.dataset.veredicto = v; estado[c.dataset.frame] = {{v, d: ta.value}}; }}
    refrescar();
  }}));
  ta.addEventListener('input', () => {{
    if (estado[c.dataset.frame]) estado[c.dataset.frame].d = ta.value;
  }});
}});
document.getElementById('descargar').addEventListener('click', () => {{
  const salida = [];
  cajas.forEach(c => {{
    const e = estado[c.dataset.frame];
    const textoDeCaja = c.querySelector('textarea').value.trim();
    if (!e && !textoDeCaja) return;
    const veredicto = e ? e.v : (textoDeCaja ? 'muestra' : 'descartar');
    salida.push({{
      frame: Number(c.dataset.frame),
      concepto: c.dataset.concepto,
      veredicto: veredicto,
      descripcion: (e ? e.d : textoDeCaja) || '',
    }});
  }});
  const blob = new Blob([JSON.stringify(salida, null, 1)], {{type:'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'anotaciones.json';
  a.click();
}});
</script>
</body></html>"""


def main_tanda(con, concepto=None):
    filas = tanda(con, concepto)
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, "tanda.html")
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(html_tanda(filas))
    tam = os.path.getsize(ruta) / (1024 * 1024)
    print(f"Fotogramas sin revisar en clases de esos conceptos: {len(filas)}")
    print(f"Hoja: {ruta}  ({tam:.1f} MB)")
    print("Escribe lo que se ve, marca, descarga y pásalo a:")
    print("  python 09_AUTOMATION/vetar_fotogramas.py --anotar anotaciones.json")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Hoja de revisión de capturas.")
    ap.add_argument("--tanda", action="store_true",
                    help="Solo los conceptos sin imagen (por defecto, todas las publicadas)")
    ap.add_argument("--concepto", default=None, help="Un concepto concreto")
    args = ap.parse_args()
    con = connect()
    if args.tanda or args.concepto:
        raise SystemExit(main_tanda(con, args.concepto))
    raise SystemExit(main())

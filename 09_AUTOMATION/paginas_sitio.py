#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Páginas nuevas del sitio: bootcamp, índices por tipo y portada con panel.

Se separa de `regenerar_vault.py` para que ese archivo siga centrado en las
notas unitarias (concepto, regla, operación, cambio, pregunta). Aquí solo hay
páginas de navegación, que se derivan de la misma base y no inventan datos:

- `12_VAULT/bootcamp/index.md`        → las 20 clases con su orden y enlaces
- `12_VAULT/bootcamp/dia-NN.md`       → una página por clase, con lo que trata,
                                        los conceptos que introduce y los
                                        enlaces a sus notas
- `12_VAULT/conceptos/index.md`       → índice por categoría
- `12_VAULT/reglas/index.md`          → índice por estado
- `12_VAULT/operaciones/index.md`     → índice con el aviso de P&L
- `12_VAULT/cambios/index.md`         → índice cronológico
- `12_VAULT/preguntas/index.md`       → índice por estado

Nada de esto lleva datos nuevos: todo sale de SQLite y de los campos que ya
publica el generador principal.
"""

import os
import re
import sqlite3

from regenerar_vault import (
    BASE,
    VAULT,
    connect,
    confianza,
    mmss,
    slug,
    yaml_str,
    CORTE,
)

# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------


def reloj(seg):
    """Segundos -> 'm:ss' o 'h:mm:ss'."""
    seg = int(seg or 0)
    h, resto = divmod(seg, 3600)
    m, s = divmod(resto, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def escribir(sub, nombre, texto):
    d = os.path.join(VAULT, sub)
    os.makedirs(d, exist_ok=True)
    ruta = os.path.join(d, nombre)
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(texto)
    return ruta


def frontmatter(datos):
    lineas = ["---"]
    for k, v in datos.items():
        if isinstance(v, list):
            lineas.append(f"{k}: [{', '.join(yaml_str(x) for x in v)}]")
        elif isinstance(v, bool):
            lineas.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lineas.append(f"{k}: {v}")
        elif isinstance(v, dict):
            # Block style para objetos (el panel).
            lineas.append(f"{k}:")
            for kk, vv in v.items():
                if isinstance(vv, list):
                    lineas.append(f"  {kk}:")
                    for item in vv:
                        if isinstance(item, dict):
                            lineas.append("    - " + _flujo(item))
                        else:
                            lineas.append(f"    - {yaml_str(item)}")
                else:
                    lineas.append(f"  {kk}: {yaml_str(vv)}")
        else:
            lineas.append(f"{k}: {yaml_str(v)}")
    lineas.append("---")
    return "\n".join(lineas)


def _flujo(d):
    return "{" + ", ".join(f"{k}: {yaml_str(v)}" for k, v in d.items()) + "}"


def pastilla(texto, **attrs):
    a = " ".join(f'data-{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<span class="xr-pastilla" {a}>{texto}</span>'


def tarjeta(href, titulo, meta="", desc=""):
    partes = [
        f'<a class="xr-tarjeta" href="{href}">',
        f'<span class="xr-tarjeta-titulo">{titulo}</span>',
    ]
    if meta:
        partes.append(f'<span class="xr-tarjeta-meta">{meta}</span>')
    if desc:
        partes.append(f'<span class="xr-tarjeta-desc">{desc}</span>')
    partes.append("</a>")
    return "".join(partes)


def lista_tarjetas(items):
    return '<div class="xr-tarjetas">\n' + "\n".join(items) + "\n</div>"


# --------------------------------------------------------------------------
# Bootcamp
# --------------------------------------------------------------------------


def datos_bootcamp(con):
    """Une curriculum, videos, conceptos y reglas por clase."""
    filas = []
    for r in con.execute("SELECT * FROM curriculum ORDER BY order_num"):
        vid = r["video_id"]
        v = con.execute("SELECT * FROM videos WHERE id=?", (vid,)).fetchone()

        # Conceptos de esta clase: los que tienen evidencia citada **en este
        # vídeo** (tabla `evidence`). Es la fuente autoritativa y trazable: cada
        # fila lleva su cita y su minuto, así que el enlace no afirma nada que
        # no esté ya respaldado en la base.
        #
        # Antes se intentó deducir del texto `curriculum.concepts`, pero son
        # nombres de trabajo del proyecto («fractalidad», «high/low»,
        # «temporalidades») que no son alias de ninguna nota: enlazar por ahí
        # producía un mapa a medias y con relaciones inventadas.
        conceptos = [
            (c["id"], c["name"], slug(c["name"]))
            for c in con.execute(
                "SELECT DISTINCT c.id, c.name FROM concepts c "
                "JOIN evidence e ON e.entity_type='concept' AND e.entity_id=c.id "
                "WHERE e.video_id=? ORDER BY c.id",
                (vid,),
            )
        ]
        temas_declarados = (r["concepts"] or "").strip()

        reglas = con.execute(
            "SELECT id, name FROM rules WHERE first_seen_video=? ORDER BY id", (vid,)
        ).fetchall()
        frames = con.execute(
            "SELECT COUNT(*) n FROM frames WHERE video_id=?", (vid,)
        ).fetchone()["n"]
        anotados = con.execute(
            "SELECT COUNT(*) n FROM frames WHERE video_id=? AND "
            "lower(coalesce(description,'')) NOT LIKE 'pendiente de anotaci%'",
            (vid,),
        ).fetchone()["n"]

        filas.append({
            "orden": r["order_num"],
            "leccion": r["lesson"],
            "video_id": vid,
            "titulo": (v["title"] if v else r["lesson"]),
            "duracion": (v["duration_sec"] if v else 0) or 0,
            "fecha": (v["upload_date"] if v else "") or "",
            "conceptos": conceptos,
            "reglas": [(x["id"], x["name"], slug(x["name"])) for x in reglas],
            "notas": r["notes"] or "",
            "temas_declarados": temas_declarados,
            "estado": r["status"] or "",
            "frames": frames,
            "anotados": anotados,
        })
    return filas


def _temas(f):
    """Apunte de trabajo del curriculum (fecha, anuncios, pendientes).

    No es «de qué trata la clase»: muchas filas solo dicen la fecha o qué
    anunció el profesor para el día siguiente. Se publica etiquetado como
    apunte, nunca como resumen del contenido, para no atribuirle a la clase
    algo que no se dijo en ella.
    """
    t = (f["notas"] or "").strip()
    t = re.sub(r"^\d{4}-\d{2}-\d{2}\.\s*", "", t)
    return t


def _temas_curso(f):
    """Los temas declarados en el curriculum para esta clase.

    `curriculum.concepts` es la lista de temas que el proyecto apuntó al ver
    la clase. Es lo único que aquí describe el contenido, así que es lo que se
    muestra en el índice.
    """
    return (f["temas_declarados"] or "").strip()


def generar_bootcamp(con, slugs_concepto):
    filas = datos_bootcamp(con)
    if not filas:
        return 0

    items = []
    for f in filas:
        num = f"{f['orden']:02d}"
        titulo = re.sub(r"^Día \d+\s*[—-]\s*", "", f["leccion"])
        temas = _temas(f)
        meta = []
        meta.append(pastilla(reloj(f["duracion"])))
        if f["conceptos"]:
            meta.append(pastilla(f"{len(f['conceptos'])} conceptos"))
        if f["reglas"]:
            meta.append(pastilla(f"{len(f['reglas'])} reglas"))
        items.append(
            '<div class="xr-dia">'
            f'<span class="xr-dia-num">DÍA<br>{f["orden"]}</span>'
            '<div class="xr-dia-cuerpo">'
            f'<a class="xr-dia-titulo" href="./dia-{num}">{titulo}</a>'
            + (f'<div class="xr-dia-temas">{_temas_curso(f)}</div>' if _temas_curso(f) else "")
            + "</div>"
            '<div class="xr-dia-meta">'
            + "".join(meta)
            + f'<a class="xr-dia-ver" href="https://www.youtube.com/watch?v={f["video_id"]}" '
            'target="_blank" rel="noopener noreferrer">Ver en YouTube ↗</a>'
            "</div></div>"
        )

    total_conceptos = len({c[0] for f in filas for c in f["conceptos"]})
    total_reglas = len({r[0] for f in filas for r in f["reglas"]})
    panel = {
        "titulo": "El bootcamp, de un vistazo",
        "bloques": [
            {"etiqueta": "clases publicadas", "valor": len(filas)},
            {"etiqueta": "conceptos enlazados", "valor": total_conceptos},
            {"etiqueta": "reglas con fuente", "valor": total_reglas},
            {
                "etiqueta": "fotogramas anotados",
                "valor": sum(f["anotados"] for f in filas),
                "nota": f"de {sum(f['frames'] for f in filas)}",
            },
        ],
        "pie": (
            "Los enlaces de cada día llevan a los conceptos y reglas que esa clase introduce. "
            "La cifra de fotogramas anotados es la parte del sitio que aún depende de revisión manual."
        ),
    }

    cuerpo = [
        frontmatter({
            "tipo": "indice",
            "title": "Bootcamp — 20 clases",
            "titulo": "Bootcamp — 20 clases",
            "confianza": "explícito",
            "estado": "vigente",
            "video": "",
            "timestamp": "",
            "panel": panel,
        }),
        "",
        "# Bootcamp — 20 clases",
        "",
        "Las clases del bootcamp, en su orden. Cada día tiene su página con los conceptos que "
        "introduce, las reglas que salen de él y el enlace al minuto del vídeo.",
        "",
        "> [!tip] Este bloque es la base de todo lo demás",
        "> Si una nota de concepto contradice lo que se dice aquí, manda la clase. Cada concepto "
        "enlazado guarda su cita y su minuto.",
        "",
        '<div class="xr-dias">',
        *items,
        "</div>",
        "",
        "## Por dónde empezar",
        "",
        "Si es la primera vez, el orden importa: los días 4 a 8 (velas, liquidez, FVG) son el "
        "vocabulario que usan las clases siguientes. Los días de psicología (1, 3, 5, 7, 9, 12, "
        "14, 16, 18, 20) se pueden leer en cualquier momento.",
        "",
    ]
    escribir("bootcamp", "index.md", "\n".join(cuerpo))

    # Una página por día.
    n = 0
    for f in filas:
        num = f"{f['orden']:02d}"
        titulo = re.sub(r"^Día \d+\s*[—-]\s*", "", f["leccion"])
        meta_duracion = reloj(f["duracion"])
        lineas = [
            frontmatter({
                "tipo": "bootcamp",
                "title": f"Día {f['orden']} — {titulo}",
                "titulo": f"Día {f['orden']} — {titulo}",
                "confianza": "explícito",
                "estado": "vigente",
                "video": f["video_id"],
                "timestamp": "00:00",
                "dia": f["orden"],
                "categoria": "BOOTCAMP",
                "duracion": meta_duracion,
            }),
            "",
            f"# Día {f['orden']} — {titulo}",
            "",
            f"> **Clase {f['orden']} de {len(filas)}** · Duración {meta_duracion} · "
            f"**Vídeo:** `{f['video_id']}`",
            "",
        ]
        if f["notas"]:
            lineas += [
                "> [!note] Apunte del curriculum",
                f"> {_temas(f)}",
                "",
            ]

        if f["conceptos"]:
            lineas += ["## Conceptos que introduce", ""]
            for cid, nombre, s in f["conceptos"]:
                lineas.append(f"- [[{s}|{nombre}]]")
            lineas.append("")

        if f["reglas"]:
            lineas += ["## Reglas con fuente en esta clase", ""]
            for rid, nombre, s in f["reglas"]:
                lineas.append(f"- [[{s}|{nombre}]]")
            lineas.append("")

        if f["frames"]:
            lineas += [
                "## Fotogramas",
                "",
                f"Esta clase tiene **{f['frames']}** fotogramas extraídos; "
                f"**{f['anotados']}** están anotados y verificados para ilustrar conceptos.",
                "",
            ]

        # Navegación entre días.
        anterior = f["orden"] - 1
        siguiente = f["orden"] + 1
        nav = []
        if anterior >= 1:
            nav.append(f"[← Día {anterior}](./dia-{anterior:02d})")
        nav.append("[Índice del bootcamp](./index)")
        if siguiente <= len(filas):
            nav.append(f"[Día {siguiente} →](./dia-{siguiente:02d})")
        lineas += ["---", "", " · ".join(nav), ""]

        escribir("bootcamp", f"dia-{num}.md", "\n".join(lineas))
        n += 1
    return n


# --------------------------------------------------------------------------
# Índices por tipo
# --------------------------------------------------------------------------


def generar_indices(con, slugs_concepto, slugs_regla, slugs_trade=None):
    hechos = {}

    # --- conceptos ---------------------------------------------------------
    por_cat = {}
    for c in con.execute("SELECT * FROM concepts ORDER BY category, name"):
        s = slugs_concepto.get(c["id"])
        if not s:
            continue
        por_cat.setdefault(c["category"] or "Sin categoría", []).append((c, s))

    lineas = [
        frontmatter({
            "tipo": "indice",
            "title": "Conceptos",
            "titulo": "Conceptos",
            "confianza": "explícito",
            "estado": "vigente",
            "video": "",
            "timestamp": "",
        }),
        "",
        "# Conceptos",
        "",
        f"Los {sum(len(v) for v in por_cat.values())} conceptos de la metodología, agrupados por "
        "categoría. Cada nota lleva su definición, cómo identificarlo, condiciones, errores "
        "comunes y la cita que lo respalda.",
        "",
    ]
    for cat in sorted(por_cat):
        grupo = por_cat[cat]
        lineas += [f"## {cat}", "", lista_tarjetas([
            tarjeta(
                f"../conceptos/{s}",
                c["name"],
                pastilla(confianza(c["certainty"]), tipo="confianza")
                + pastilla("vigente" if c["status"] != "obsoleto" else "obsoleta",
                           estado="vigente" if c["status"] != "obsoleto" else "obsoleta"),
                (c["definition"] or "")[:150] + ("…" if len(c["definition"] or "") > 150 else ""),
            )
            for c, s in grupo
        ]), ""]
    escribir("conceptos", "index.md", "\n".join(lineas))
    hechos["conceptos"] = sum(len(v) for v in por_cat.values())

    # --- reglas ------------------------------------------------------------
    reglas = con.execute("SELECT * FROM rules ORDER BY status, id").fetchall()
    vigentes = [r for r in reglas if r["status"] != "obsoleto"]
    obsoletas = [r for r in reglas if r["status"] == "obsoleto"]
    lineas = [
        frontmatter({
            "tipo": "indice",
            "title": "Reglas operativas",
            "titulo": "Reglas operativas",
            "confianza": "explícito",
            "estado": "vigente",
            "video": "",
            "timestamp": "",
        }),
        "",
        "# Reglas operativas",
        "",
        f"**{len(vigentes)}** reglas vigentes y **{len(obsoletas)}** obsoletas, que se conservan "
        "con la regla que las reemplaza: saber qué se dejó de hacer también es metodología.",
        "",
        "## Vigentes",
        "",
        lista_tarjetas([
            tarjeta(
                f"../reglas/{slugs_regla.get(r['id'], slug(r['name']))}",
                r["name"],
                pastilla(confianza(r["certainty"]), tipo="confianza")
                + (pastilla(f"v{r['version']}") if r["version"] and r["version"] > 1 else ""),
                (r["description"] or "")[:160] + ("…" if len(r["description"] or "") > 160 else ""),
            )
            for r in vigentes
        ]),
        "",
    ]
    if obsoletas:
        lineas += [
            "## Obsoletas",
            "",
            "Se conservan con el motivo y la regla que las sustituye.",
            "",
            lista_tarjetas([
                tarjeta(
                    f"../reglas/{slugs_regla.get(r['id'], slug(r['name']))}",
                    r["name"],
                    pastilla("obsoleta", estado="obsoleta"),
                    (r["description"] or "")[:160],
                )
                for r in obsoletas
            ]),
            "",
        ]
    escribir("reglas", "index.md", "\n".join(lineas))
    hechos["reglas"] = len(reglas)

    # --- operaciones -------------------------------------------------------
    ops = con.execute(
        "SELECT t.*, m.pnl_usd, m.r_multiple, m.outcome, m.risk_usd "
        "FROM trades t LEFT JOIN trade_metrics m ON m.trade_id=t.id ORDER BY t.date DESC"
    ).fetchall()
    if ops:
        tarjetas = []
        for t in ops:
            s = slug(f"operacion-{t['id']}-{t['instrument'] or ''}-{t['date'] or ''}")
            meta = []
            if t["instrument"]:
                meta.append(pastilla(t["instrument"]))
            if t["date"]:
                meta.append(pastilla(str(t["date"])[:10]))
            if t["result"]:
                meta.append(pastilla(str(t["result"])))
            desc = (t["context"] or t["reasoning"] or "")[:140]
            tarjetas.append(tarjeta(f"../operaciones/{s}", f"Operación · {t['instrument'] or t['id']}",
                                    "".join(meta), desc))
        lineas = [
            frontmatter({
                "tipo": "indice",
                "title": "Operaciones",
                "titulo": "Operaciones",
                "confianza": "explícito",
                "estado": "vigente",
                "video": "",
                "timestamp": "",
                "anotaciones": False,
            }),
            "",
            "# Operaciones",
            "",
            "> [!warning] P&L autodeclarado, no auditado",
            "> Las cifras vienen de lo que se cuenta en los vídeos; no hay extractos ni capturas "
            "de la cuenta que las respalden.",
            "",
            f"{len(tarjetas)} operaciones analizadas, de la más reciente a la más antigua.",
            "",
            lista_tarjetas(tarjetas),
            "",
        ]
        escribir("operaciones", "index.md", "\n".join(lineas))
        hechos["operaciones"] = len(tarjetas)

    # --- cambios -----------------------------------------------------------
    cambios = con.execute("SELECT * FROM changes ORDER BY date DESC, id DESC").fetchall()
    if cambios:
        tarjetas = []
        for ch in cambios:
            meta = pastilla(str(ch["date"])[:10]) if ch["date"] else ""
            desc = (ch["description"] or "")[:150]
            tarjetas.append(
                tarjeta(f"../cambios/{slug('cambio-%s-%s-%s' % (ch['id'], ch['change_type'], ch['date']))}",
                        f"{ch['change_type'] or 'Cambio'} · {ch['entity_type'] or ''}".strip(" ·"),
                        meta, desc)
            )
        lineas = [
            frontmatter({
                "tipo": "indice",
                "title": "Cambios metodológicos",
                "titulo": "Cambios metodológicos",
                "confianza": "explícito",
                "estado": "vigente",
                "video": "",
                "timestamp": "",
            }),
            "",
            "# Cambios metodológicos",
            "",
            "Lo que se decía antes y lo que se dice ahora, con el vídeo donde cambia. "
            "Un cambio no borra la regla anterior: la marca como obsoleta.",
            "",
            lista_tarjetas(tarjetas),
            "",
        ]
        escribir("cambios", "index.md", "\n".join(lineas))
        hechos["cambios"] = len(tarjetas)

    return hechos


def contar_pendientes(con):
    """Cifras honestas del estado del proyecto, sin redondear a favor."""
    total = con.execute("SELECT COUNT(*) n FROM frames").fetchone()["n"]
    anotados = con.execute(
        "SELECT COUNT(*) n FROM frames WHERE lower(coalesce(description,'')) "
        "NOT LIKE 'pendiente de anotaci%' AND trim(coalesce(description,'')) NOT IN "
        "('keyword','periodic','scene','visual','deictico','déictico','frame de contexto')"
    ).fetchone()["n"]
    boot_total = con.execute(
        "SELECT COUNT(*) n FROM frames f JOIN videos v ON v.id=f.video_id "
        "WHERE v.category='BOOTCAMP'"
    ).fetchone()["n"]
    boot_anot = con.execute(
        "SELECT COUNT(*) n FROM frames f JOIN videos v ON v.id=f.video_id "
        "WHERE v.category='BOOTCAMP' AND lower(coalesce(f.description,'')) "
        "NOT LIKE 'pendiente de anotaci%'"
    ).fetchone()["n"]
    return {
        "frames_total": total,
        "frames_anotados": anotados,
        "boot_frames": boot_total,
        "boot_anotados": boot_anot,
    }


# --------------------------------------------------------------------------
# Índice de preguntas abiertas
# --------------------------------------------------------------------------


def generar_indice_preguntas(con):
    """Índice de preguntas abiertas, agrupadas por estado de confirmación.

    El estado sale del propio cuerpo de la pregunta («NO CONFIRMADO»,
    «PARCIAL»…), no de una clasificación nueva.
    """
    filas = []
    for r in con.execute("SELECT id, name, notes FROM rules ORDER BY id"):
        pass
    for c in con.execute("SELECT * FROM concepts ORDER BY id"):
        pass
    # Las preguntas viven como notas ya generadas; se leen de su frontmatter.
    d = os.path.join(VAULT, "preguntas")
    if not os.path.isdir(d):
        return 0
    for n in sorted(os.listdir(d)):
        if not n.endswith(".md") or n == "index.md":
            continue
        with open(os.path.join(d, n), encoding="utf-8") as fh:
            texto = fh.read()
        titulo = ""
        video = ""
        conf = ""
        m = re.search(r'^titulo:\s*"?(.*?)"?\s*$', texto, re.M)
        if m:
            titulo = m.group(1)
        m = re.search(r'^video:\s*"?(.*?)"?\s*$', texto, re.M)
        if m:
            video = m.group(1)
        m = re.search(r'^confianza:\s*"?(.*?)"?\s*$', texto, re.M)
        if m:
            conf = m.group(1)
        # El estado se escribe en prosa («PARCIALMENTE RESUELTO; queda…»), así
        # que se toma la primera frase y, de ella, la etiqueta en mayúsculas
        # inicial. Sin etiqueta reconocible, la pregunta cuenta como abierta:
        # es la lectura segura.
        m = re.search(r"\*\*Estado de la pregunta:\*\*\s*(.+)", texto)
        crudo = (m.group(1).strip() if m else "")
        etiqueta = ""
        m2 = re.match(r"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]{2,})", crudo)
        if m2:
            etiqueta = m2.group(1).strip()
        if not etiqueta:
            etiqueta = "NO CONFIRMADO"
        # Agrupa por la familia del estado, no por la frase entera.
        if "RESUELTO" in etiqueta:
            etiqueta = "RESUELTO"
        elif "PARCIAL" in etiqueta:
            etiqueta = "PARCIAL"
        elif "ABIERTO" in etiqueta:
            etiqueta = "ABIERTO"
        elif "AMBIGU" in etiqueta:
            etiqueta = "AMBIGUO"
        filas.append((n[:-3], titulo, etiqueta, video, conf))

    grupos = {}
    for f in filas:
        grupos.setdefault(f[2], []).append(f)

    lineas = [
        frontmatter({
            "tipo": "indice",
            "title": "Preguntas abiertas",
            "titulo": "Preguntas abiertas",
            "confianza": "no confirmado",
            "estado": "vigente",
            "video": "",
            "timestamp": "",
        }),
        "",
        "# Preguntas abiertas",
        "",
        f"**{len(filas)} preguntas** que el material no cierra. No se responden aquí: se dejan "
        "formuladas con lo que sí se sabe y con lo que haría falta para resolverlas.",
        "",
        "> [!note] La regla del proyecto es no inventar",
        "> Una pregunta abierta no es un fallo del sitio: es el sitio negándose a rellenar un hueco.",
        "",
    ]
    for estado in sorted(grupos, key=lambda e: (e != "NO CONFIRMADO", e)):
        grupo = grupos[estado]
        lineas += [f"## {estado.title()} ({len(grupo)})", ""]
        lineas.append(lista_tarjetas([
            tarjeta(
                f"../preguntas/{s}",
                t or s,
                pastilla(estado.lower().replace("_", " "), estado="obsoleta")
                + (pastilla(f"`{v}`") if v else ""),
            )
            for s, t, _, v, _ in grupo
        ]))
        lineas.append("")
    escribir("preguntas", "index.md", "\n".join(lineas))
    return len(filas)

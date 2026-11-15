#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenera el vault de Obsidian/Quartz (12_VAULT/) desde la base SQLite.

Una nota por:
  - concepto      (tabla concepts)
  - regla         (tabla rules)
  - operación     (tabla trades)
  - cambio        (tabla changes)
  - pregunta      (05_METHODOLOGY/11_PREGUNTAS_ABIERTAS.md)

Enlaces [[...]]:
  - regla → concepto          (detección automática sobre el texto de la regla)
  - concepto → concepto       (campo `combinations`: «requiere / se combina»)
  - regla nueva → obsoleta    (rules.supersedes)
  - operación → regla         (detección automática por conceptos del trade)

Fotogramas: 1–3 por concepto, priorizando los anotados. Se copian a
12_VAULT/media/, se convierten a WebP (máx. 1200 px de ancho) y se incrustan
con pie (vídeo, timestamp, confianza).

Uso:
    python 09_AUTOMATION/regenerar_vault.py --limite-conceptos 10   # prueba
    python 09_AUTOMATION/regenerar_vault.py                        # completo
    python 09_AUTOMATION/regenerar_vault.py --sin-media            # sin copiar frames
"""

import argparse
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import unicodedata
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
VAULT = os.path.join(BASE, "12_VAULT")
MEDIA = os.path.join(VAULT, "media")
PREGUNTAS_MD = os.path.join(BASE, "05_METHODOLOGY", "11_PREGUNTAS_ABIERTAS.md")
CORTE = "2026-11-14"

SKIP_DESC = {"keyword", "periodic", "scene", "frame de contexto"}
PENDIENTE = "pendiente de anotaci"
# Alias demasiado genéricos para usarlos como enlace automático: generarían
# relaciones falsas entre conceptos que solo comparten una palabra común.
ALIAS_GENERICOS = {"gap", "target", "objetivo", "alto", "bajo", "miedo", "prisa",
                   "ego", "volumen", "cinta", "footprint", "festivo"}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def slug(text, maxlen=72):
    s = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:maxlen].strip("-") or "nota")


def mmss(sec):
    if sec is None:
        return ""
    sec = int(round(float(sec)))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def yaml_str(value):
    if value is None:
        return '""'
    value = str(value).replace('"', '\\"')
    return f'"{value}"'


def yaml_list(values):
    return "[" + ", ".join(yaml_str(v) for v in values if v) + "]"


def confianza(value):
    v = (value or "NO CONFIRMADO").strip().lower()
    mapping = {
        "explicito": "explícito", "explícito": "explícito",
        "observado": "observado", "inferido": "inferido",
        "no confirmado": "no confirmado",
    }
    return mapping.get(v, "no confirmado")


def ensure_dirs():
    os.makedirs(VAULT, exist_ok=True)
    for sub in ("conceptos", "reglas", "operaciones", "cambios", "preguntas", "media"):
        os.makedirs(os.path.join(VAULT, sub), exist_ok=True)


def ffmpeg_path():
    root = os.path.expanduser("~")
    d = os.path.join(root, "Documents", "AutoDownloader", ".venv", "Lib", "site-packages",
                     "imageio_ffmpeg", "binaries")
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if name.lower().startswith("ffmpeg") and name.lower().endswith(".exe"):
                return os.path.join(d, name)
    p = shutil.which("ffmpeg")
    if p:
        return p
    raise RuntimeError("ffmpeg no disponible para convertir a WebP")


def jpg_a_webp(src, dst):
    ff = ffmpeg_path()
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-i", src,
           "-vf", "scale='min(1200,iw)':-2", "-c:v", "libwebp", "-quality", "82", "-y", dst]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return os.path.exists(dst)


def normaliza_titulo(text):
    return re.sub(r"\s+", " ", (text or "").strip())


# --------------------------------------------------------------------------
# Modelo de notas
# --------------------------------------------------------------------------

class Nota:
    def __init__(self, tipo, titulo, slug_base, carpeta):
        self.tipo = tipo
        self.titulo = normaliza_titulo(titulo)
        self.slug = slug_base
        self.carpeta = carpeta
        self.frontmatter = {}
        self.cuerpo = []
        self.enlaces = []  # (slug, texto)

    @property
    def rel(self):
        return f"{self.carpeta}/{self.slug}.md"

    def render(self):
        fm = {"tipo": self.tipo, "titulo": self.titulo, "title": self.titulo}
        fm.update(self.frontmatter)
        lines = ["---"]
        for k, v in fm.items():
            if v is None or v == "":
                lines.append(f"{k}: \"\"")
            elif isinstance(v, list):
                lines.append(f"{k}: {yaml_list(v)}")
            elif isinstance(v, bool):
                lines.append(f"{k}: {'true' if v else 'false'}")
            elif isinstance(v, (int, float)):
                lines.append(f"{k}: {v}")
            else:
                lines.append(f"{k}: {yaml_str(v)}")
        lines.append("---")
        lines.append("")
        lines.append(f"# {self.titulo}")
        lines.append("")
        lines.extend(self.cuerpo)
        lines.append("")
        return "\n".join(lines)


# --------------------------------------------------------------------------
# Enlaces
# --------------------------------------------------------------------------

def alt_en_texto(alt, text):
    """Coincidencia por palabra/frase completa. Evita que EMA case dentro de
    «tema» o RSI dentro de «preguntarse»."""
    patron = r"(?<![a-z0-9áéíóúüñ])" + re.escape(alt.lower()) + r"(?![a-z0-9áéíóúüñ])"
    return re.search(patron, text.lower()) is not None


def concept_mentions(text, conceptos, limit=8):
    scores = {}
    for c in conceptos:
        hits = 0
        for alt in c["alts"]:
            if len(alt) > 2 and alt not in ALIAS_GENERICOS and alt_en_texto(alt, text):
                hits += 1
        if hits:
            scores[c["id"]] = hits
    return [cid for cid, _ in sorted(scores.items(), key=lambda x: -x[1])[:limit]]


def render_links(items, heading="Conceptos relacionados"):
    """items: [(slug, display)]"""
    seen = set()
    uniq = []
    for s, d in items:
        if s and s not in seen:
            seen.add(s)
            uniq.append((s, d))
    if not uniq:
        return []
    out = [f"## {heading}", ""]
    for s, d in uniq:
        out.append(f"- [[{s}|{d}]]")
    out.append("")
    return out


# --------------------------------------------------------------------------
# Fotogramas por concepto
# --------------------------------------------------------------------------

def frame_is_annotated(row):
    d = (row["description"] or "").strip().lower()
    return bool(d) and d not in SKIP_DESC and not d.startswith(PENDIENTE) and not d.startswith("frame de contexto")


def frame_vacio(path, min_tinta=0.0008):
    """Descarta capturas cuya zona de gráfico está vacía (sin velas ni trazos).
    Ver la misma función en frames_selectivos.py."""
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        im = Image.open(path).convert("L")
        w, h = im.size
        c = im.crop((int(w * 0.06), int(h * 0.10), int(w * 0.72), int(h * 0.88)))
        px = list(c.getdata())
        return (sum(1 for p in px if p < 110) / len(px)) < min_tinta
    except Exception:
        return False


def es_pantalla(path, max_croma=0.13):
    """True si la captura es pantalla/gráfico y no cámara hablando.
    Se mide la saturación de color: la piel, la ropa y la habitación suben el
    croma; un gráfico gris de TradingView lo mantiene muy bajo."""
    try:
        from PIL import Image
    except ImportError:
        return True
    try:
        im = Image.open(path).convert("RGB")
        w, h = im.size
        c = im.crop((int(w * 0.12), int(h * 0.16), int(w * 0.78), int(h * 0.84)))
        c = c.resize((200, 130), Image.LANCZOS)
        px = list(c.getdata())
        sat = 0
        for r, g, b in px:
            mx, mn = max(r, g, b), min(r, g, b)
            if mx > 0 and (mx - mn) / mx > 0.18 and mx > 45:
                sat += 1
        return (sat / len(px)) <= max_croma
    except Exception:
        return True


def candidate_frames(con, concepto):
    cid = concepto["id"]
    name = concepto["name"]
    alts = concepto["alts"]
    picked = []
    seen = set()

    def add(row, rank, why):
        if row["id"] in seen:
            return
        seen.add(row["id"])
        picked.append((rank, row, why))

    # 1) Evidencia con frame_id explícito: los anotados mandan.
    for ev in con.execute(
        "SELECT * FROM evidence WHERE entity_type='concept' AND entity_id=? AND frame_id IS NOT NULL",
        (cid,),
    ):
        fr = con.execute("SELECT * FROM frames WHERE id=?", (ev["frame_id"],)).fetchone()
        if fr:
            add(fr, 0 if frame_is_annotated(fr) else 2, "evidencia enlazada")

    # 2) Fotogramas anotados que mencionan el concepto.
    for fr in con.execute("SELECT * FROM frames"):
        if not frame_is_annotated(fr):
            continue
        text = ((fr["description"] or "") + " " + (fr["analysis"] or "")).lower()
        if any(a in text for a in alts):
            add(fr, 1, "anotación menciona el concepto")

    # 3) Fotogramas nuevos pendientes etiquetados con el concepto.
    for fr in con.execute("SELECT * FROM frames WHERE description LIKE ?",
                          (f"pendiente de anotación%concepto:%{name}%",)):
        add(fr, 3, "fotograma pendiente de anotación")

    picked.sort(key=lambda x: (x[0], x[1]["timestamp_sec"]))
    return picked[:3]


def limpiar_media():
    """El contenido de media/ es generado; se reconstruye en cada ejecución
    para que los pies de foto no puedan quedar asociados a otro fotograma."""
    if os.path.isdir(MEDIA):
        for name in os.listdir(MEDIA):
            if name.lower().endswith(".webp"):
                os.remove(os.path.join(MEDIA, name))


def build_media(con, concepto, slug_concepto, dry=False):
    rows = candidate_frames(con, concepto)
    lines = []
    used = 0
    for rank, fr, why in rows:
        src = os.path.join(BASE, fr["path"])
        if not os.path.exists(src):
            continue
        if frame_vacio(src):
            continue
        if not es_pantalla(src):
            continue
        dest_name = f"{slug_concepto}-{fr['id']}.webp"
        dest = os.path.join(MEDIA, dest_name)
        if not dry and not os.path.exists(dest):
            if not jpg_a_webp(src, dest):
                continue
        video = con.execute("SELECT title FROM videos WHERE id=?", (fr["video_id"],)).fetchone()
        vtitle = video["title"] if video else fr["video_id"]
        estado = "anotado" if frame_is_annotated(fr) else "pendiente de anotación"
        caption = (f"**{vtitle}** (`{fr['video_id']}`) · **{mmss(fr['timestamp_sec'])}** · "
                   f"**Confianza:** {confianza(concepto['certainty'])} · {estado}")
        if frame_is_annotated(fr):
            excerpt = (fr["description"] or "").strip()
            if excerpt:
                caption += f"\n> {excerpt[:220]}{'…' if len(excerpt) > 220 else ''}"
        lines.append(f"![{concepto['name']} en {fr['video_id']}](../media/{dest_name})")
        lines.append("")
        lines.append(caption)
        lines.append("")
        used += 1
    return lines


# --------------------------------------------------------------------------
# Generación de notas
# --------------------------------------------------------------------------

def conceptos_data(con):
    out = []
    for r in con.execute("SELECT * FROM concepts ORDER BY id"):
        alts = [r["name"]] + [a.strip() for a in (r["aliases"] or "").split(",") if a.strip()]
        out.append(dict(r, alts=[a.lower() for a in alts]))
    return out


def generate_conceptos(con, conceptos, limite=None, sin_media=False, dry=False):
    notas = {}
    slugs = {}
    for c in conceptos:
        s = slug(c["name"])
        base = s
        i = 2
        while s in slugs.values():
            s = f"{base}-{i}"
            i += 1
        slugs[c["id"]] = s

    for c in conceptos[:limite] if limite else conceptos:
        s = slugs[c["id"]]
        nota = Nota("concepto", c["name"], s, "conceptos")
        uso = c["status"] if c["status"] not in ("vigente", "obsoleto") else ""
        nota.frontmatter.update({
            "confianza": confianza(c["certainty"]),
            "estado": "obsoleta" if c["status"] == "obsoleto" else "vigente",
            "video": c["first_seen_video"] or "",
            "timestamp": mmss(c["first_seen_ts"]),
            "categoria": c["category"] or "",
            "uso": uso,
            "sinonimos": c["alts"][1:],
            "id": c["id"],
        })
        nota.cuerpo += [
            f"> **Confianza:** {confianza(c['certainty'])} · **Estado:** {c['status']} · "
            f"**Categoría:** {c['category'] or '—'}",
            "",
        ]
        for titulo, campo in [
            ("Definición", "definition"),
            ("Interpretación de Xavi", "xavi_interpretation"),
            ("Cómo identificarlo", "how_identify"),
            ("Cuándo se usa", "when_used"),
            ("Condiciones", "conditions"),
            ("Temporalidades", "timeframes"),
            ("Aplicación", "application"),
            ("Errores comunes", "common_errors"),
            ("Excepciones", "exceptions"),
            ("Notas", "notes"),
        ]:
            if c[campo]:
                nota.cuerpo += [f"## {titulo}", "", str(c[campo]), ""]

        # concepto → concepto (requiere / se combina)
        rel = []
        comb = (c["combinations"] or "").lower()
        for other in conceptos:
            if other["id"] == c["id"]:
                continue
            if any(alt_en_texto(a, comb) and a not in ALIAS_GENERICOS
                   for a in other["alts"] if len(a) > 2):
                rel.append((slugs[other["id"]], other["name"]))
        nota.cuerpo += render_links(rel, "Requiere / se combina con")

        # Evidencia
        evs = con.execute(
            "SELECT * FROM evidence WHERE entity_type='concept' AND entity_id=? ORDER BY timestamp_sec",
            (c["id"],),
        ).fetchall()
        if evs:
            nota.cuerpo += ["## Evidencia", ""]
            for ev in evs[:8]:
                quote = (ev["quote"] or "").strip()
                nota.cuerpo.append(
                    f"- «{quote}» — `{ev['video_id']}` @ {mmss(ev['timestamp_sec'])} "
                    f"({confianza(ev['source_type'])})"
                )
            nota.cuerpo.append("")

        if not sin_media:
            media_lines = build_media(con, c, s, dry=dry)
            if media_lines:
                nota.cuerpo += ["## Fragmentos visuales", ""] + media_lines

        notes_dir = os.path.join(VAULT, "conceptos")
        if not dry:
            with open(os.path.join(notes_dir, f"{s}.md"), "w", encoding="utf-8") as fh:
                fh.write(nota.render())
        notas[c["id"]] = nota
    return notas, slugs


def generate_reglas(con, conceptos, slugs_concepto, notas_obsoletas):
    slugs_regla = {}
    for r in con.execute("SELECT * FROM rules ORDER BY id"):
        s = slug(r["name"])
        base = s
        i = 2
        while s in slugs_regla.values():
            s = f"{base}-{i}"
            i += 1
        slugs_regla[r["id"]] = s

    for r in con.execute("SELECT * FROM rules ORDER BY id"):
        s = slugs_regla[r["id"]]
        nota = Nota("regla", r["name"], s, "reglas")
        nota.frontmatter.update({
            "confianza": confianza(r["certainty"]),
            "estado": "vigente" if r["status"] == "vigente" else "obsoleta",
            "video": r["first_seen_video"] or "",
            "timestamp": mmss(r["first_seen_ts"]),
            "id": r["id"],
            "version": r["version"] or 1,
        })
        nota.cuerpo += [
            f"> **Confianza:** {confianza(r['certainty'])} · **Estado:** {r['status']} · "
            f"**Versión:** {r['version'] or 1}",
            "",
        ]
        for titulo, campo in [
            ("Descripción", "description"),
            ("Contexto", "context"),
            ("Condiciones", "conditions"),
            ("Confirmaciones", "confirmations"),
            ("Condiciones de entrada", "entry_conditions"),
            ("Invalidación", "invalidation"),
            ("Gestión de riesgo", "risk_management"),
            ("Objetivos", "targets"),
            ("Excepciones", "exceptions"),
            ("Notas", "notes"),
        ]:
            if r[campo]:
                nota.cuerpo += [f"## {titulo}", "", str(r[campo]), ""]

        # regla → concepto
        text = " ".join(str(r[c] or "") for c in (
            "name", "description", "context", "conditions", "confirmations",
            "entry_conditions", "invalidation", "risk_management", "targets",
            "exceptions", "notes"))
        cids = concept_mentions(text, conceptos, limit=6)
        nota.cuerpo += render_links(
            [(slugs_concepto[cid], next(c["name"] for c in conceptos if c["id"] == cid)) for cid in cids]
        )

        # regla nueva → obsoleta / obsoleta → sustituta
        if r["supersedes"]:
            old = con.execute("SELECT name FROM rules WHERE id=?", (r["supersedes"],)).fetchone()
            if old:
                nota.cuerpo += ["## Reemplaza a", "", f"- [[{slugs_regla[r['supersedes']]}|{old['name']}]]", ""]
        for succ in con.execute("SELECT id, name FROM rules WHERE supersedes=?", (r["id"],)):
            nota.cuerpo += ["## Reemplazada por", "", f"- [[{slugs_regla[succ['id']]}|{succ['name']}]]", ""]

        # evidencia
        evs = con.execute(
            "SELECT * FROM evidence WHERE entity_type='rule' AND entity_id=? ORDER BY timestamp_sec",
            (r["id"],),
        ).fetchall()
        if evs:
            nota.cuerpo += ["## Evidencia", ""]
            for ev in evs[:8]:
                nota.cuerpo.append(
                    f"- «{(ev['quote'] or '').strip()}» — `{ev['video_id']}` @ {mmss(ev['timestamp_sec'])} "
                    f"({confianza(ev['source_type'])})"
                )
            nota.cuerpo.append("")

        with open(os.path.join(VAULT, "reglas", f"{s}.md"), "w", encoding="utf-8") as fh:
            fh.write(nota.render())
    return slugs_regla


def generate_operaciones(con, conceptos, reglas, slugs_concepto, slugs_regla):
    for r in con.execute("SELECT * FROM trades ORDER BY id"):
        s = slug(f"operacion-{r['id']}-{r['instrument'] or ''}-{r['date'] or ''}")
        nota = Nota("operacion", f"Operación #{r['id']} — {r['instrument'] or '—'} — {r['date'] or 'sin fecha'}", s, "operaciones")
        nota.frontmatter.update({
            "confianza": confianza(r["certainty"]),
            "estado": "vigente",
            "video": r["video_id"] or "",
            "timestamp": "",
            "fecha": r["date"] or "",
            "clasificacion": r["classification"] or "",
            "id": r["id"],
        })
        nota.cuerpo += [
            "> **Aviso:** P&L autodeclarado, no auditado. Las cifras provienen de lo que Xavi dice "
            "en el vídeo y no se han verificado con extractos de cuenta.",
            "",
            f"> **Clasificación:** {r['classification'] or '—'} · **Confianza:** {confianza(r['certainty'])}",
            "",
        ]
        for titulo, campo in [
            ("Contexto", "context"), ("Razonamiento", "reasoning"),
            ("Setup", "setup"), ("Entrada", "entry"), ("Stop", "stop"),
            ("Objetivo", "target"), ("Resultado", "result"),
            ("Gestión", "management"), ("Análisis posterior", "post_analysis"),
            ("Notas", "notes"),
        ]:
            if r[campo]:
                nota.cuerpo += [f"## {titulo}", "", str(r[campo]), ""]

        # operación → regla (detección automática por conceptos del trade)
        text = " ".join(str(r[c] or "") for c in ("context", "reasoning", "setup", "entry", "stop", "target", "management", "post_analysis", "notes"))
        cids = concept_mentions(text, conceptos, limit=5)
        if cids:
            names = {c["id"]: c["name"] for c in conceptos}
            nota.cuerpo += render_links(
                [(slugs_concepto[cid], names[cid]) for cid in cids],
                "Conceptos presentes",
            )
            related_rules = []
            for rule in reglas:
                rt = " ".join(str(rule[c] or "") for c in (
                    "name", "description", "context", "conditions", "entry_conditions",
                    "invalidation", "risk_management", "targets", "exceptions", "notes"))
                rt = rt.lower()
                score = 0
                for cid in cids:
                    c = next(x for x in conceptos if x["id"] == cid)
                    if any(a in rt for a in c["alts"] if len(a) > 2):
                        score += 1
                if score >= 2:
                    related_rules.append((score, rule))
            related_rules.sort(key=lambda x: -x[0])
            if related_rules:
                nota.cuerpo += render_links(
                    [(slugs_regla[x[1]["id"]], x[1]["name"]) for x in related_rules[:4]],
                    "Reglas relacionadas (detección automática)",
                )

        with open(os.path.join(VAULT, "operaciones", f"{s}.md"), "w", encoding="utf-8") as fh:
            fh.write(nota.render())


def generate_cambios(con, slugs_concepto, slugs_regla):
    for r in con.execute("SELECT * FROM changes ORDER BY id"):
        s = slug(f"cambio-{r['id']}-{r['change_type']}-{r['date']}")
        nota = Nota("cambio", f"Cambio #{r['id']} — {r['change_type']} — {r['date']}", s, "cambios")
        nota.frontmatter.update({
            "confianza": "explícito" if r["source_video"] else "inferido",
            "estado": "vigente",
            "video": r["source_video"] or "",
            "timestamp": mmss(r["source_ts"]),
            "fecha": r["date"] or "",
            "tipo_cambio": r["change_type"] or "",
            "entidad": f"{r['entity_type']}#{r['entity_id']}",
        })
        nota.cuerpo += [
            f"> **Tipo:** {r['change_type']} · **Entidad:** `{r['entity_type']}#{r['entity_id']}` · **Fecha:** {r['date']}",
            "",
            "## Descripción", "", r["description"] or "—", "",
            "## Valor anterior", "", r["old_value"] or "—", "",
            "## Valor nuevo", "", r["new_value"] or "—", "",
        ]
        link = None
        if r["entity_type"] == "concept" and r["entity_id"] in slugs_concepto:
            c = con.execute("SELECT name FROM concepts WHERE id=?", (r["entity_id"],)).fetchone()
            link = (slugs_concepto[r["entity_id"]], c["name"] if c else f"Concepto {r['entity_id']}")
        elif r["entity_type"] == "rule" and r["entity_id"] in slugs_regla:
            rr = con.execute("SELECT name FROM rules WHERE id=?", (r["entity_id"],)).fetchone()
            link = (slugs_regla[r["entity_id"]], rr["name"] if rr else f"Regla {r['entity_id']}")
        if link:
            nota.cuerpo += ["## Entidad afectada", "", f"- [[{link[0]}|{link[1]}]]", ""]
        if r["source_video"]:
            nota.cuerpo += ["## Fuente", "", f"- `{r['source_video']}` @ {mmss(r['source_ts'])}", ""]
        with open(os.path.join(VAULT, "cambios", f"{s}.md"), "w", encoding="utf-8") as fh:
            fh.write(nota.render())


def parse_preguntas():
    txt = open(PREGUNTAS_MD, encoding="utf-8").read()
    parts = re.split(r"^### ", txt, flags=re.M)[1:]
    out = []
    for part in parts:
        lines = part.splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        title = re.sub(r"^\d+(\.\d+)*\.\s*", "", title)
        body = "\n".join(lines[1:]).strip()
        # Cortar si el bloque alcanza la siguiente sección de nivel 2.
        body = re.split(r"\n##\s", body, maxsplit=1)[0].rstrip("-\n ")
        estado_match = re.search(r"\*\*Estado:\*\*\s*(.+)", body)
        estado = estado_match.group(1).strip() if estado_match else "NO CONFIRMADO"
        video_match = re.search(r"`([A-Za-z0-9_-]{11})`", body)
        ts_match = re.search(r"`[A-Za-z0-9_-]{11}`\s*\[?(\d{1,2}:\d{2})", body)
        out.append({
            "titulo": title,
            "cuerpo": body,
            "estado": estado,
            "video": video_match.group(1) if video_match else "",
            "timestamp": ts_match.group(1) if ts_match else "",
        })
    return out


def generate_preguntas():
    for i, q in enumerate(parse_preguntas(), 1):
        s = slug(f"pregunta-{i}-{q['titulo']}")
        nota = Nota("pregunta", q["titulo"], s, "preguntas")
        conf = "no confirmado"
        if "EXPLÍCITO" in q["estado"].upper():
            conf = "explícito"
        elif "OBSERVADO" in q["estado"].upper():
            conf = "observado"
        elif "INFERIDO" in q["estado"].upper():
            conf = "inferido"
        nota.frontmatter.update({
            "confianza": conf,
            "estado": "vigente",
            "video": q["video"],
            "timestamp": q["timestamp"],
            "id": i,
        })
        nota.cuerpo += [f"> **Estado de la pregunta:** {q['estado']}", "", q["cuerpo"]]
        with open(os.path.join(VAULT, "preguntas", f"{s}.md"), "w", encoding="utf-8") as fh:
            fh.write(nota.render())


def generate_index(conceptos_notas, slugs_concepto, reglas_count, trades_count,
                   cambios_count, preguntas_count):
    core = [(c.slug, c.titulo, c.frontmatter.get("categoria", "")) for c in conceptos_notas.values()
            if c.frontmatter.get("categoria") == "CORE"][:8]
    lines = [
        "---",
        "tipo: portada",
        f"titulo: {yaml_str('Metodología Xavi Ruyra — estudio no oficial')}",
        f"title: {yaml_str('Metodología Xavi Ruyra — estudio no oficial')}",
        f"confianza: {yaml_str('no confirmado')}",
        "estado: vigente",
        "video: \"\"",
        f"timestamp: {yaml_str('')}",
        "---",
        "",
        "# Metodología Xavi Ruyra — estudio no oficial",
        "",
        "> **Proyecto de estudio no oficial.** Este sitio es un resumen estructurado y trazable de "
        "contenido público de Xavi Ruyra. No es un curso oficial, no está afiliado ni respaldado por él, "
        "y no sustituye a sus vídeos. Todo lo que no tiene fuente con vídeo y minuto se marca como "
        "**no confirmado**.",
        "",
        f"**Fecha de corte de las cifras:** {CORTE}.",
        "",
        "## Qué contiene",
        "",
        f"- **{len(conceptos_notas)}** conceptos con definición, condiciones y evidencia.",
        f"- **{reglas_count}** reglas operativas, incluidas las obsoletas con su sustituto.",
        f"- **{trades_count}** operaciones analizadas. El P&L es autodeclarado y no está auditado.",
        f"- **{cambios_count}** cambios metodológicos documentados.",
        f"- **{preguntas_count}** preguntas abiertas. La regla del proyecto es no inventar: si no hay "
        "fuente, se dice.",
        "",
        "## Cómo leer este sitio",
        "",
        "- Cada nota lleva **confianza** (explícito / observado / inferido / no confirmado), "
        "**estado** (vigente / obsoleta), **vídeo** y **timestamp** de la fuente principal.",
        "- Los enlaces internos conectan reglas con conceptos, conceptos que se requieren entre sí "
        "y reglas nuevas con las que reemplazan.",
        "- La vista de **grafo** (arriba, icono de red) muestra la estructura completa.",
        "- La **búsqueda** está disponible en la lupa.",
        "",
        "## Niveles de confianza",
        "",
        "| Nivel | Significado |",
        "|---|---|",
        "| **explícito** | Xavi lo dice literalmente en un vídeo; hay cita y minuto. |",
        "| **observado** | Se desprende de lo que hace en un ejemplo o recap, no de una regla formulada. |",
        "| **inferido** | Interpretación del proyecto a partir de varias fuentes; no está formulado. |",
        "| **no confirmado** | No hay fuente suficiente. Se deja anotado como pregunta abierta. |",
        "",
        "## Conceptos núcleo",
        "",
    ]
    for slug_c, titulo_c, categoria_c in core:
        lines.append(f"- [[{slug_c}|{titulo_c}]] — {categoria_c}")
    lines += [
        "",
        "## Fuente",
        "",
        "Los datos se regeneran desde SQLite con `09_AUTOMATION/regenerar_vault.py`. "
        "Los fotogramas son capturas de vídeos públicos usadas como cita visual; "
        "las transcripciones completas y los Reels de Instagram quedan fuera de este sitio.",
        "",
    ]
    with open(os.path.join(VAULT, "index.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite-conceptos", type=int, default=None,
                    help="Genera solo los N primeros conceptos (prueba)")
    ap.add_argument("--sin-media", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    con = connect()
    ensure_dirs()
    if not args.dry_run:
        limpiar_media()
    conceptos = conceptos_data(con)
    notas, slugs_concepto = generate_conceptos(
        con, conceptos, limite=args.limite_conceptos,
        sin_media=args.sin_media, dry=args.dry_run)

    # Para la prueba solo se generan conceptos + portada.
    if args.limite_conceptos:
        slugs_regla = {}
        reglas_count = 0
        trades_count = 0
        cambios_count = 0
        preguntas_count = 0
    else:
        slugs_regla = generate_reglas(con, conceptos, slugs_concepto, {})
        reglas = [dict(r) for r in con.execute("SELECT * FROM rules")]
        generate_operaciones(con, conceptos, reglas, slugs_concepto, slugs_regla)
        generate_cambios(con, slugs_concepto, slugs_regla)
        generate_preguntas()
        reglas_count = len(reglas)
        trades_count = len(list(con.execute("SELECT id FROM trades")))
        cambios_count = len(list(con.execute("SELECT id FROM changes")))
        preguntas_count = len(parse_preguntas())

    if not args.dry_run:
        generate_index(notas, slugs_concepto, reglas_count, trades_count,
                       cambios_count, preguntas_count)

    print(f"Vault: {VAULT}")
    print(f"Conceptos: {len(notas)}")
    print(f"Media: {len(os.listdir(MEDIA)) if os.path.isdir(MEDIA) else 0} archivos")
    if args.limite_conceptos:
        print("Modo prueba: solo conceptos + portada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

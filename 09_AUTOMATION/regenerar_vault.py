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
    # Lanczos en vez del escalado bicúbico por defecto: al reducir 1806 -> 1200
    # conserva mucho mejor el borde de las velas y del texto. Calidad 90 en
    # lugar de 82: el texto pequeño del gráfico se emborronaba.
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-i", src,
           "-vf", "scale='min(1200,iw)':-2:flags=lanczos",
           "-c:v", "libwebp", "-quality", "90", "-compression_level", "6", "-y", dst]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return os.path.exists(dst)


def normaliza_titulo(text):
    return re.sub(r"\s+", " ", (text or "").strip())


# frame_id -> concept_id al que pertenece la imagen. Lo calcula `main()` antes
# de generar notas; vacío = sin reparto (modo prueba).
DUENO_FOTOGRAMAS = {}


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


def frame_vacio(path, min_tinta=0.0012):
    """Descarta capturas cuya zona de gráfico está vacía (sin velas ni trazos).

    El umbral está medido sobre las 54 imágenes que publica el sitio: la mediana
    de «tinta» (fracción de píxeles oscuros en la zona del gráfico) es 0,030, y
    las diapositivas de texto sobre un gráfico en blanco caen por debajo de
    0,0015. Con 0,002 se descartan esas diapositivas y no se toca ninguna
    captura con velas.

    Hay dos capas con el mismo nombre porque miden cosas distintas: esta lee el
    .jpg de origen que produce el extractor, y `webp_vacio` lee el archivo ya
    publicado (que puede venir recortado de la recaptura).
    """
    return _tinta(path) < min_tinta


def _tinta(path):
    """Fracción de píxeles oscuros en la zona donde debería estar el gráfico."""
    try:
        from PIL import Image
    except ImportError:
        return 1.0
    try:
        im = Image.open(path).convert("L")
        w, h = im.size
        c = im.crop((int(w * 0.06), int(h * 0.10), int(w * 0.72), int(h * 0.88)))
        datos = list(c.getdata())
        return sum(1 for p in datos if p < 110) / len(datos)
    except Exception:
        return 1.0


def webp_vacio(path, min_tinta=0.002):
    """Igual que `frame_vacio`, sobre el .webp ya generado.

    NO se usa para filtrar lo publicado: mide píxeles oscuros y un esquema de
    líneas claras sobre fondo blanco (que sí ilustra el concepto) da valores tan
    bajos como una diapositiva vacía. Medido: `internal-external-liquidity-175`
    tiene 0,0009 de tinta y es un gráfico completo con SSL, PDH, BSL, FVG y REL.
    Esa distinción la hace una persona mirando la imagen; ver
    `revisar_capturas.py` y `vetar_fotogramas.py`.
    """
    return _tinta(path) < min_tinta


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


NEGACIONES = (
    "no hay", "no se ve", "no verifica", "no muestra", "no identifica",
    "no aparece", "no aporta", "no se distingue", "no consta", "sin rótulo",
    "no hay rótulo", "no se aprecia", "no permite ver", "no se observa",
)
_RE_NEG = re.compile("|".join(re.escape(n) for n in NEGACIONES))


def _oraciones(text):
    return [s for s in re.split(r"(?<=[.:;])\s+|\n+", text or "") if s.strip()]


def global_aliases(con):
    """[(alias, concept_id)] de todos los conceptos, para saber qué niega una negación.

    Hace falta porque «cuando no hay FVG uso CISD» contiene una negación y la
    palabra CISD en la misma frase, pero lo negado es el FVG.
    """
    out = []
    for r in con.execute("SELECT id, name, aliases FROM concepts"):
        for a in [r["name"]] + [x.strip() for x in (r["aliases"] or "").split(",") if x.strip()]:
            a = a.lower()
            if len(a) > 2 and a not in ALIAS_GENERICOS:
                out.append((a, r["id"]))
    return out


def niega_concepto(desc, alts, cid=None, aliases_globales=None):
    """True si la anotación dice que *este* concepto no se ve.

    Se busca la negación y se mira cuál es el primer alias que aparece después:
    si es de este concepto, la negación va sobre él; si es de otro, no. Así
    «no hay un rótulo que identifique el IFVG» descarta la imagen para IFVG,
    pero «cuando no hay FVG uso CISD» no descarta nada para CISD.
    """
    propias = {a for a in alts if len(a) > 2}
    for oracion in _oraciones(desc):
        o = oracion.lower()
        for m in _RE_NEG.finditer(o):
            ventana = o[m.end():m.end() + 70]
            if not ventana.strip():
                continue
            # Primer alias que aparece tras la negación, sea de este concepto o de otro.
            mejor = None
            for alt, otro_id in (aliases_globales or []):
                pos = ventana.find(alt)
                if pos == -1:
                    continue
                if otro_id != cid and alt not in propias:
                    if mejor is None or pos < mejor[0]:
                        mejor = (pos, otro_id)
                elif otro_id == cid or alt in propias:
                    if mejor is None or pos < mejor[0]:
                        mejor = (pos, cid)
            if mejor is not None and mejor[1] == cid:
                return True
            if mejor is None and any(alt_en_texto(a, ventana) for a in propias):
                return True
    return False


def justifica_concepto(texto, alts):
    """True si el texto nombra el concepto con límites de palabra."""
    return any(alt_en_texto(a, texto) for a in alts if len(a) > 2)


# Una captura puede nombrar el concepto y, aun así, no enseñarlo: la anotación
# dice que el gráfico está vacío, que es una diapositiva, que no hay velas.
# Eso no es una negación del concepto («no hay IFVG») sino una negación del
# contenido visual, y basta para no publicarla como prueba.
_AUSENCIA = re.compile(
    r"gr[áa]fico[^.]{0,40}vac[íi]|vac[íi]o,? sin|completamente vac[íi]|"
    r"sin (?:una sola )?vela|no hay velas|sin velas|"
    r"diapositiva (?:de|con) (?:texto|t[íi]tulo)|"
    r"(?:solo|únicamente) (?:se ve|hay|aparece) (?:la )?(?:diapositiva|texto|t[íi]tulo)|"
    r"fondo (?:negro|vac[íi]o) sin|"
    r"no (?:hay|se ve|se observa) (?:ninguna|ningún) (?:vela|serie|trazo|dibujo)"
)


def vetos_de(con, cid):
    """Conjunto de frame_id vetados para este concepto (o para todos).

    Los escribe `vetar_fotogramas.py` cuando alguien mira la imagen y decide que
    no enseña el concepto. Se guardan en una tabla porque el mismo fotograma
    puede servir para un concepto y no para otro: una diapositiva de Judas Swing
    ilustra Judas Swing, pero no el PO3.
    """
    vetados = set()
    try:
        for r in con.execute(
            "SELECT frame_id FROM frame_vetos WHERE concept_id IS NULL OR concept_id=?",
            (cid,),
        ):
            vetados.add(r["frame_id"])
    except sqlite3.OperationalError:
        # Base antigua sin la tabla: no hay vetos, no es un error.
        return set()
    return vetados


def frame_sin_contenido(desc):
    """True si la anotación dice que la imagen no enseña un gráfico.

    Un fotograma de una diapositiva de título o de un gráfico en blanco no
    ilustra nada aunque su texto mencione el concepto: es el mismo tipo de
    error que publicar la captura de Judas Swing bajo la nota de IFVG, pero por
    la vía opuesta —aquí la anotación avisa de que no hay nada que ver y la
    regla anterior no lo miraba.
    """
    return bool(_AUSENCIA.search((desc or "").lower()))


def candidate_frames(con, concepto):
    """Fotogramas para un concepto, solo si la anotación los respalda.

    Antes bastaba con que existiera una fila de `evidence` con `frame_id` para
    colocar la imagen, sin leer la anotación. Eso metió en la nota de IFVG una
    captura cuyo comentario dice literalmente «no hay un rótulo legible que
    identifique el primer IFVG». Ahora manda la anotación:

    - rango 0: la anotación nombra el concepto (lo muestra);
    - rango 1: la anotación no lo nombra pero no lo niega (contexto);
    - rango 2: fotograma pendiente de anotación etiquetado con el concepto.

    Se descarta cualquier fotograma cuya anotación niegue el concepto.
    """
    cid = concepto["id"]
    alts = concepto["alts"]
    # Alias que identifican el concepto sin ambigüedad; si no hay, se usan
    # todos (peor evidencia, pero al menos queda etiquetada como contexto).
    propias = concepto.get("alts_propias") or alts
    alias_globales = global_aliases(con)
    vetados = vetos_de(con, cid)
    picked = []
    seen = set()

    def add(row, rank, why):
        if row["id"] in seen or rank is None:
            return
        seen.add(row["id"])
        picked.append((rank, row, why))

    # 1) Evidencia con frame_id explícito.
    for ev in con.execute(
        "SELECT * FROM evidence WHERE entity_type='concept' AND entity_id=? AND frame_id IS NOT NULL",
        (cid,),
    ):
        fr = con.execute("SELECT * FROM frames WHERE id=?", (ev["frame_id"],)).fetchone()
        if not fr:
            continue
        # Un fotograma sin anotar no se puede verificar: no se publica como
        # ilustración del concepto, tenga o no fila de evidencia.
        if not frame_is_annotated(fr):
            continue
        desc = fr["description"] or ""
        if niega_concepto(desc, alts, cid, alias_globales):
            continue
        if frame_sin_contenido(desc) or fr["id"] in vetados:
            continue
        muestra = justifica_concepto(desc, propias)
        add(fr, 0 if muestra else 1,
            "la anotación describe el concepto" if muestra else "la anotación no nombra el concepto")

    # 2) Fotogramas anotados que nombran el concepto en su descripción.
    #
    # Se mira **solo `description`**, que es lo que el anotador vio en pantalla.
    # `analysis` es la transcripción: dice lo que se hablaba, no lo que se veía.
    for fr in con.execute("SELECT * FROM frames"):
        if not frame_is_annotated(fr):
            continue
        desc = fr["description"] or ""
        if (justifica_concepto(desc, propias)
                and not niega_concepto(desc, alts, cid, alias_globales)
                and not frame_sin_contenido(desc)
                and fr["id"] not in vetados):
            add(fr, 0, "la anotación describe el concepto")

    # 3) Fotogramas pendientes de anotación: NO se usan como ilustración.
    #
    # Su etiqueta `concepto:` la puso el extractor automático con el primer
    # concepto que sonaba en una ventana de 5 s de la transcripción. Eso dice
    # lo que se hablaba, no lo que se ve en pantalla: es la vía por la que la
    # nota de IFVG acabó mostrando una captura de Judas Swing. Sin anotación no
    # hay forma de verificar la imagen, y el proyecto no inventa.

    picked.sort(key=lambda x: (x[0], x[1]["timestamp_sec"]))
    # Si hay al menos una imagen que muestra el concepto, las de contexto
    # sobran: ilustrar con tres capturas que no enseñan el concepto es peor
    # que no poner ninguna. El contexto queda como recurso único.
    con_muestra = [p for p in picked if p[0] == 0]
    if con_muestra:
        return con_muestra[:3]
    contexto = [p for p in picked if p[0] == 1]
    return contexto[:1]


def limpiar_media():
    """El contenido de media/ es generado; se reconstruye en cada ejecución
    para que los pies de foto no puedan quedar asociados a otro fotograma."""
    if os.path.isdir(MEDIA):
        for name in os.listdir(MEDIA):
            if name.lower().endswith(".webp"):
                os.remove(os.path.join(MEDIA, name))



def asignar_fotogramas(con, conceptos):
    """Reparte los fotogramas entre conceptos: uno no puede probar dos cosas.

    Un fotograma termina publicado en varias notas porque su anotación nombra
    más de un concepto («NQ 5m. SMT en el low y FVG de 5m»). Eso no lo hace
    prueba de los dos: una imagen concreta enseña lo que enseña. Es el mismo
    error que puso un Judas Swing en la nota de IFVG, pero multiplicado.

    Criterio, por orden:
      1. si la fila de `evidence` apunta a este concepto explícitamente, gana;
      2. si no, gana el concepto cuyo alias aparezca **todas** sus veces en la
         anotación (una mención suelta es más probable que sea contexto);
      3. si sigue habiendo empate, gana el alias más largo y específico;
      4. si el empate persiste, el fotograma se queda con el concepto de id
         menor: es una decisión arbitraria pero estable y declarada.

    Devuelve {frame_id: concept_id_dueño}.
    """
    from collections import defaultdict
    peso = defaultdict(dict)  # fid -> {cid: (evidencia, menciones, largo)}
    anotados = {c["id"]: c for c in conceptos}

    for c in conceptos:
        for rank, fr, why in candidate_frames(con, c):
            fid = fr["id"]
            desc = (fr["description"] or "").lower()
            propias = c.get("alts_propias") or c["alts"]
            menciones = sum(1 for a in propias if len(a) > 2 and alt_en_texto(a, desc))
            largo = max((len(a) for a in propias if len(a) > 2 and alt_en_texto(a, desc)), default=0)
            ev = 0
            fila = con.execute(
                "SELECT 1 FROM evidence WHERE entity_type='concept' AND entity_id=? AND frame_id=?",
                (c["id"], fid),
            ).fetchone()
            if fila:
                ev = 1
            peso[fid][c["id"]] = (ev, menciones, largo, rank)

    dueno = {}
    for fid, opciones in peso.items():
        def clave(cid):
            ev, menciones, largo, rank = opciones[cid]
            return (-ev, -menciones, -largo, rank, cid)
        dueno[fid] = sorted(opciones, key=clave)[0]
    return dueno

def build_media(con, concepto, slug_concepto, dry=False):
    rows = candidate_frames(con, concepto)
    lines = []
    used = 0
    for rank, fr, why in rows:
        # Un fotograma solo es prueba de un concepto. Si ya se asignó a otro
        # (o si aquí solo sería contexto), no se vuelve a publicar.
        if DUENO_FOTOGRAMAS and DUENO_FOTOGRAMAS.get(fr["id"], concepto["id"]) != concepto["id"]:
            continue
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
        # Una imagen cuyo comentario no nombra el concepto no es prueba de
        # nada: se publica, pero se dice que es contexto.
        if rank == 1:
            estado += " · imagen de contexto, no muestra el concepto"
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

    # Un alias compartido no identifica nada: «fvg» vale para FVG, pero no
    # demuestra que una imagen sea de IFVG. Solo los alias que pertenecen a un
    # único concepto sirven como prueba visual.
    from collections import Counter
    cuenta = Counter()
    for c in out:
        for a in set(c["alts"]):
            if len(a) > 2 and a not in ALIAS_GENERICOS:
                cuenta[a] += 1
    for c in out:
        c["alts_propias"] = [a for a in c["alts"]
                             if len(a) > 2 and a not in ALIAS_GENERICOS and cuenta[a] == 1]
    return out


def clases_bootcamp(con, tipo, eid, video_principal=""):
    """Clases del bootcamp donde aparece esta entidad.

    No basta con `first_seen_video`: un concepto puede haberse visto primero en
    un recap y aun así tener su clase. Se miran las dos vías y se devuelve la
    lista ordenada por número de día, sin duplicados.
    """
    ids = {video_principal} if video_principal else set()
    for ev in con.execute(
        "SELECT DISTINCT video_id FROM evidence WHERE entity_type=? AND entity_id=?",
        (tipo, eid),
    ):
        if ev["video_id"]:
            ids.add(ev["video_id"])
    if not ids:
        return []
    marcas = ",".join("?" * len(ids))
    filas = con.execute(
        f"SELECT order_num, lesson, video_id FROM curriculum "
        f"WHERE video_id IN ({marcas}) ORDER BY order_num", tuple(ids)
    ).fetchall()
    return filas


def enlace_bootcamp(con, video_id):
    """Enlace a la clase del bootcamp en la que aparece este vídeo, si la hay."""
    if not video_id:
        return ""
    r = con.execute(
        "SELECT order_num, lesson FROM curriculum WHERE video_id=?", (video_id,)
    ).fetchone()
    return _linea_clase(r) if r else ""


def _linea_clase(r):
    titulo = re.sub(r"^Día \d+\s*[—-]\s*", "", r["lesson"])
    return (f"- **Clase del bootcamp:** [[../bootcamp/dia-{r['order_num']:02d}"
            f"|Día {r['order_num']} — {titulo}]]")


def lineas_clases(con, tipo, eid, video_principal=""):
    """Bloque «dónde se explica» con todas las clases aplicables."""
    filas = clases_bootcamp(con, tipo, eid, video_principal)
    if not filas:
        return []
    if len(filas) == 1:
        return [_linea_clase(filas[0])]
    enlaces = " · ".join(
        f"[[../bootcamp/dia-{f['order_num']:02d}|Día {f['order_num']}]]" for f in filas
    )
    return [f"- **Clases del bootcamp:** {enlaces}"]


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
        ]
        nota.cuerpo += lineas_clases(con, "concept", c["id"], c["first_seen_video"])
        nota.cuerpo.append("")
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
        ]
        nota.cuerpo += lineas_clases(con, "rule", r["id"], r["first_seen_video"])
        nota.cuerpo.append("")
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
                   cambios_count, preguntas_count, estado=None):
    """Portada: qué es esto, por dónde entrar y en qué estado está.

    El panel se genera con cifras contadas de la base, no escritas a mano: si
    mañana cambian las notas, la portada cambia con ellas.
    """
    estado = estado or {}
    core = [(c.slug, c.titulo, c.frontmatter.get("categoria", "")) for c in conceptos_notas.values()
            if c.frontmatter.get("categoria") == "CORE"]
    categorias = {}
    for c in conceptos_notas.values():
        cat = c.frontmatter.get("categoria", "") or "Sin categoría"
        categorias[cat] = categorias.get(cat, 0) + 1

    frames_total = estado.get("frames_total", 0)
    frames_anot = estado.get("frames_anotados", 0)
    boot_dias = estado.get("boot_dias", 20)

    panel = {
        "titulo": "El proyecto en cifras",
        "bloques": [
            {"etiqueta": "clases de bootcamp", "valor": boot_dias},
            {"etiqueta": "conceptos", "valor": len(conceptos_notas)},
            {"etiqueta": "reglas", "valor": reglas_count},
            {"etiqueta": "operaciones", "valor": trades_count,
             "nota": "P&L autodeclarado"},
            {"etiqueta": "cambios", "valor": cambios_count},
            {"etiqueta": "preguntas abiertas", "valor": preguntas_count},
        ],
        "barras": [
            {"etiqueta": "Fotogramas con anotación verificable",
             "hecho": frames_anot, "total": frames_total,
             "nota": "el resto está extraído pero sin revisar, y no se publica como prueba visual"},
        ],
        "pie": (
            "Todo lo que aparece en este sitio se regenera desde una base SQLite con "
            "`python 09_AUTOMATION/pipeline.py`. Las cifras de esta portada se cuentan en cada "
            "generación, no se escriben a mano."
        ),
    }

    def _yaml_panel(p):
        salida = ["panel:", f"  titulo: {yaml_str(p['titulo'])}"]
        salida.append("  bloques:")
        for b in p["bloques"]:
            partes = [f"etiqueta: {yaml_str(b['etiqueta'])}", f"valor: {b['valor']}"]
            if b.get("nota"):
                partes.append(f"nota: {yaml_str(b['nota'])}")
            salida.append("    - {" + ", ".join(partes) + "}")
        salida.append("  barras:")
        for b in p["barras"]:
            partes = [f"etiqueta: {yaml_str(b['etiqueta'])}",
                      f"hecho: {b['hecho']}", f"total: {b['total']}"]
            if b.get("nota"):
                partes.append(f"nota: {yaml_str(b['nota'])}")
            salida.append("    - {" + ", ".join(partes) + "}")
        salida.append(f"  pie: {yaml_str(p['pie'])}")
        return salida

    secciones = [
        ("bootcamp", "Bootcamp", f"Las {boot_dias} clases en orden, con lo que da cada una."),
        ("conceptos", "Conceptos", f"{len(conceptos_notas)} conceptos con definición, condiciones y errores."),
        ("reglas", "Reglas operativas", f"{reglas_count} reglas, incluidas las obsoletas con su sustituto."),
        ("operaciones", "Operaciones", f"{trades_count} operaciones analizadas, con el P&L autodeclarado."),
        ("cambios", "Cambios", f"{cambios_count} cambios de criterio documentados."),
        ("preguntas", "Preguntas abiertas", f"{preguntas_count} preguntas sin cerrar."),
        ("comprobador", "Comprobador de fuentes", "Lo que el sitio no puede respaldar, dicho en voz alta."),
    ]
    tarjetas = "\n".join(
        f'<a class="xr-tarjeta" href="./{s}">'
        f'<span class="xr-tarjeta-titulo">{t}</span>'
        f'<span class="xr-tarjeta-desc">{d}</span></a>'
        for s, t, d in secciones
    )

    lines = [
        "---",
        "tipo: portada",
        f"titulo: {yaml_str('Metodología Xavi Ruyra — estudio no oficial')}",
        f"title: {yaml_str('Metodología Xavi Ruyra — estudio no oficial')}",
        f"confianza: {yaml_str('no confirmado')}",
        "estado: vigente",
        'video: ""',
        f"timestamp: {yaml_str('')}",
        "anotaciones: false",
        *_yaml_panel(panel),
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
        "## Por dónde entrar",
        "",
        '<div class="xr-tarjetas">',
        tarjetas,
        "</div>",
        "",
        "## Cómo leer una nota",
        "",
        "Cada nota empieza con una **ficha de fuente**: tipo, confianza, estado y un botón que salta "
        "al minuto exacto del vídeo. Debajo, la nota en sí. Al final, las **anotaciones**: "
        "se puede comentar por sección, sin cuenta.",
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
        lines.append(f"- [[{slug_c}|{titulo_c}]]")
    lines += [
        "",
        "## Fuente y límites",
        "",
        "Los datos se regeneran desde SQLite con `09_AUTOMATION/pipeline.py`. Los fotogramas son "
        "capturas de vídeos públicos usadas como cita visual; las transcripciones completas y los "
        "Reels de Instagram quedan fuera de este sitio.",
        "",
        "Las cifras de operaciones son **autodeclaradas**: no hay extractos de cuenta que las "
        "respalden. El sitio lo repite en cada ficha porque es la diferencia entre documentar y "
        "auditar.",
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
    global DUENO_FOTOGRAMAS
    DUENO_FOTOGRAMAS = asignar_fotogramas(con, conceptos)
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
        estado = _estado_proyecto(con)
        generate_index(notas, slugs_concepto, reglas_count, trades_count,
                       cambios_count, preguntas_count, estado)
        # Páginas de navegación y auditoría.
        try:
            import paginas_sitio
            slugs_regla_todos = {r["id"]: slug(r["name"])
                                 for r in con.execute("SELECT id, name FROM rules")}
            paginas_sitio.generar_bootcamp(con, slugs_concepto)
            paginas_sitio.generar_indices(con, slugs_concepto, slugs_regla_todos)
            paginas_sitio.generar_indice_preguntas(con)
        except Exception as e:  # una página de navegación no debe tumbar el vault
            print(f"AVISO: páginas de navegación: {e}")
        sin_fuente = comprobador_fuentes(con, slugs_concepto, slugs_regla, {}, {})
        print(f"Comprobador de fuentes: {sin_fuente} entidades sin respaldo")

    print(f"Vault: {VAULT}")
    print(f"Conceptos: {len(notas)}")
    print(f"Media: {len(os.listdir(MEDIA)) if os.path.isdir(MEDIA) else 0} archivos")
    if args.limite_conceptos:
        print("Modo prueba: solo conceptos + portada.")
    return 0


def _estado_proyecto(con):
    """Cifras reales para la portada: se cuentan, no se escriben."""
    def uno(sql, *a):
        r = con.execute(sql, a).fetchone()
        return r[0] if r else 0
    total = uno("SELECT COUNT(*) FROM frames")
    # «Anotado» aquí significa con descripción propia, no la etiqueta del
    # extractor ni el aviso de pendiente.
    anotados = uno(
        "SELECT COUNT(*) FROM frames WHERE lower(coalesce(description,'')) "
        "NOT LIKE 'pendiente de anotaci%' AND trim(coalesce(description,'')) NOT IN "
        "('keyword','periodic','scene','visual','deictico','déictico','frame de contexto')"
    )
    dias = uno("SELECT COUNT(*) FROM curriculum")
    return {"frames_total": total, "frames_anotados": anotados, "boot_dias": dias}




# --------------------------------------------------------------------------
# Comprobador de fuentes
# --------------------------------------------------------------------------

def _cuenta_evidencia(con, tipo, eid):
    r = con.execute(
        "SELECT COUNT(*) n FROM evidence WHERE entity_type=? AND entity_id=?",
        (tipo, eid),
    ).fetchone()
    return r["n"] if r else 0


def _tiene_video(con, vid):
    if not vid:
        return False
    return con.execute("SELECT 1 FROM videos WHERE id=?", (vid,)).fetchone() is not None


def comprobador_fuentes(con, slugs_concepto, slugs_regla, slugs_trade, slugs_cambio):
    """Página que dice, sin adornos, qué está respaldado y qué no.

    No corrige nada: hace visible el hueco. Un sitio que se presenta como
    resumen trazable tiene que poder enseñar su propio debe.
    """
    filas = []

    # Conceptos sin evidencia citada.
    for c in con.execute("SELECT id, name, certainty FROM concepts ORDER BY id"):
        n = _cuenta_evidencia(con, "concept", c["id"])
        if n == 0:
            filas.append(("Concepto", c["name"], slugs_concepto.get(c["id"]),
                          confianza(c["certainty"]), 0, "Sin ninguna cita de vídeo."))
    # Reglas sin evidencia.
    for r in con.execute("SELECT id, name, certainty FROM rules ORDER BY id"):
        n = _cuenta_evidencia(con, "rule", r["id"])
        if n == 0:
            filas.append(("Regla", r["name"], slugs_regla.get(r["id"]),
                          confianza(r["certainty"]), 0, "Sin cita; la regla se apoya en el texto."))
    # Fuentes que apuntan a un vídeo que no está en la base.
    for ev in con.execute(
        "SELECT entity_type, entity_id, video_id FROM evidence ORDER BY id"
    ):
        if not _tiene_video(con, ev["video_id"]):
            filas.append((
                "Evidencia",
                f"{ev['entity_type']} #{ev['entity_id']}",
                None,
                "no confirmado",
                0,
                f"El vídeo `{ev['video_id']}` no está en la base: el enlace no se puede comprobar.",
            ))

    # Lo que sí está: cifras de cobertura por tipo, contadas de la base.
    total_conceptos = con.execute("SELECT COUNT(*) n FROM concepts").fetchone()["n"]
    con_ev = con.execute(
        "SELECT COUNT(DISTINCT entity_id) n FROM evidence WHERE entity_type='concept'"
    ).fetchone()["n"]
    total_reglas = con.execute("SELECT COUNT(*) n FROM rules").fetchone()["n"]
    reg_con_ev = con.execute(
        "SELECT COUNT(DISTINCT entity_id) n FROM evidence WHERE entity_type='rule'"
    ).fetchone()["n"]

    panel = {
        "titulo": "Cobertura de fuentes",
        "barras": [
            {"etiqueta": "Conceptos con cita de vídeo", "hecho": con_ev, "total": total_conceptos},
            {"etiqueta": "Reglas con cita de vídeo", "hecho": reg_con_ev, "total": total_reglas},
        ],
        "pie": (
            "«Con cita» significa que la base guarda al menos una fila de evidencia con vídeo y "
            "minuto. No mide si la cita es buena, solo si existe: la lectura crítica es tuya."
        ),
    }

    lineas = [
        "---",
        "tipo: indice",
        f"title: {yaml_str('Comprobador de fuentes')}",
        f"titulo: {yaml_str('Comprobador de fuentes')}",
        f"confianza: {yaml_str('no confirmado')}",
        "estado: vigente",
        'video: ""',
        'timestamp: ""',
        "panel:",
        "  titulo: " + yaml_str(panel["titulo"]),
        "  barras:",
        *[
            f"    - {{etiqueta: {yaml_str(b['etiqueta'])}, hecho: {b['hecho']}, total: {b['total']}}}"
            for b in panel["barras"]
        ],
        "  pie: " + yaml_str(panel["pie"]),
        "---",
        "",
        "# Comprobador de fuentes",
        "",
        "Este sitio se presenta como un resumen **trazable**. Esta página es su propia auditoría: "
        "enumera lo que no tiene fuente y, por tanto, no debería tomarse como establecido.",
        "",
        "## Cómo leer una nota",
        "",
        "| Marca | Significado |",
        "|---|---|",
        "| **explícito** | Se dice literalmente en un vídeo; la nota incluye la cita y el minuto. |",
        "| **observado** | Se deduce de un ejemplo o un recap, no de una regla formulada. |",
        "| **inferido** | Interpretación del proyecto a partir de varias fuentes. |",
        "| **no confirmado** | No hay fuente suficiente. Figura aquí abajo si aplica. |",
        "",
        "## Qué falta",
        "",
    ]
    if not filas:
        lineas += [
            "> [!success] Todo tiene fuente",
            "> Todas las entidades tienen al menos una cita y todos los vídeos citados están en la base.",
            "",
        ]
    else:
        lineas += [
            '<div class="xr-aviso" data-tono="warn">',
            f"**{len(filas)} entidades sin respaldo comprobable.** Aparecen listadas; ninguna se ha "
            "borrado ni se ha rellenado con una fuente inventada.",
            "</div>",
            "",
            "| Tipo | Entidad | Confianza | Qué le falta |",
            "|---|---|---|---|",
        ]
        for tipo, nombre, s, conf, _, motivo in filas:
            enlace = f"[{nombre}](../{ {'Concepto': 'conceptos', 'Regla': 'reglas'}[tipo] }/{s})" if s and tipo in ("Concepto", "Regla") else nombre
            lineas.append(f"| {tipo} | {enlace} | {conf} | {motivo} |")
        lineas.append("")

    lineas += [
        "## Regla del proyecto",
        "",
        "Cuando no hay fuente, no se rellena: se marca. Las anotaciones de fotogramas y las "
        "preguntas abiertas existen para eso, y por eso el sitio puede decir en voz alta lo que "
        "todavía no sabe.",
        "",
    ]
    with open(os.path.join(VAULT, "comprobador.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas))
    return len(filas)


if __name__ == "__main__":
    sys.exit(main())

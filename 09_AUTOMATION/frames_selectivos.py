#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracción selectiva de fotogramas para la Fase 0.

Reutiliza el pipeline existente:
  - funciones `hhmmss`, `find_transcript`, `load_segments`, `keyword_hits`,
    `dedupe`, `extract_at` y el formato de salida (index.csv + tabla `frames`)
    de `09_AUTOMATION/extract_frames.py`;
  - el criterio de palabras clave se amplía con los alias del glosario vivo
    de la base (concepts, categorías CORE y SUPPORTING, estado vigente).

Añade lo que el pipeline original no tenía:
  - detección de cambios de pantalla por hash perceptual (la detección de
    escena de FFmpeg no funciona en capturas de TradingView);
  - selección de 8–15 fotogramas por vídeo (3–6 en clases de psicología);
  - descarte de fotogramas casi idénticos por hash perceptual;
  - registro como «pendiente de anotación» en `frames`, sin borrar nunca
    fotogramas existentes (el extractor original hacía DELETE por vídeo).

Uso:
  python 09_AUTOMATION/frames_selectivos.py --videos 1McPSXSSR48
  python 09_AUTOMATION/frames_selectivos.py --lote 10 --grupo 1
  python 09_AUTOMATION/frames_selectivos.py --videos A,B --dry-run
  python 09_AUTOMATION/frames_selectivos.py --marcar-caidos

Requiere: ffmpeg (se localiza automáticamente) y yt-dlp para descargar.
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
FRAMES_DIR = os.path.join(BASE, "03_FRAMES")
VIDEO_DIR = os.path.join(FRAMES_DIR, "videos")
BIN_DIR = os.path.join(BASE, "09_AUTOMATION", ".bin")

sys.path.insert(0, os.path.join(BASE, "09_AUTOMATION"))
from extract_frames import hhmmss, find_transcript, load_segments, extract_at  # noqa: E402

DEIXIS = [
    "aquí", "aqui", "como ven", "como veis", "este nivel", "esta zona",
    "fíjate", "fijate", "mira", "se ve", "lo tenéis", "lo teneis",
    "marcado", "os marco", "dibujo", "este punto", "justo aquí",
    "justo aqui", "fijaos", "observad", "veis aquí", "veís aquí",
]

PSICOLOGIA = {"PSYCHOLOGY"}
# Clases del bootcamp que son de psicología/mentalidad (no técnicas): tienen
# poco material visual y no necesitan 8–15 capturas.
PSICO_BOOTCAMP = {
    "t9rcx-dDGvA", "NDVbDdE5TW0", "mBHtx-BfWWg", "GO9GLSF_vLo",
    "WHz8ySmAcnQ", "ZOxEUWwDSoQ", "eH7QCo2d0TU", "djkeIcfNGgs",
    "2kBd2-bLuwU", "ygJya0srm8g",
}


# --------------------------------------------------------------------------
# Entorno (ffmpeg / yt-dlp)
# --------------------------------------------------------------------------

def _candidates_ffmpeg():
    yield os.environ.get("FFMPEG_BIN")
    yield shutil.which("ffmpeg")
    yield os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
        r"\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    )
    # AutoDownloader (imageio-ffmpeg): único ffmpeg verificado en esta máquina.
    root = os.path.expanduser("~")
    for pattern_dir in (
        os.path.join(root, "Documents", "AutoDownloader", ".venv", "Lib", "site-packages",
                     "imageio_ffmpeg", "binaries"),
    ):
        if os.path.isdir(pattern_dir):
            for name in sorted(os.listdir(pattern_dir)):
                if name.lower().startswith("ffmpeg") and name.lower().endswith(".exe"):
                    yield os.path.join(pattern_dir, name)


def resolve_ffmpeg():
    for c in _candidates_ffmpeg():
        if c and os.path.isfile(c):
            return c
    raise RuntimeError("No se encontró ffmpeg. Define FFMPEG_BIN.")


def prepare_bin(ffmpeg_path):
    """Crea 09_AUTOMATION/.bin/ffmpeg.exe como enlace duro para que el
    pipeline reutilizado (que llama a 'ffmpeg') lo encuentre en el PATH."""
    os.makedirs(BIN_DIR, exist_ok=True)
    alias = os.path.join(BIN_DIR, "ffmpeg.exe")
    if not os.path.exists(alias):
        try:
            os.link(ffmpeg_path, alias)
        except OSError:
            shutil.copy2(ffmpeg_path, alias)
    os.environ["PATH"] = BIN_DIR + os.pathsep + os.environ.get("PATH", "")
    return alias


def yt_dlp_cmd():
    p = shutil.which("yt-dlp")
    if p:
        return [p]
    root = os.path.expanduser("~")
    cand = os.path.join(root, "Documents", "AutoDownloader", ".venv", "Scripts", "yt-dlp.exe")
    if os.path.isfile(cand):
        return [cand]
    return None


# --------------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------------

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def load_glosario(con):
    """Nombre + alias de los conceptos vigentes que se usan en la metodología."""
    out = []
    for row in con.execute(
        "SELECT name, aliases FROM concepts "
        "WHERE status='vigente' AND category IN ('CORE','SUPPORTING')"
    ):
        alts = [row["name"]] + [a for a in (row["aliases"] or "").split(",")]
        alts = [a.strip().lower() for a in alts if a and len(a.strip()) > 2]
        if alts:
            out.append((row["name"], alts))
    return out


def video_row(con, vid):
    return con.execute("SELECT * FROM videos WHERE id=?", (vid,)).fetchone()


def media_path(vid):
    for ext in (".mp4", ".webm", ".mkv"):
        p = os.path.join(VIDEO_DIR, vid + ext)
        if os.path.exists(p):
            return p
    return None


def duration_of(con, vid, path):
    row = video_row(con, vid)
    if row and row["duration_sec"]:
        return float(row["duration_sec"])
    ff = resolve_ffmpeg()
    proc = subprocess.run([ff, "-hide_banner", "-i", path], capture_output=True, text=True)
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"No se pudo leer la duración de {path}")


# --------------------------------------------------------------------------
# Descarga
# --------------------------------------------------------------------------

def download(vid, force=False):
    path = media_path(vid)
    if path and not force:
        return path, "ya existía"
    exe = yt_dlp_cmd()
    if not exe:
        raise RuntimeError("yt-dlp no está instalado")
    ff = resolve_ffmpeg()
    os.makedirs(VIDEO_DIR, exist_ok=True)
    out = os.path.join(VIDEO_DIR, vid + ".%(ext)s")
    cmd = exe + [
        "--no-warnings", "--ffmpeg-location", ff,
        "-f", "bv*[height<=480]+ba/b[height<=480]/b",
        "--merge-output-format", "mp4",
        "-o", out,
        f"https://www.youtube.com/watch?v={vid}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    path = media_path(vid)
    if not path:
        msg = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise RuntimeError(msg[-1] if msg else "descarga fallida")
    return path, "descargado"


# --------------------------------------------------------------------------
# Señales
# --------------------------------------------------------------------------

def alt_en_texto(alt, text):
    """Coincidencia por palabra/frase completa (evita EMA dentro de «tema»)."""
    patron = r"(?<![a-z0-9áéíóúüñ])" + re.escape(alt.lower()) + r"(?![a-z0-9áéíóúüñ])"
    return re.search(patron, text.lower()) is not None


def transcript_candidates(segments, glosario):
    """Devuelve [(ts, concepto|None, frase, motivo)] agrupados por ventana de 5 s."""
    by_window = {}
    for seg in segments:
        ts = float(seg.get("start") or 0)
        text = (seg.get("text") or "").strip()
        tl = text.lower()
        hits = [name for name, alts in glosario if any(alt_en_texto(a, tl) for a in alts)]
        is_deixis = any(d in tl for d in DEIXIS)
        if not hits and not is_deixis:
            continue
        w = int(ts // 5) * 5
        entry = by_window.setdefault(w, {"ts": ts, "concepts": [], "frase": "", "deixis": False})
        for h in hits:
            if h not in entry["concepts"]:
                entry["concepts"].append(h)
        if is_deixis:
            entry["deixis"] = True
        if text and len(text) > len(entry["frase"]):
            entry["frase"] = text
    out = []
    for w in sorted(by_window):
        e = by_window[w]
        motivo = "keyword" if e["concepts"] else "deictico"
        out.append((e["ts"], e["concepts"][0] if e["concepts"] else None,
                    e["frase"], motivo, e["deixis"], len(e["concepts"])))
    return out


def dhash(path, size=8):
    """dHash de 64 bits con Pillow; None si no se puede leer."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        img = Image.open(path).convert("L").resize((size + 1, size), Image.LANCZOS)
        px = list(img.tobytes())
        bits = 0
        for row in range(size):
            for col in range(size):
                left = px[row * (size + 1) + col]
                right = px[row * (size + 1) + col + 1]
                bits = (bits << 1) | (1 if left > right else 0)
        return bits
    except Exception:
        return None


def hamming(a, b):
    return bin(a ^ b).count("1")


def perfil_frame(path):
    """(proporcion_plano, tinta). Una captura de pantalla de gráfico tiene un
    fondo liso dominante >~0,85; una cámara hablando, <~0,30. Sirve para no
    elegir la webcam como fragmento visual de un concepto técnico."""
    try:
        from PIL import Image
        from collections import Counter
    except ImportError:
        return 1.0, 0.01
    try:
        im = Image.open(path).convert("L")
        w, h = im.size
        c = im.crop((int(w * 0.06), int(h * 0.10), int(w * 0.72), int(h * 0.88)))
        c = c.resize((220, 140), Image.LANCZOS)
        px = list(c.getdata())
        n = len(px)
        modal = Counter(px).most_common(1)[0][0]
        plano = sum(1 for p in px if abs(p - modal) <= 6) / n
        tinta = sum(1 for p in px if p < 110) / n
        return plano, tinta
    except Exception:
        return 1.0, 0.01


def croma(path):
    """Fracción de píxeles con color saturado en el área del gráfico. Una cámara
    a pantalla completa (piel, ropa, habitación) da valores altos; un gráfico
    gris de TradingView, muy bajos. Es el discriminador que separa «pantalla»
    de «cámara hablando». Se mide solo el centro: la webcam del presentador
    suele ir en una esquina."""
    try:
        from PIL import Image
    except ImportError:
        return 0.0
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
        return sat / len(px)
    except Exception:
        return 0.0


def es_pantalla(path, max_croma=0.13):
    """True si parece captura de pantalla/gráfico y no cámara hablando."""
    return croma(path) <= max_croma


def frame_vacio(path, min_tinta=0.0008):
    """True si la zona del gráfico no tiene tinta (lienzo vacío, sin velas ni
    anotaciones). La barra de TradingView y la webcam no cuentan: se mide solo
    el área central del gráfico."""
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


def sample_visual_changes(video_path, ffmpeg, interval=5.0, work_dir=None):
    """Muestrea el vídeo cada `interval` s y devuelve timestamps donde el
    contenido cambia de forma perceptible (hash perceptual)."""
    from PIL import Image
    tmp = work_dir or os.path.join(BIN_DIR, "tmp_frames")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error",
        "-i", video_path,
        "-vf", f"fps=1/{interval},scale=160:-2",
        "-q:v", "5", os.path.join(tmp, "%05d.jpg"),
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    files = sorted(os.listdir(tmp))
    prev = None
    changes = []
    for i, name in enumerate(files):
        h = dhash(os.path.join(tmp, name), 8)
        if h is None:
            continue
        if prev is not None and hamming(prev, h) >= 10:
            changes.append(round((i + 1) * interval, 2))
        prev = h
    shutil.rmtree(tmp, ignore_errors=True)
    return changes


# --------------------------------------------------------------------------
# Selección
# --------------------------------------------------------------------------

def select_candidates(transcript_cands, visual_changes, duration, cap_min, cap_max, min_gap):
    """Fusiona señales, puntúa y elige entre cap_min y cap_max timestamps."""
    merged = {}
    for ts, concept, frase, motivo, deixis, n_concepts in transcript_cands:
        key = int(round(ts))
        merged.setdefault(key, {"ts": ts, "concepts": set(), "frase": "", "deixis": False,
                                "visual": False, "score": 0.0})
        item = merged[key]
        if concept:
            item["concepts"].add(concept)
        item["deixis"] = item["deixis"] or deixis
        if frase and len(frase) > len(item["frase"]):
            item["frase"] = frase
        item["score"] = 2.0 * len(item["concepts"]) + (1.0 if item["deixis"] else 0.0)

    for ts in visual_changes:
        # Asocia el cambio visual al candidato textual más cercano (<= 8 s) o crea uno.
        best = None
        for key in merged:
            if abs(merged[key]["ts"] - ts) <= 8:
                if best is None or abs(merged[best]["ts"] - ts) > abs(merged[key]["ts"] - ts):
                    best = key
        if best is not None:
            merged[best]["visual"] = True
            merged[best]["score"] += 1.5
        else:
            merged[int(round(ts))] = {"ts": ts, "concepts": set(), "frase": "",
                                      "deixis": False, "visual": True, "score": 1.5}

    ranked = sorted(merged.values(), key=lambda x: -x["score"])
    chosen = []
    for item in ranked:
        if len(chosen) >= cap_max:
            break
        if item["score"] <= 0:
            continue
        if all(abs(item["ts"] - c["ts"]) >= min_gap for c in chosen):
            chosen.append(item)
    if len(chosen) < cap_min:
        # Relleno con candidatos visuales/textuales aunque estén más juntos.
        for item in sorted(merged.values(), key=lambda x: -x["score"]):
            if len(chosen) >= cap_min:
                break
            if item in chosen:
                continue
            if all(abs(item["ts"] - c["ts"]) >= max(8.0, min_gap / 2) for c in chosen):
                chosen.append(item)
    return sorted(chosen, key=lambda x: x["ts"])


# --------------------------------------------------------------------------
# Procesado de un vídeo
# --------------------------------------------------------------------------

def process_video(con, vid, glosario, dry_run=False, force_download=False, rehacer=False):
    row = video_row(con, vid)
    if not row:
        return {"vid": vid, "estado": "no existe en catálogo"}
    existing = con.execute("SELECT COUNT(*) FROM frames WHERE video_id=?", (vid,)).fetchone()[0]
    if existing and not dry_run:
        if not rehacer:
            return {"vid": vid, "estado": f"omitido: ya tiene {existing} fotogramas"}
        # Rehacer solo los fotogramas pendientes de anotación; las anotaciones
        # manuales no se tocan nunca.
        pend = con.execute(
            "SELECT id, path FROM frames WHERE video_id=? AND description LIKE 'pendiente de anotación%'",
            (vid,),
        ).fetchall()
        for pid, rel in pend:
            fpath = os.path.join(BASE, rel)
            if os.path.exists(fpath):
                os.remove(fpath)
            con.execute("DELETE FROM frames WHERE id=?", (pid,))
        con.commit()

    path, note = download(vid, force=force_download) if not dry_run else (media_path(vid), "sin descargar (dry-run)")
    if not path:
        return {"vid": vid, "estado": "sin medio local y dry-run"}

    ffmpeg = resolve_ffmpeg()
    prepare_bin(ffmpeg)
    duration = duration_of(con, vid, path)
    segs_path = find_transcript(vid)
    segments = load_segments(segs_path)
    if not segments:
        return {"vid": vid, "estado": "sin transcripción"}

    is_psy = (row["category"] or "").upper() in PSICOLOGIA or vid in PSICO_BOOTCAMP
    cap_min, cap_max, min_gap = (3, 6, 30.0) if is_psy else (8, 15, 20.0)

    t_cands = transcript_candidates(segments, glosario)
    v_changes = sample_visual_changes(path, ffmpeg, interval=5.0)
    chosen = select_candidates(t_cands, v_changes, duration, cap_min, cap_max, min_gap)

    if dry_run:
        return {"vid": vid, "estado": "dry-run", "candidatos": len(t_cands),
                "cambios_visuales": len(v_changes), "elegidos": len(chosen),
                "timestamps": [round(c["ts"], 1) for c in chosen]}

    out_dir = os.path.join(FRAMES_DIR, vid)
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    hashes = []
    for item in chosen:
        ts = min(item["ts"] + 1.0, max(duration - 1.0, 0))  # tras la transición
        concept = "; ".join(sorted(item["concepts"])) if item["concepts"] else None
        motivo = "keyword" if item["concepts"] else ("deictico" if item["deixis"] else "visual")
        name = f"{len(rows) + 1:04d}_{hhmmss(ts)}_{motivo}.jpg"
        out_path = os.path.join(out_dir, name)
        if not extract_at(path, ts, out_path):
            continue
        if frame_vacio(out_path):
            os.remove(out_path)
            continue
        if not es_pantalla(out_path):
            os.remove(out_path)
            continue
        h = dhash(out_path, 8)
        if h is not None and any(hamming(h, prev) <= 4 for prev in hashes):
            os.remove(out_path)
            continue
        hashes.append(h)
        rows.append({
            "video_id": vid,
            "timestamp_sec": round(ts, 3),
            "timestamp": hhmmss(ts),
            "path": os.path.relpath(out_path, BASE).replace("\\", "/"),
            "reason": motivo,
            "transcript": (item["frase"] or "")[:900],
            "concepto": concept,
        })

    index_path = os.path.join(out_dir, "index.csv")
    with open(index_path, "w", encoding="utf-8", newline="") as fh:
        import csv
        writer = csv.DictWriter(fh, fieldnames=[
            "video_id", "timestamp_sec", "timestamp", "path", "reason", "transcript", "concepto",
        ])
        writer.writeheader()
        writer.writerows(rows)

    for r in rows:
        desc = "pendiente de anotación"
        if r["concepto"]:
            desc += f" | concepto: {r['concepto']}"
        desc += f" | motivo: {r['reason']}"
        con.execute(
            "INSERT INTO frames(video_id, timestamp_sec, path, description, analysis) VALUES (?,?,?,?,?)",
            (vid, r["timestamp_sec"], r["path"], desc, r["transcript"] or None),
        )
    con.commit()

    return {"vid": vid, "estado": "ok", "descarga": note, "duracion": round(duration, 1),
            "candidatos_texto": len(t_cands), "cambios_visuales": len(v_changes),
            "elegidos": len(rows), "carpeta": os.path.relpath(out_dir, BASE)}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def mark_unavailable(con):
    ids = [
        "Kmp7NNgdVec", "Hy64veaxjbA", "qphnTygzhpY", "jlNNLj3wO3E",
        "uLaWblY79LU", "chmAtNLplRM", "28sqDyo9wyw", "gtdRDaVVikk", "mOcRbnw1G3k",
    ]
    cur = con.cursor()
    cur.execute("PRAGMA user_version")
    for vid in ids:
        cur.execute("UPDATE videos SET status='no_disponible', updated_at=CURRENT_TIMESTAMP WHERE id=?", (vid,))
    con.commit()
    return len(ids)


def limpiar_camara(con):
    """Elimina fotogramas pendientes que en realidad son cámara hablando y
    renumera el index.csv de cada vídeo afectado. Nunca toca los anotados."""
    rows = con.execute("SELECT id, video_id, path FROM frames "
                       "WHERE description LIKE 'pendiente de anotación%'").fetchall()
    borrados = 0
    videos = set()
    for fid, vid, rel in rows:
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            continue
        if es_pantalla(path):
            continue
        os.remove(path)
        con.execute("DELETE FROM frames WHERE id=?", (fid,))
        borrados += 1
        videos.add(vid)
    con.commit()
    for vid in videos:
        reescribir_index(con, vid)
    return borrados


def reescribir_index(con, vid):
    """Sincroniza index.csv con lo que queda en `frames` para ese vídeo."""
    import csv
    rows = con.execute(
        "SELECT video_id, timestamp_sec, path, description, analysis FROM frames "
        "WHERE video_id=? ORDER BY timestamp_sec", (vid,)
    ).fetchall()
    out_dir = os.path.join(FRAMES_DIR, vid)
    os.makedirs(out_dir, exist_ok=True)
    index_path = os.path.join(out_dir, "index.csv")
    with open(index_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "video_id", "timestamp_sec", "timestamp", "path", "reason", "transcript", "concepto",
        ])
        writer.writeheader()
        for r in rows:
            desc = r["description"] or ""
            motivo = desc.split("motivo:")[-1].strip() if "motivo:" in desc else ""
            concepto = desc.split("concepto:")[-1].split("|")[0].strip() if "concepto:" in desc else ""
            writer.writerow({
                "video_id": r["video_id"],
                "timestamp_sec": r["timestamp_sec"],
                "timestamp": hhmmss(r["timestamp_sec"]),
                "path": r["path"],
                "reason": motivo,
                "transcript": r["analysis"] or "",
                "concepto": concepto,
            })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", help="IDs separados por coma")
    ap.add_argument("--lote", type=int, help="Nº de vídeos a procesar")
    ap.add_argument("--grupo", type=int, choices=[1, 2, 3, 4],
                    help="1 bootcamp, 2 con operaciones, 3 edu/recap, 4 resto")
    ap.add_argument("--prioridad", action="store_true",
                    help="Ordenar pendientes por la prioridad acordada")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force-download", action="store_true")
    ap.add_argument("--rehacer", action="store_true",
                    help="Rehace solo los fotogramas pendientes de anotación de los vídeos indicados")
    ap.add_argument("--limpiar-camara", action="store_true",
                    help="Elimina los fotogramas pendientes que en realidad son cámara hablando")
    ap.add_argument("--marcar-caidos", action="store_true")
    args = ap.parse_args()

    con = connect()
    if args.marcar_caidos:
        n = mark_unavailable(con)
        print(f"Marcados como no_disponible: {n}")
        return 0
    if args.limpiar_camara:
        n = limpiar_camara(con)
        print(f"Fotogramas de cámara eliminados: {n}")
        return 0

    glosario = load_glosario(con)
    print(f"Glosario: {len(glosario)} conceptos vigentes CORE/SUPPORTING")

    if args.videos:
        vids = [v.strip() for v in args.videos.split(",") if v.strip()]
    else:
        rows = con.execute(
            """SELECT v.id, v.category FROM videos v
               WHERE v.in_scope=1 AND v.status<>'no_disponible'
                 AND EXISTS (SELECT 1 FROM segments s WHERE s.video_id=v.id)
                 AND NOT EXISTS (SELECT 1 FROM frames f WHERE f.video_id=v.id)
               ORDER BY v.upload_date"""
        ).fetchall()
        def grupo(r):
            if r["category"] == "BOOTCAMP":
                return 1
            tr = con.execute("SELECT COUNT(*) FROM trades WHERE video_id=?", (r["id"],)).fetchone()[0]
            if tr:
                return 2
            if r["category"] in ("EDUCATIONAL", "TRADE_RECAP"):
                return 3
            return 4
        if args.grupo:
            rows = [r for r in rows if grupo(r) == args.grupo]
        if args.prioridad:
            rows = sorted(rows, key=lambda r: (grupo(r), r["id"]))
        vids = [r["id"] for r in rows]
        if args.lote:
            vids = vids[:args.lote]

    if not vids:
        print("Nada que procesar.")
        return 0

    print(f"Vídeos a procesar: {len(vids)}")
    results = []
    for i, vid in enumerate(vids, 1):
        print(f"\n[{i}/{len(vids)}] {vid}")
        try:
            res = process_video(con, vid, glosario, dry_run=args.dry_run,
                                force_download=args.force_download, rehacer=args.rehacer)
        except Exception as exc:
            res = {"vid": vid, "estado": f"ERROR: {type(exc).__name__}: {exc}"}
        results.append(res)
        print("  " + json.dumps(res, ensure_ascii=False))

    out = os.path.join(BASE, "10_REPORTS", "lotes",
                       f"lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)
    print(f"\nResultados: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

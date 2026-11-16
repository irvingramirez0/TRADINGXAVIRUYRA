#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronización manual del canal de Xavi Ruyra y del bootcamp.

Qué hace:
1. Lee el RSS oficial del canal.
2. Compara los vídeos con la tabla `videos` de la base de conocimiento.
3. Registra los nuevos (título, fecha, URL, descripción, visitas).
4. Detecta si alguno es del bootcamp.
5. Escribe un reporte diario en 10_REPORTS/daily/.
6. Registra la comprobación en `sync_log` y en 09_AUTOMATION/logs/.

Uso:
    python3 09_AUTOMATION/sync_bootcamp.py
    python3 09_AUTOMATION/sync_bootcamp.py --download
    python3 09_AUTOMATION/sync_bootcamp.py --download --process

--download  descarga subtítulos automáticos en español + info.json del bootcamp nuevo.
--process   después de descargar, reconstruye transcripciones limpias y reindexa la DB.

Nota honesta:
- Este script NO se ejecuta solo. La ejecución automática depende de que se cree una
  tarea programada en Claude Desktop (mcp__scheduled-tasks__create_scheduled_task).
- Si la app está cerrada a la hora programada, la tarea se ejecuta al abrirla.
- El RSS devuelve las últimas ~15 publicaciones. Con una comprobación diaria es suficiente;
  si el canal publicara más de 15 vídeos entre dos comprobaciones, habría que usar yt-dlp.
"""

import argparse
import glob
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
CHANNEL_ID = "UCGlOTZY4Cvsa4PiBNKPSq3A"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
CHANNEL_NAME = "Xavi Ruyra"
LOG_DIR = os.path.join(BASE, "09_AUTOMATION", "logs")
REPORT_DIR = os.path.join(BASE, "10_REPORTS", "daily")
CATALOG_UPDATES = os.path.join(BASE, "01_CATALOG", "sync_new_videos.jsonl")

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


def now():
    return datetime.now()


def ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(CATALOG_UPDATES), exist_ok=True)


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    con.execute("PRAGMA synchronous=OFF")
    return con


def categorize(title):
    t = (title or "").lower()
    if "bootcamp" in t:
        return "BOOTCAMP"
    if "trade recap" in t or "road to payout" in t or "bias " in t:
        return "TRADE_RECAP"
    if any(k in t for k in ["psicolog", "mentalidad", "disciplina", "miedo", "reglas", "sistema"]):
        return "PSYCHOLOGY"
    if any(k in t for k in ["miami", "dubai", "cumplea", "paraca", "coche", "vida de", "compras", "viaje"]):
        return "VLOG"
    if any(k in t for k in ["estrategia", "concepto", "liquidez", "fvg", "ifvg", "cisd", "po3", "dol",
                            "equilibrium", "backtest", "gestion", "gestión", "riesgo", "calcular",
                            "empezar", "guia", "guía", "explico", "como ", "cómo "]):
        return "EDUCATIONAL"
    return "OTHER"


def priority(title, category):
    t = (title or "").lower()
    if category == "BOOTCAMP":
        return 1
    if any(k in t for k in ["simple estrategia", "ifvg updated", "aplicando la mejor estrategia",
                            "cisd", "dol", "equilibrium", "fvg", "po3", "gestion de riesgo",
                            "gestión de riesgo", "break-even", "daily bias", "masterclass"]):
        return 1
    if category in ("EDUCATIONAL", "TRADE_RECAP"):
        return 2
    return 3


def fetch_rss():
    req = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; XaviKB/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    root = ET.fromstring(raw)
    entries = []
    for entry in root.findall("atom:entry", NS):
        vid = entry.findtext("yt:videoId", default="", namespaces=NS)
        title = entry.findtext("atom:title", default="", namespaces=NS)
        published = entry.findtext("atom:published", default="", namespaces=NS)
        updated = entry.findtext("atom:updated", default="", namespaces=NS)
        link_el = entry.find("atom:link", NS)
        link = link_el.get("href") if link_el is not None else f"https://www.youtube.com/watch?v={vid}"
        group = entry.find("media:group", NS)
        description = ""
        views = None
        if group is not None:
            description = group.findtext("media:description", default="", namespaces=NS) or ""
            stats = group.find("media:community/media:statistics", NS)
            if stats is not None:
                try:
                    views = int(stats.get("views"))
                except (TypeError, ValueError):
                    views = None
        upload_date = published[:10].replace("-", "") if published else None
        entries.append({
            "id": vid,
            "title": title,
            "published": published,
            "updated": updated,
            "upload_date": upload_date,
            "url": link,
            "description": description,
            "view_count": views,
        })
    return entries


def fetch_ytdlp_index(limit=15):
    """Respaldo cuando el RSS no responde: lista los últimos vídeos con yt-dlp.

    El modo --flat-playlist no trae fecha ni descripción; se completan después
    solo para los vídeos que no estén ya en la base.
    """
    exe = yt_dlp_cmd()
    if not exe:
        raise RuntimeError("el RSS falló y yt-dlp no está instalado")
    url = f"https://www.youtube.com/channel/{CHANNEL_ID}/videos"
    cmd = exe + ["--flat-playlist", "--playlist-end", str(limit), "--dump-json",
                 "--extractor-args", "youtube:lang=es", url]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp falló: {proc.stderr.strip()[:300]}")
    entries = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        vid = d.get("id")
        if not vid:
            continue
        entries.append({
            "id": vid,
            "title": d.get("title") or "",
            # `--flat-playlist` no trae fecha, pero sí el id; el reporte
            # imprimía «Bootcamp Día 21: … ()» porque `published` quedaba
            # vacío y el formato corta a 10 caracteres. Se deja constancia con
            # `upload_date` cuando yt-dlp lo da, y `""` cuando no: la función
            # que completa metadatos lo rellena luego.
            "published": d.get("upload_date") or "",
            "updated": "",
            "upload_date": d.get("upload_date"),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "description": "",
            "view_count": d.get("view_count"),
        })
    if not entries:
        raise RuntimeError("yt-dlp no devolvió vídeos")
    return entries


def fetch_video_meta(video_id):
    """Metadatos de un vídeo concreto con yt-dlp (para el respaldo sin RSS)."""
    exe = yt_dlp_cmd()
    if not exe:
        return {}
    cmd = exe + ["--skip-download", "--dump-json", "--extractor-args", "youtube:lang=es",
                 f"https://www.youtube.com/watch?v={video_id}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        return {}
    try:
        d = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}
    return {
        "title": d.get("title") or "",
        "upload_date": d.get("upload_date"),
        "duration": d.get("duration"),
        "description": d.get("description") or "",
        "view_count": d.get("view_count"),
        "published": d.get("upload_date") or "",
    }


def load_known_ids(con):
    return {row[0] for row in con.execute("SELECT id FROM videos")}


def is_bootcamp(title):
    t = (title or "").lower()
    return "bootcamp" in t or bool(re.search(r"\bd[ií]a\s+\d+", t))


def append_catalog(entry, category):
    record = {
        "id": entry["id"],
        "title": entry["title"],
        "upload_date": entry["upload_date"],
        "duration": None,
        "view_count": entry["view_count"],
        "url": entry["url"],
        "description": entry["description"],
        "category": category,
        "source": "youtube_rss",
        "detected_at": now().isoformat(timespec="seconds"),
    }
    with open(CATALOG_UPDATES, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def insert_video(con, entry, category):
    prio = priority(entry["title"], category)
    con.execute(
        """INSERT OR IGNORE INTO videos
           (id, title, upload_date, duration_sec, url, channel, description,
            view_count, category, priority, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            entry["id"], entry["title"], entry["upload_date"], None, entry["url"],
            CHANNEL_NAME, entry["description"], entry["view_count"], category, prio,
            "catalogado",
        ),
    )
    con.execute(
        "UPDATE videos SET title=?, upload_date=?, url=?, description=?, view_count=?, "
        "category=?, priority=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (
            entry["title"], entry["upload_date"], entry["url"], entry["description"],
            entry["view_count"], category, prio, entry["id"],
        ),
    )


def directorio_bin():
    """Carpeta de binarios del propio proyecto.

    Existe por el entorno donde corre la tarea programada: Claude Desktop monta
    el proyecto en un sandbox Linux (`/sessions/…/mnt/TRADINGXAVIRUYRA`) donde
    `~` no es `C:\\Users\\Asus` y el venv de AutoDownloader no existe. Una ruta
    absoluta fuera del proyecto no cruza esa frontera; una ruta relativa a
    `BASE` sí. Es el mismo criterio que ya usaba `frames_selectivos.py` con
    `ffmpeg` (`09_AUTOMATION/.bin/`).
    """
    return os.path.join(BASE, "09_AUTOMATION", ".bin")


def yt_dlp_cmd():
    """Localiza yt-dlp.

    El orden importa y el venv de AutoDownloader NO es un detalle: es el único
    yt-dlp que existe en este equipo. Sin esa rama, cada ejecución diaria
    reportaba «yt-dlp no está instalado» y la clase se quedaba sin subtítulos
    aunque el binario estuviera a un `os.path.isfile` de distancia. Se
    mantiene la misma lista de rutas que `frames_selectivos.py` para que los
    dos scripts no vuelvan a discrepar sobre si la herramienta está.

    `YTDLP_BIN` manda sobre todo lo demás: es la salida cuando la tarea corre
    en un entorno donde ninguna de estas rutas existe y se quiere apuntar a un
    binario concreto sin tocar el código.
    """
    for var in ("YTDLP_BIN", "YT_DLP_BIN"):
        override = os.environ.get(var)
        if override and os.path.isfile(override):
            return [override]
    p = shutil.which("yt-dlp")
    if p:
        return [p]
    root = os.path.expanduser("~")
    for cand in (
        # Dentro del proyecto primero: es lo único que sobrevive al sandbox.
        os.path.join(directorio_bin(), "yt-dlp.exe"),
        os.path.join(directorio_bin(), "yt-dlp"),
        os.path.join(root, "Documents", "AutoDownloader", ".venv", "Scripts", "yt-dlp.exe"),
        os.path.join(root, ".local", "bin", "yt-dlp"),
    ):
        if os.path.isfile(cand):
            return [cand]
    # Fallback: el módulo de Python (python3 -m yt_dlp).
    try:
        probe = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=30,
        )
        if probe.returncode == 0:
            return [sys.executable, "-m", "yt_dlp"]
    except Exception:
        pass
    return None


def download_bootcamp(video_id):
    """Descarga subtítulos automáticos en español + info.json. Devuelve (ok, mensaje)."""
    exe = yt_dlp_cmd()
    if not exe:
        # El mensaje lleva la salida. El 2026-11-15 decía solo «no está
        # instalado» y eso no dice qué hacer: la herramienta se resolvió con
        # `pip install yt-dlp` el día 12 y con la ruta del venv el 15, y en
        # ambos casos hizo falta adivinar el comando.
        return False, (
            "yt-dlp no está instalado. Instálalo con "
            "`python -m pip install yt-dlp` (o define YTDLP_BIN con la ruta al "
            "binario) y repite la comprobación."
        )
    out_dir = os.path.join(BASE, "02_TRANSCRIPTS", "bootcamp")
    os.makedirs(out_dir, exist_ok=True)
    cmd = exe + [
        "--skip-download",
        "--write-auto-subs",
        "--sub-langs", "es-orig,es",
        "--sub-format", "vtt",
        "--write-info-json",
        "--extractor-args", "youtube:lang=es",
        "-o", "%(upload_date)s_%(id)s_%(title)s.%(ext)s",
        "-P", out_dir,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except Exception as exc:
        return False, f"Error ejecutando yt-dlp: {exc}"
    # yt-dlp puede devolver error por una de las dos variantes (p. ej. 429 en "es")
    # aunque la otra se haya descargado. Se comprueba el resultado real en disco.
    got = glob.glob(os.path.join(out_dir, f"*{video_id}*.vtt"))
    if got:
        note = "Subtítulos e info.json descargados."
        if proc.returncode != 0:
            note += " Una variante de subtítulo falló, pero hay VTT válido en disco."
        return True, note
    if proc.returncode != 0:
        return False, f"yt-dlp falló: {proc.stderr.strip()[:400]}"
    return True, "Subtítulos e info.json descargados."


def run_processing():
    """Reconstruye transcripciones limpias y reindexa la base."""
    results = []
    for script in ("build_transcripts.py", "init_db.py"):
        path = os.path.join(BASE, "09_AUTOMATION", script)
        if not os.path.exists(path):
            results.append(f"{script}: no encontrado")
            continue
        # `encoding="utf-8"` explícito: los scripts imprimen acentos («Índice
        # de búsqueda»), y sin fijarlo en Windows se decodificaba con la
        # página de códigos de la consola y llegaba roto al reporte.
        proc = subprocess.run(
            [sys.executable, path], capture_output=True, text=True,
            timeout=600, encoding="utf-8", errors="replace",
        )
        if proc.returncode == 0:
            results.append(f"{script}: OK")
        else:
            # El detalle útil puede venir por stdout: `init_db.py` avisa de un
            # FTS roto con un `print`, no con una excepción, y sin esta rama
            # el reporte diario decía «ERROR —» y nada más.
            detalle = (proc.stderr.strip() or proc.stdout.strip() or "sin salida")
            results.append(f"{script}: ERROR — {detalle[-400:]}")
    return results


def write_log(lines):
    path = os.path.join(LOG_DIR, f"sync_{now().strftime('%Y-%m-%d')}.log")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_report(new_entries, feed_entries, status, download_notes, process_notes, source="RSS oficial"):
    date_str = now().strftime("%Y-%m-%d")
    path = os.path.join(REPORT_DIR, f"{date_str}.md")
    stamp = now().strftime("%H:%M:%S")
    lines = [
        f"## Comprobación {stamp}",
        "",
        f"- **Canal:** {CHANNEL_NAME} (`{CHANNEL_ID}`)",
        f"- **Fuente:** {source}",
        f"- **Entradas en el feed:** {len(feed_entries)}",
        f"- **Vídeos nuevos:** {len(new_entries)}",
        f"- **Estado:** {status}",
    ]
    if feed_entries:
        latest = feed_entries[0]
        # Sin fecha —el respaldo `--flat-playlist` no la trae— se imprime solo
        # el título. Antes salía «Bootcamp Día 21: Daily bias + DOL ()», que
        # parece un dato y es un hueco.
        fecha = (latest.get("published") or "")[:10]
        cuando = f" ({fecha})" if fecha else " (fecha no disponible)"
        lines.append(f"- **Última publicación del feed:** {latest['title']}{cuando}")
    if new_entries:
        lines.append("")
        lines.append("### Nuevos detectados")
        lines.append("")
        for e in new_entries:
            tag = "BOOTCAMP" if is_bootcamp(e["title"]) else categorize(e["title"])
            fecha = (e.get("published") or "")[:10] or "fecha no disponible"
            lines.append(f"- `{e['id']}` — {e['title']} — {fecha} — {tag}")
            lines.append(f"  - {e['url']}")
    else:
        lines.append("")
        lines.append("Sin novedades. La comprobación queda registrada.")
    if download_notes:
        lines.append("")
        lines.append("### Descarga")
        for n in download_notes:
            lines.append(f"- {n}")
    if process_notes:
        lines.append("")
        lines.append("### Procesamiento")
        for n in process_notes:
            lines.append(f"- {n}")
    lines.append("")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def main():
    parser = argparse.ArgumentParser(description="Sincroniza el canal y el bootcamp de Xavi Ruyra.")
    parser.add_argument("--download", action="store_true", help="Descargar subtítulos del bootcamp nuevo.")
    parser.add_argument("--process", action="store_true", help="Reconstruir transcripciones e índice tras descargar.")
    args = parser.parse_args()

    ensure_dirs()
    stamp = now().isoformat(timespec="seconds")
    log_lines = [f"[{stamp}] Sincronización iniciada."]

    source = "RSS oficial"
    try:
        feed = fetch_rss()
    except Exception as exc:
        rss_error = f"{type(exc).__name__}: {exc}"
        log_lines.append(f"RSS no disponible ({rss_error}); se usa yt-dlp como respaldo.")
        try:
            feed = fetch_ytdlp_index()
            source = f"yt-dlp (RSS no disponible: {rss_error[:120]})"
            log_lines.append(f"Respaldo yt-dlp: {len(feed)} entradas.")
        except Exception as exc2:
            msg = f"ERROR al leer el feed: RSS {rss_error}; respaldo {type(exc2).__name__}: {exc2}"
            log_lines.append(msg)
            write_log(log_lines)
            write_report([], [], "ERROR de red", [], [], source="RSS + yt-dlp")
            print(msg)
            return 1

    con = connect()
    known = load_known_ids(con)
    new_entries = [e for e in feed if e["id"] not in known]

    # Si venimos del respaldo, faltan fecha/descripción: se piden solo a los nuevos.
    for e in new_entries:
        if not e.get("upload_date"):
            meta = fetch_video_meta(e["id"])
            if meta:
                e["title"] = meta.get("title") or e["title"]
                e["upload_date"] = meta.get("upload_date")
                e["description"] = meta.get("description") or ""
                e["view_count"] = meta.get("view_count") or e.get("view_count")
                e["published"] = meta.get("upload_date") or e.get("published") or ""
                log_lines.append(f"META {e['id']}: completada con yt-dlp")

    download_notes = []
    for e in new_entries:
        cat = categorize(e["title"])
        insert_video(con, e, cat)
        append_catalog(e, cat)
        log_lines.append(f"NUEVO: {e['id']} — {e['title']} — {cat}")
        if args.download and is_bootcamp(e["title"]):
            ok, msg = download_bootcamp(e["id"])
            download_notes.append(f"{e['id']}: {msg}")
            log_lines.append(f"DESCARGA {e['id']}: {msg}")

    process_notes = []
    if args.process and any(is_bootcamp(e["title"]) for e in new_entries):
        # Cerrar la conexión antes de llamar a init_db.py: si sigue abierta con
        # locking_mode=EXCLUSIVE, el subproceso no puede escribir y falla.
        con.commit()
        con.close()
        try:
            process_notes = run_processing()
        finally:
            con = connect()
        log_lines.extend(f"PROCESO: {n}" for n in process_notes)

    status = "sin novedades" if not new_entries else f"{len(new_entries)} vídeo(s) nuevo(s)"
    con.execute(
        "INSERT INTO sync_log(run_at, new_videos, status, notes) VALUES (?,?,?,?)",
        (stamp, len(new_entries), status, "; ".join(download_notes) if download_notes else None),
    )
    con.commit()

    report_path = write_report(new_entries, feed, status, download_notes, process_notes, source=source)
    log_lines.append(f"Resultado: {status}. Reporte: {report_path}")
    write_log(log_lines)

    print(f"[{stamp}] {status}")
    if new_entries:
        for e in new_entries:
            fecha = (e.get("published") or "")[:10] or "fecha no disponible"
            print(f"  NUEVO {e['id']} — {e['title']} — {fecha}")
    else:
        print("  Sin publicaciones nuevas. Comprobación registrada.")
    print(f"Reporte: {report_path}")

    con.close()
    # Salida distinta de 0 si algún paso falló de verdad.
    #
    # Antes siempre era 0. El 2026-11-15 `init_db.py` falló, el reporte lo
    # escribió como «ERROR», y el proceso terminó con éxito igual: la tarea
    # programada no podía distinguir «no había novedades» de «había novedades
    # y el procesamiento se rompió». Quien lea el código de salida —una tarea
    # programada, un `&&`— necesita que esa diferencia exista.
    fallos = [n for n in process_notes if "ERROR" in n or "AVISO FTS" in n]
    fallos += [n for n in download_notes if "no está instalado" in n or "falló" in n]
    if fallos:
        print("\nFallos:", " · ".join(fallos))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

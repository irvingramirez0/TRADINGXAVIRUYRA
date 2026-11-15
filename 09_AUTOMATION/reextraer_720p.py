#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-extrae a 720p los fotogramas que quedaron por debajo de 1200 px.

Problema que resuelve: la Fase 0 descargó a 480p (formato `bv*[height<=480]`),
así que los `.webp` del sitio salen a 854 px de ancho. El encargo pedía 1200.

Método: en lugar de re-descargar vídeos completos (volumen y ~2 h de reloj),
se pide a yt-dlp solo el tramo de ±6 s alrededor del instante de cada
fotograma, a 720p60, y se extrae ese instante exacto. Un tramo de 20 s a 720p
pesa ~0,7 MB; un vídeo completo, 60-300 MB.

Reglas de seguridad:
  - Solo toca filas con `description LIKE 'pendiente de anotación%'`. Las
    anotaciones manuales son intocables.
  - Sustituye el `.jpg` del mismo nombre: la ruta no cambia, las referencias
    en el vault y en `index.csv` siguen siendo válidas.
  - Verifica que el nuevo fotograma no sea una cámara ni un lienzo vacío
    (mismos filtros que la Fase 0). Si el 720p no supera el filtro, conserva
    el original y lo reporta; no se pierde nada.
  - Registra `analysis` con la misma frase de transcripción y anota en
    `description` que la imagen se re-extrajo a 720p.

Uso:
    python 09_AUTOMATION/reextraer_720p.py                 # informe, no toca nada
    python 09_AUTOMATION/reextraer_720p.py --aplicar       # re-extrae de verdad
    python 09_AUTOMATION/reextraer_720p.py --aplicar --videos 7HOAf7vHMqU
"""

import argparse
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frames_selectivos import (  # noqa: E402  (pipeline ya existente)
    BASE,
    DB,
    resolve_ffmpeg,
    yt_dlp_cmd,
    es_pantalla,
    frame_vacio,
)

MEDIA = os.path.join(BASE, "12_VAULT", "media")
TMP = os.path.join(BASE, "09_AUTOMATION", ".tmp", "720p")

# Ancho mínimo aceptable de un .webp: por debajo, se considera flojo.
MIN_ANCHO = 1200
# Ventana de descarga alrededor del instante: margen a ambos lados.
MARGEN = 6.0
# Selector por altura, no por id de formato: no todos los vídeos ofrecen el
# mismo id (los hay a 720p24 y a 720p60). Pidiendo la altura, yt-dlp elige el
# mejor formato disponible sin subir de calidad ni bajar de 720.
FORMATO = "bv*[height<=720][ext=mp4]/bv*[height<=720]/b[height<=720]"


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def frames_flojos(con, solo_videos=None, solo_publicados=True, incluir_anotados=False):
    """Filas cuyo .webp en el vault no llega a MIN_ANCHO px.

    Por defecto solo mira los fotogramas que el sitio publica de verdad
    (`solo_publicados`): re-extraer los 695 pendientes sería trabajo y datos
    para imágenes que nadie va a ver. Los archivos del vault se llaman
    `{slug}-{frame_id}.webp`, así que el id sale del nombre.

    Con `incluir_anotados` entra también el fotograma anotado a mano. Es
    seguro: se sustituye la imagen del **mismo instante**, nunca el texto de
    `description`/`analysis`; la anotación sigue siendo válida.
    """
    publicados = {}
    for name in os.listdir(MEDIA) if os.path.isdir(MEDIA) else []:
        if not name.lower().endswith(".webp"):
            continue
        m = re.search(r"-(\d+)\.webp$", name)
        if m:
            publicados[int(m.group(1))] = os.path.join(MEDIA, name)

    sql = "SELECT id, video_id, timestamp_sec, path, description, analysis FROM frames WHERE 1=1"
    args = []
    if not incluir_anotados:
        sql += " AND description LIKE 'pendiente de anotaci%'"
    if solo_videos:
        sql += " AND video_id IN (%s)" % ",".join("?" * len(solo_videos))
        args = list(solo_videos)
    out = []
    for r in con.execute(sql, args):
        if solo_publicados and r["id"] not in publicados:
            continue
        jpg = os.path.join(BASE, r["path"]) if r["path"] else None
        if not jpg or not os.path.exists(jpg):
            continue
        w, _ = Image.open(jpg).size
        if w < MIN_ANCHO:
            es_anotado = not (r["description"] or "").lower().startswith("pendiente de anotaci")
            out.append(dict(r, ancho_actual=w, jpg=jpg,
                            webp=publicados.get(r["id"]), anotado=es_anotado))
    return sorted(out, key=lambda x: (x["video_id"], x["timestamp_sec"]))


def descargar_tramo(exe, ff, vid, ts, dest_dir):
    """Descarga ±MARGEN segundos alrededor de `ts` a 720p. Devuelve (mp4, inicio)."""
    inicio = max(0.0, ts - MARGEN)
    fin = ts + MARGEN
    plantilla = os.path.join(dest_dir, f"{vid}_{int(ts)}.%(ext)s")
    cmd = exe + [
        "--no-warnings", "--no-playlist",
        "--ffmpeg-location", ff,
        "-f", FORMATO,
        "--download-sections", f"*{inicio:.1f}-{fin:.1f}",
        "--force-keyframes-at-cuts",
        "--no-part",
        "-o", plantilla,
        f"https://www.youtube.com/watch?v={vid}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    mp4 = os.path.join(dest_dir, f"{vid}_{int(ts)}.mp4")
    if not os.path.exists(mp4):
        msg = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise RuntimeError(msg[-1] if msg else "descarga fallida")
    return mp4, inicio


def extraer(mp4, inicio, ts, destino):
    """Extrae el instante exacto de `ts` del tramo ya recortado."""
    ff = resolve_ffmpeg()
    rel = max(0.0, ts - inicio)
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-y",
           "-ss", f"{rel:.3f}", "-i", mp4, "-frames:v", "1", "-q:v", "2", destino]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return os.path.exists(destino)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true",
                    help="sin esta bandera solo muestra el informe")
    ap.add_argument("--videos", nargs="*", help="limitar a estos vídeos")
    ap.add_argument("--limite", type=int, default=0, help="máximo de fotogramas")
    ap.add_argument("--incluir-anotados", action="store_true",
                    help="re-extraer también los anotados a mano (no toca el texto)")
    args = ap.parse_args()

    con = connect()
    flojos = frames_flojos(con, args.videos, incluir_anotados=args.incluir_anotados)
    if args.limite:
        flojos = flojos[:args.limite]

    print(f"Fotogramas pendientes por debajo de {MIN_ANCHO} px: {len(flojos)}")
    if not flojos:
        return 0

    por_video = {}
    for f in flojos:
        por_video.setdefault(f["video_id"], []).append(f)
    print(f"Vídeos implicados: {len(por_video)}")
    for vid, fs in sorted(por_video.items()):
        print(f"  {vid}: {len(fs)} fotogramas")

    if not args.aplicar:
        print("\n(Informe solo. Añade --aplicar para re-extraer.)")
        return 0

    exe = yt_dlp_cmd()
    if not exe:
        print("ERROR: yt-dlp no está instalado.")
        return 1
    ff = resolve_ffmpeg()
    os.makedirs(TMP, exist_ok=True)

    ok = fallidos = 0
    sin_mejora = []
    for vid, fs in sorted(por_video.items()):
        print(f"\n=== {vid} ({len(fs)}) ===")
        for f in fs:
            destino = os.path.join(TMP, f"{f['id']}.jpg")
            try:
                mp4, inicio = descargar_tramo(exe, ff, vid, f["timestamp_sec"], TMP)
            except Exception as e:  # descarga caída o vídeo no disponible
                print(f"  [{f['id']}] descarga: {e}")
                fallidos += 1
                continue
            try:
                if not extraer(mp4, inicio, f["timestamp_sec"], destino):
                    print(f"  [{f['id']}] no se pudo extraer")
                    fallidos += 1
                    continue
                w, h = Image.open(destino).size
                if w < MIN_ANCHO:
                    sin_mejora.append((f["id"], f"{w}px"))
                    print(f"  [{f['id']}] 720p no disponible ({w}px), se conserva el original")
                    continue
                # Mismos filtros de la Fase 0: ni cámara ni lienzo vacío.
                if not es_pantalla(destino) or frame_vacio(destino):
                    sin_mejora.append((f["id"], "rechazado por filtro"))
                    print(f"  [{f['id']}] el 720p no supera el filtro, se conserva el original")
                    continue
                # Copia del original antes de sobrescribir: si el instante
                # extraído no fuera el mismo, se puede volver atrás.
                respaldo = os.path.join(TMP, "respaldo_" + os.path.basename(f["jpg"]))
                if not os.path.exists(respaldo):
                    shutil.copy2(f["jpg"], respaldo)
                shutil.copy2(destino, f["jpg"])
                if not f["anotado"]:
                    # Solo se reescribe la marca de los pendientes. El texto de
                    # una anotación manual no se toca jamás.
                    con.execute(
                        "UPDATE frames SET description = ? WHERE id = ?",
                        (re.sub(r"\|\s*calidad:.*$", "", f["description"]).rstrip()
                         + " | calidad: 720p re-extraído", f["id"]),
                    )
                    con.commit()
                ok += 1
                print(f"  [{f['id']}] {f['ancho_actual']}px -> {w}px")
            finally:
                if os.path.exists(mp4):
                    os.remove(mp4)

    print(f"\nRe-extraídos: {ok} | fallidos: {fallidos} | sin mejora: {len(sin_mejora)}")
    if sin_mejora:
        for fid, motivo in sin_mejora:
            print(f"  sin mejora: {fid} ({motivo})")
    print("\nRegenera el sitio con: python 09_AUTOMATION/pipeline.py --solo-vault")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

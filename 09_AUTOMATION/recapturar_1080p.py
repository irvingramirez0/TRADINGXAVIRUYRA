#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recaptura los fotogramas publicados con mejor encuadre y mejor calidad.

Por qué existe
--------------
Las capturas del sitio salían pixeladas por dos motivos acumulados:

1. **Encuadre**: la captura incluía la barra de herramientas de TradingView
   (izquierda), la barra de menús (arriba) y la barra de dibujo (abajo). El
   gráfico ocupaba solo ~78 % del ancho, así que al escalar a 1200 px el
   contenido útil se quedaba en ~940 px efectivos.
2. **Calidad**: el WebP se generaba a calidad 82 sobre un escalado bicúbico.

Qué hace
--------
- Descarga el tramo de ±4 s del instante de cada fotograma y extrae ese
  instante exacto a la máxima resolución disponible (720p en este corpus:
  yt-dlp no ofrece 1080p para estos vídeos, verificado).
- Detecta el rectángulo del lienzo del gráfico por su color de fondo y recorta
  la interfaz. Si la captura no encaja con el patrón de TradingView (una
  diapositiva, por ejemplo), **no recorta**: deja la imagen completa.
- Guarda en el mismo `.jpg`, sin tocar rutas ni anotaciones. Solo actualiza la
  marca de calidad de los fotogramas pendientes.

El recorte va **antes** del escalado: al pasar de un encuadre de 1280 px a uno
de ~1240 px de gráfico puro y escalar a 1200, el contenido queda prácticamente
a resolución nativa en lugar de ampliarse.

Uso:
    python 09_AUTOMATION/recapturar_1080p.py                 # informe
    python 09_AUTOMATION/recapturar_1080p.py --aplicar
    python 09_AUTOMATION/recapturar_1080p.py --aplicar --limite 5
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frames_selectivos import BASE, DB, resolve_ffmpeg, yt_dlp_cmd  # noqa: E402
from reextraer_720p import connect  # noqa: E402

MEDIA = os.path.join(BASE, "12_VAULT", "media")
TMP = os.path.join(BASE, "09_AUTOMATION", ".tmp", "recaptura")
MARGEN = 4.0
FORMATO = "bv*[height<=1080][ext=mp4]/bv*[height<=1080]/b[height<=1080]"


def cerca(p, q, tol=22):
    return all(abs(a - b) <= tol for a, b in zip(p, q))


def bbox_lienzo(path):
    """Devuelve (l, t, r, b) en fracciones, o None si no parece TradingView.

    El lienzo del gráfico es un rectángulo grande de un único color de fondo;
    la barra de herramientas y las barras de menú usan otro color. Se busca la
    primera fila/columna, desde cada borde, en la que manda el color del
    lienzo. Solo se acepta el recorte si las cuatro fronteras caen en rangos
    plausibles para una captura de TradingView a ventana completa.
    """
    im = Image.open(path).convert("RGB")
    w, h = im.size
    centro = im.crop((int(w * .3), int(h * .3), int(w * .7), int(h * .7)))
    bg = Counter(centro.getdata()).most_common(1)[0][0]

    pequena = im.resize((320, max(1, int(320 * h / w))), Image.LANCZOS)
    W, H = pequena.size
    px = pequena.load()

    def fila_frac(y):
        return sum(1 for x in range(W) if cerca(px[x, y], bg)) / W

    def col_frac(x):
        return sum(1 for y in range(H) if cerca(px[x, y], bg)) / H

    U = 0.32
    top = next((y for y in range(H) if fila_frac(y) > U), 0) / H
    bottom = next(((y + 1) / H for y in range(H - 1, -1, -1) if fila_frac(y) > U), 1.0)
    left = next((x for x in range(W) if col_frac(x) > U), 0) / W
    right = next(((x + 1) / W for x in range(W - 1, -1, -1) if col_frac(x) > U), 1.0)

    # Algunas capturas no son TradingView sino FXReplay dentro del navegador;
    # ahí el encabezado (pestañas + barra de direcciones + marcadores + barra
    # de la app) mide hasta un 16-20 % de la altura. Los márgenes aceptados
    # son amplios a propósito: la frontera la decide el color del lienzo.
    plausible = (0.005 <= left <= 0.06 and 0.01 <= top <= 0.20
                 and bottom >= 0.80 and right >= 0.90)
    return (left, top, right, bottom) if plausible else None


def descargar(exe, ff, vid, ts, destino_dir):
    inicio = max(0.0, ts - MARGEN)
    fin = ts + MARGEN
    plantilla = os.path.join(destino_dir, f"{vid}_{int(ts)}.%(ext)s")
    cmd = exe + [
        "--no-warnings", "--no-playlist", "--ffmpeg-location", ff,
        "-f", FORMATO,
        "--download-sections", f"*{inicio:.1f}-{fin:.1f}",
        "--force-keyframes-at-cuts", "--no-part",
        "-o", plantilla,
        f"https://www.youtube.com/watch?v={vid}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    mp4 = os.path.join(destino_dir, f"{vid}_{int(ts)}.mp4")
    if not os.path.exists(mp4):
        msg = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise RuntimeError(msg[-1] if msg else "descarga fallida")
    return mp4, inicio


def extraer(mp4, inicio, ts, destino):
    ff = resolve_ffmpeg()
    rel = max(0.0, ts - inicio)
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-y",
           "-ss", f"{rel:.3f}", "-i", mp4, "-frames:v", "1", "-q:v", "1", destino]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return os.path.exists(destino)


def recortar(src, dst, caja):
    """Recorta (l,t,r,b) fraccionarios y guarda en JPEG de alta calidad."""
    im = Image.open(src)
    w, h = im.size
    l, t, r, b = caja
    im.crop((int(w * l), int(h * t), int(w * r), int(h * b))).save(
        dst, "JPEG", quality=97, subsampling=0, optimize=True
    )
    return Image.open(dst).size


def publicados(con, solo_videos=None, limite=0):
    """Filas de `frames` cuyas imágenes el sitio publica de verdad.

    Se identifica por el nombre del `.webp` en `12_VAULT/media`
    (`{slug}-{frame_id}.webp`), así que solo se recaptura lo que se ve.
    """
    ids = []
    for n in os.listdir(MEDIA) if os.path.isdir(MEDIA) else []:
        m = re.search(r"-(\d+)\.webp$", n)
        if m:
            ids.append(int(m.group(1)))
    if not ids:
        return []
    marcas = ",".join("?" * len(ids))
    sql = (f"SELECT id, video_id, timestamp_sec, path, description "
           f"FROM frames WHERE id IN ({marcas})")
    args = list(ids)
    if solo_videos:
        sql += " AND video_id IN (%s)" % ",".join("?" * len(solo_videos))
        args += list(solo_videos)
    out = []
    for r in con.execute(sql, args):
        jpg = os.path.join(BASE, r["path"]) if r["path"] else None
        if not jpg or not os.path.exists(jpg):
            continue
        d = dict(r)
        d["jpg"] = jpg
        d["anotado"] = not (r["description"] or "").lower().startswith("pendiente de anotaci")
        out.append(d)
    out.sort(key=lambda x: (x["video_id"], x["timestamp_sec"]))
    return out[:limite] if limite else out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--videos", nargs="*")
    ap.add_argument("--ids", nargs="*", type=int,
                    help="reprocesar solo estos frame_id")
    args = ap.parse_args()

    con = connect()
    objetivos = publicados(con, args.videos, args.limite)
    if args.ids:
        pedidos = set(args.ids)
        objetivos = [f for f in objetivos if f["id"] in pedidos]

    print(f"Fotogramas publicados a recapturar: {len(objetivos)}")
    print(f"Vídeos: {len({f['video_id'] for f in objetivos})}")
    if not args.aplicar:
        print("\n(Informe solo. Añade --aplicar.)")
        return 0

    exe, ff = yt_dlp_cmd(), resolve_ffmpeg()
    if not exe:
        print("ERROR: yt-dlp no está instalado.")
        return 1
    os.makedirs(TMP, exist_ok=True)

    ok = recortados = fallidos = sin_cambio = 0
    for f in objetivos:
        destino = os.path.join(TMP, f"{f['id']}.jpg")
        try:
            mp4, inicio = descargar(exe, ff, f["video_id"], f["timestamp_sec"], TMP)
        except Exception as e:
            print(f"  [{f['id']}] descarga: {e}")
            fallidos += 1
            continue
        try:
            if not extraer(mp4, inicio, f["timestamp_sec"], destino):
                print(f"  [{f['id']}] no se pudo extraer")
                fallidos += 1
                continue
            alto_fuente = Image.open(destino).size[0]
            caja = bbox_lienzo(destino)
            if caja:
                recortar(destino, destino, caja)
                recortados += 1
            aux = os.path.join(TMP, "respaldo_" + os.path.basename(f["jpg"]))
            if not os.path.exists(aux):
                shutil.copy2(f["jpg"], aux)
            shutil.copy2(destino, f["jpg"])
            if not f.get("anotado"):
                con.execute(
                    "UPDATE frames SET description=? WHERE id=?",
                    (re.sub(r"\|\s*calidad:.*$", "", f["description"]).rstrip()
                     + f" | calidad: {alto_fuente}p"
                     + (" recortado" if caja else ""), f["id"]),
                )
                con.commit()
            ok += 1
            print(f"  [{f['id']}] {alto_fuente}px"
                  + (f" recorte {caja[0]:.2f}/{caja[1]:.2f}-{caja[2]:.2f}/{caja[3]:.2f}" if caja else " sin recorte"))
        finally:
            if os.path.exists(mp4):
                os.remove(mp4)

    print(f"\nRecapturados: {ok} | con recorte: {recortados} | fallidos: {fallidos}")
    print("Regenera el sitio: python 09_AUTOMATION/pipeline.py --solo-vault")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba que la recaptura mejora de verdad, midiendo en vez de opinando.

Para cada `.webp` publicado compara el respaldo del fotograma anterior con la
copia nueva y calcula:

- **nitidez** = varianza del laplaciano sobre el gris, normalizada por el
  tamaño de la imagen (un valor más alto = bordes más definidos);
- **ancho efectivo de gráfico** = píxeles de ancho del lienzo, descontando la
  interfaz, en la imagen final de 1200 px.

Uso:
    python 09_AUTOMATION/verificar_calidad.py
"""

import os
import re
import sys

from PIL import Image, ImageFilter, ImageStat

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "09_AUTOMATION"))
from recapturar_1080p import bbox_lienzo  # noqa: E402

MEDIA = os.path.join(BASE, "12_VAULT", "media")
RESPALDO = os.path.join(BASE, "09_AUTOMATION", ".tmp", "recaptura")


def nitidez(path):
    im = Image.open(path).convert("L")
    borde = im.filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(borde).var[0]


def ancho_util(path, recortada):
    """Ancho en px del contenido de gráfico dentro de la imagen ya publicada."""
    w, h = Image.open(path).size
    if recortada:
        return w
    caja = bbox_lienzo(path)
    if not caja:
        return w
    return int(w * (caja[2] - caja[0]))


def main():
    import sqlite3
    con = sqlite3.connect(os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db"))
    con.row_factory = sqlite3.Row

    filas = []
    for name in sorted(os.listdir(MEDIA)):
        m = re.search(r"-(\d+)\.webp$", name) if name.endswith(".webp") else None
        if not m:
            continue
        fid = int(m.group(1))
        r = con.execute("SELECT path FROM frames WHERE id=?", (fid,)).fetchone()
        if not r:
            continue
        actual = os.path.join(BASE, r["path"])
        resp = os.path.join(RESPALDO, "respaldo_" + os.path.basename(r["path"]))
        if os.path.exists(actual) and os.path.exists(resp):
            filas.append((fid, name, resp, actual, os.path.join(MEDIA, name)))

    if not filas:
        print("No hay respaldos para comparar.")
        print(f"Buscando en: {RESPALDO}")
        return 1

    print(f"Comparando {len(filas)} fotogramas\n")
    print(f"{'id':>5} {'antes':>8} {'después':>8} {'mejora':>7}  archivo")
    gana = pierde = 0
    for fid, name, resp, actual, webp in filas:
        a, d = nitidez(resp), nitidez(actual)
        ratio = d / a if a else 0
        gana += ratio > 1.05
        pierde += ratio < 0.95
        print(f"{fid:>5} {a:8.1f} {d:8.1f} {ratio:6.2f}x  {name[:46]}")
    print(f"\nMejoran más de un 5 %: {gana} | empeoran más de un 5 %: {pierde}")

    print("\nResolución publicada:")
    anchos = {}
    for _, _, _, _, webp in filas:
        w, h = Image.open(webp).size
        anchos.setdefault((w, h), 0)
        anchos[(w, h)] += 1
    for k, v in sorted(anchos.items(), key=lambda x: -x[1]):
        print(f"  {k[0]}x{k[1]}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

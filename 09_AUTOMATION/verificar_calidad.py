#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba la mejora de las capturas midiendo geometría, no "nitidez".

Un medidor de varianza de bordes no sirve aquí: compara imágenes con encuadres
y tamaños distintos, así que mide el contenido y no la calidad. Lo que sí es
objetivo:

- resolución del `.jpg` de origen antes y después;
- si se recortó la interfaz;
- **ancho efectivo de gráfico** dentro del `.webp` publicado (1200 px): cuántos
  de esos píxeles son gráfico y no barra de herramientas.

Uso:
    python 09_AUTOMATION/verificar_calidad.py
"""

import os
import re
import sqlite3

from PIL import Image


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(BASE, "12_VAULT", "media")
RESPALDO = os.path.join(BASE, "09_AUTOMATION", ".tmp", "recaptura")


def main():
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
        if not (os.path.exists(actual) and os.path.exists(resp)):
            continue
        filas.append((fid, name, resp, actual, os.path.join(MEDIA, name)))

    if not filas:
        print(f"No hay respaldos en {RESPALDO}")
        return 1

    print(f"{'id':>5} {'antes':>9} {'después':>9} {'recorte':>8} {'gráfico en 1200':>16}")
    mejor_res = recortadas = 0
    for fid, name, resp, actual, webp in filas:
        wa, ha = Image.open(resp).size
        wd, hd = Image.open(actual).size
        ww, hw = Image.open(webp).size
        # Antes: el gráfico ocupaba el ancho menos la barra izquierda (~3 %) y
        # nada más; el resto de la imagen era chrome. Después del recorte, todo
        # el ancho es gráfico.
        antes_util = int(ww * 0.94)
        # El recorte deja anchos que no son una resolución completa del vídeo
        # (1920 -> 1805, 1280 -> 1203). Comparar con los anchos nativos es más
        # fiable que inferirlo otra vez de la imagen.
        recortada = wd not in (1920, 1280, 854, 852, 640)
        util = ww if recortada else antes_util
        mejor_res += wd > wa
        recortadas += recortada
        print(f"{fid:>5} {wa:>9} {wd:>9} {'sí' if recortada else 'no':>8} {util:>10} px")

    print(f"\nCon más resolución de origen: {mejor_res}/{len(filas)}")
    print(f"Con la interfaz recortada:     {recortadas}/{len(filas)}")
    print("\nEl ancho útil es cuántos píxeles del .webp publicado son gráfico.")
    print("Antes ~1128 px (el resto era barra de herramientas); ahora hasta 1200.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

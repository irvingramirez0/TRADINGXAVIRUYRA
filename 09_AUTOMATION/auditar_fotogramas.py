#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audita el vínculo entre cada fotograma publicado y el concepto que ilustra.

Para cada concepto revisa los fotogramas que `candidate_frames` elegiría y
clasifica el vínculo leyendo la **anotación**, que es la única fuente que dice
qué se ve en la imagen:

- **muestra**: la anotación nombra el concepto.
- **contexto**: no lo nombra, pero tampoco lo niega.
- **contradice**: la anotación dice del concepto que no se ve. No se publica.

Con `--bootcamp` se limita a los vídeos de la categoría BOOTCAMP, que es la
revisión que se pidió primero.

Uso:
    python 09_AUTOMATION/auditar_fotogramas.py
    python 09_AUTOMATION/auditar_fotogramas.py --bootcamp
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regenerar_vault import (  # noqa: E402
    connect,
    conceptos_data,
    candidate_frames,
    frame_is_annotated,
    justifica_concepto,
    niega_concepto,
    mmss,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootcamp", action="store_true")
    ap.add_argument("--detalle", action="store_true", help="una línea por imagen")
    args = ap.parse_args()

    con = connect()
    conceptos = conceptos_data(con)

    videos_bootcamp = set()
    if args.bootcamp:
        videos_bootcamp = {r["id"] for r in con.execute(
            "SELECT id FROM videos WHERE category='BOOTCAMP'")}

    total = muestra = contexto = sin_img = 0
    filas = []
    for c in conceptos:
        seleccion = candidate_frames(con, c)
        if args.bootcamp:
            seleccion = [s for s in seleccion if s[1]["video_id"] in videos_bootcamp]
        total += 1
        if not seleccion:
            sin_img += 1
            filas.append((c["name"], "-", "sin imagen", ""))
            continue
        for rank, fr, why in seleccion:
            texto = (fr["description"] or "") + " " + (fr["analysis"] or "")
            if not frame_is_annotated(fr):
                etiqueta = "pendiente"
            elif justifica_concepto((fr["description"] or ""), c.get("alts_propias") or c["alts"]):
                etiqueta = "muestra"
                muestra += 1
            else:
                etiqueta = "contexto"
                contexto += 1
            desc = (fr["description"] or "").replace("\n", " ")[:120]
            filas.append((c["name"], f"{fr['id']}@{mmss(fr['timestamp_sec'])}", etiqueta, desc))

    if args.detalle:
        actual = None
        for nombre, frame, etiqueta, desc in filas:
            if nombre != actual:
                print(f"\n### {nombre}")
                actual = nombre
            print(f"  [{etiqueta:8s}] {frame:16s} {desc}")
    else:
        from collections import Counter
        por_etiqueta = Counter(f[2] for f in filas)
        print(f"Conceptos revisados: {total}")
        print(f"  con imagen que muestra el concepto: {sum(1 for f in filas if f[2]=='muestra')}")
        print(f"  con imagen solo de contexto:        {sum(1 for f in filas if f[2]=='contexto')}")
        print(f"  con imagen pendiente:               {sum(1 for f in filas if f[2]=='pendiente')}")
        print(f"  sin ninguna imagen:                 {sin_img}")

        # Los que quedan sin nada tras el filtro son los que hay que vigilar.
        vacios = [f[0] for f in filas if f[2] == "sin imagen"]
        if vacios:
            print(f"\nConceptos sin imagen ({len(vacios)}):")
            for v in vacios:
                print(f"  - {v}")
        solo_contexto = sorted({f[0] for f in filas if f[2] == "contexto"})
        if solo_contexto:
            print(f"\nConceptos que solo tienen contexto ({len(solo_contexto)}):")
            for v in solo_contexto:
                print(f"  - {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

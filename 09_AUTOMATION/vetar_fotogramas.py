#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veta un fotograma **para un concepto concreto**, tras una revisión visual.

Por qué es por concepto y no por fotograma
------------------------------------------
Un mismo fotograma puede ilustrar legítimamente dos conceptos (una diapositiva
de Judas Swing sirve para Judas Swing y para el Open de las 10) y, a la vez, no
servir para un tercero que lo tomó prestado por una coincidencia de palabras.
Vetar la imagen entera tiraría la evidencia buena; vetarla para el concepto que
no corresponde deja el resto intacto.

Cómo se guarda
--------------
Tabla `frame_vetos(frame_id, concept_id, motivo, fecha, entity_type)`. El generador la
consulta en `candidate_frames`, así que el veto sobrevive a cualquier
regeneración del vault. `concept_id` nulo significa «esta imagen no sirve para
nada» (gráfico vacío, captura rota).

Uso
---
    python 09_AUTOMATION/vetar_fotogramas.py --listar
    python 09_AUTOMATION/vetar_fotogramas.py --frame 382 --concepto "PO3 (Power of 3)" --motivo "es un esquema de Judas Swing"
    python 09_AUTOMATION/vetar_fotogramas.py --veredictos veredictos.json
    python 09_AUTOMATION/vetar_fotogramas.py --quitar --frame 382 --concepto "PO3 (Power of 3)"

El JSON de veredictos es la lista que descarga `revisar_capturas.py`: cada
objeto trae `webp`, `veredicto` y opcionalmente `concepto` y `motivo`. Solo se
aplican los `descartar`.
"""

import argparse
import json
import os
import re
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")


def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute(
        """CREATE TABLE IF NOT EXISTS frame_vetos (
               frame_id   INTEGER NOT NULL,
               concept_id INTEGER,
               motivo     TEXT,
               fecha      TEXT DEFAULT CURRENT_TIMESTAMP,
               entity_type TEXT NOT NULL DEFAULT 'concept',
               PRIMARY KEY (frame_id, concept_id, entity_type)
           )"""
    )
    # Migración idempotente: los vetos anteriores son todos de concepto.
    columnas = {r[1] for r in con.execute("PRAGMA table_info(frame_vetos)")}
    if "entity_type" not in columnas:
        con.execute(
            "ALTER TABLE frame_vetos ADD COLUMN entity_type TEXT NOT NULL DEFAULT 'concept'"
        )
    con.commit()
    return con


def id_de_webp(nombre):
    m = re.search(r"-(\d+)\.webp$", nombre)
    return int(m.group(1)) if m else None


def id_concepto(con, nombre):
    if not nombre:
        return None
    r = con.execute(
        "SELECT id FROM concepts WHERE lower(name)=lower(?)", (nombre.strip(),)
    ).fetchone()
    return r["id"] if r else None


def vetar(con, fid, cid, motivo, aplicar=True):
    r = con.execute("SELECT 1 FROM frames WHERE id=?", (fid,)).fetchone()
    if not r:
        print(f"  [{fid}] no existe")
        return False
    ya = con.execute(
        "SELECT 1 FROM frame_vetos WHERE frame_id=? AND "
        + ("concept_id IS ?" if cid is None else "concept_id=?"),
        (fid, cid),
    ).fetchone()
    if ya:
        print(f"  [{fid}] ya vetado para ese concepto")
        return False
    if aplicar:
        con.execute(
            "INSERT OR REPLACE INTO frame_vetos (frame_id, concept_id, motivo) VALUES (?,?,?)",
            (fid, cid, " ".join((motivo or "").split())[:200]),
        )
        con.commit()
    etiqueta = "todos los conceptos" if cid is None else f"concepto #{cid}"
    print(f"  [{fid}] vetado para {etiqueta} — {(motivo or '')[:70]}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--veredictos", nargs="*", default=[])
    ap.add_argument("--frame", type=int, nargs="*", default=[])
    ap.add_argument("--concepto", default="",
                    help="nombre exacto del concepto; vacío = todos")
    ap.add_argument("--motivo", default="revisión visual: no muestra el concepto")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--quitar", action="store_true")
    ap.add_argument(
        "--anotar", nargs="*", default=[],
        help="JSON de la hoja de tanda: escribe la descripción de los fotogramas "
             "pendientes y veta los que no sirven.",
    )
    args = ap.parse_args()

    con = conectar()

    if args.listar:
        filas = con.execute(
            "SELECT v.frame_id, v.concept_id, v.motivo, v.fecha, c.name "
            "FROM frame_vetos v LEFT JOIN concepts c ON c.id=v.concept_id "
            "ORDER BY v.frame_id"
        ).fetchall()
        print(f"Vetos registrados: {len(filas)}")
        for r in filas:
            quien = r["name"] or "todos los conceptos"
            print(f"  [{r['frame_id']:>4}] → {quien:<34} {r['motivo'][:70]}")
        return 0

    if args.quitar:
        cid = id_concepto(con, args.concepto)
        for fid in args.frame:
            if cid is None:
                con.execute("DELETE FROM frame_vetos WHERE frame_id=?", (fid,))
            else:
                con.execute(
                    "DELETE FROM frame_vetos WHERE frame_id=? AND concept_id=?", (fid, cid)
                )
            print(f"  [{fid}] veto retirado")
        con.commit()
        return 0

    cambios = 0
    cid = id_concepto(con, args.concepto) if args.concepto else None
    if args.concepto and cid is None:
        print(f"AVISO: no existe el concepto {args.concepto!r}; se veta para todos.")

    for arch in args.veredictos:
        with open(arch, encoding="utf-8") as fh:
            datos = json.load(fh)
        if isinstance(datos, dict):
            datos = datos.get("veredictos") or []
        print(f"{arch}: {len(datos)} veredictos")
        for v in datos:
            if v.get("veredicto") != "descartar":
                continue
            fid = id_de_webp(v.get("webp") or "")
            if fid is None:
                continue
            c = id_concepto(con, v.get("concepto") or args.concepto)
            cambios += vetar(con, fid, c, v.get("motivo") or args.motivo)

    for fid in args.frame:
        cambios += vetar(con, fid, cid, args.motivo)

    # Anotación de fotogramas pendientes, escrita a mano en la hoja de tanda.
    #
    # Esto NO inventa nada: escribe exactamente el texto que una persona
    # tecleó al mirar la imagen. Es el paso que convierte un fotograma
    # «pendiente de anotación» en evidencia citable, y hasta ahora solo se
    # podía hacer con SQL a mano.
    anotados = 0
    vetados_por_tanda = 0
    for arch in args.anotar:
        with open(arch, encoding="utf-8") as fh:
            entradas = json.load(fh)
        if isinstance(entradas, dict):
            entradas = entradas.get("anotaciones") or []
        print(f"{arch}: {len(entradas)} entradas")
        for e in entradas:
            fid = e.get("frame")
            if fid is None:
                continue
            fid = int(fid)
            veredicto = (e.get("veredicto") or "").lower()
            desc = (e.get("descripcion") or "").strip()
            if veredicto == "descartar" or (veredicto == "no sirve"):
                c = id_concepto(con, e.get("concepto") or args.concepto)
                vetados_por_tanda += vetar(
                    con, fid, c, "revisión visual: no muestra el concepto"
                )
                continue
            if not desc:
                # Sin texto no hay nada que guardar. Se avisa en vez de
                # dejar el fotograma como estaba silenciosamente.
                print(f"  [{fid}] sin descripción: no se anota")
                continue
            con.execute(
                "UPDATE frames SET description=? WHERE id=?", (desc, fid)
            )
            anotados += 1

    con.commit()
    print(f"\nVetos nuevos: {cambios + vetados_por_tanda}")
    print(f"Fotogramas anotados: {anotados}")
    print("Regenera el sitio: python 09_AUTOMATION/pipeline.py --solo-vault")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

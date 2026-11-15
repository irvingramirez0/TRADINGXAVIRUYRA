#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecuta el proyecto de punta a punta:

  1. Marca los vídeos caídos (no_disponible).
  2. Extrae fotogramas selectivos de los vídeos pendientes, por prioridad.
  3. Limpia fotogramas que en realidad son cámara hablando.
  4. Regenera el índice de búsqueda de fotogramas.
  5. Regenera el vault desde SQLite.
  6. Verifica el vault.
  7. Genera el informe de cobertura.

Uso:
    python 09_AUTOMATION/pipeline.py                 # todo
    python 09_AUTOMATION/pipeline.py --solo-vault    # sin extraer fotogramas
    python 09_AUTOMATION/pipeline.py --lote 10       # solo 10 vídeos nuevos
"""

import argparse
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = [sys.executable, "-I"]


def run(script, *args, timeout=None):
    path = os.path.join(BASE, "09_AUTOMATION", script)
    cmd = PY + [path] + list(args)
    print(f"\n=== {script} {' '.join(args)} ===")
    proc = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True,
                          timeout=timeout, encoding="utf-8", errors="replace")
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if out:
        print(out)
    if proc.returncode != 0:
        print("FALLO:", err[-1500:] or "(sin salida)")
    return proc.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-vault", action="store_true", help="No extraer fotogramas")
    ap.add_argument("--lote", type=int, default=None, help="Nº de vídeos nuevos a extraer")
    args = ap.parse_args()

    fallos = []

    if not args.solo_vault:
        if run("frames_selectivos.py", "--marcar-caidos") != 0:
            fallos.append("marcar_caidos")
        cmd = ["--prioridad"]
        if args.lote:
            cmd += ["--lote", str(args.lote)]
        if run("frames_selectivos.py", *cmd) != 0:
            fallos.append("extraccion")
        if run("frames_selectivos.py", "--limpiar-camara") != 0:
            fallos.append("limpiar_camara")

    if run("build_search_index.py") != 0:
        fallos.append("indice")
    if run("regenerar_vault.py") != 0:
        fallos.append("vault")
    if run("verificar_vault.py") != 0:
        fallos.append("verificacion")
    if run("reporte_cobertura.py") != 0:
        fallos.append("informe")

    print("\n=== RESULTADO ===")
    if fallos:
        print("Pasos con problemas:", ", ".join(fallos))
        return 1
    print("Todo correcto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

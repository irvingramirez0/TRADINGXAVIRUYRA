#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valida la integridad y la cobertura de la base de conocimiento.

Comprueba:
- Conteos por tabla.
- Conceptos y reglas sin evidencia.
- Evidencias sin vídeo, sin fecha o con vídeo inexistente.
- Operaciones con vídeo inexistente.
- Duplicados de conceptos y reglas.
- Cobertura de transcripciones y fotogramas.
- Reglas obsoletas y su sustituto.
- Existencia física de los fotogramas anotados.

Salida legible por consola. Devuelve código 1 si hay fallos críticos.
"""

import json
import os
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    con.execute("PRAGMA synchronous=OFF")
    return con


def scalar(cur, sql, params=()):
    row = cur.execute(sql, params).fetchone()
    return row[0] if row else 0


def main():
    con = connect()
    cur = con.cursor()
    failures = []

    print("== CONTEOS ==")
    for table in ("videos", "segments", "frames", "concepts", "rules", "evidence",
                  "trades", "changes", "curriculum", "sync_log"):
        print(f"{table:12} {scalar(cur, f'SELECT COUNT(*) FROM {table}')}")

    print("\n== CONCEPTOS POR CATEGORÍA ==")
    for cat, n in cur.execute("SELECT category, COUNT(*) FROM concepts GROUP BY category ORDER BY category"):
        print(f"{cat:12} {n}")

    print("\n== REGLAS POR ESTADO ==")
    for status, n in cur.execute("SELECT status, COUNT(*) FROM rules GROUP BY status ORDER BY status"):
        print(f"{status:12} {n}")

    print("\n== EVIDENCIA POR TIPO ==")
    for st, n in cur.execute("SELECT source_type, COUNT(*) FROM evidence GROUP BY source_type ORDER BY source_type"):
        print(f"{st:12} {n}")

    print("\n== OPERACIONES POR CLASIFICACIÓN ==")
    for cl, n in cur.execute("SELECT classification, COUNT(*) FROM trades GROUP BY classification ORDER BY COUNT(*) DESC"):
        print(f"{n:3}  {cl}")

    print("\n== INTEGRIDAD ==")
    checks = []

    n = scalar(cur, """SELECT COUNT(*) FROM concepts c
                       WHERE NOT EXISTS (SELECT 1 FROM evidence e
                                         WHERE e.entity_type='concept' AND e.entity_id=c.id)""")
    checks.append(("Conceptos sin evidencia", n, 0))

    n = scalar(cur, """SELECT COUNT(*) FROM rules r
                       WHERE NOT EXISTS (SELECT 1 FROM evidence e
                                         WHERE e.entity_type='rule' AND e.entity_id=r.id)""")
    checks.append(("Reglas sin evidencia", n, 0))

    n = scalar(cur, "SELECT COUNT(*) FROM evidence WHERE video_id IS NULL OR video_id=''")
    checks.append(("Evidencias sin vídeo", n, 0))

    n = scalar(cur, "SELECT COUNT(*) FROM evidence WHERE date IS NULL OR date=''")
    checks.append(("Evidencias sin fecha", n, 0))

    n = scalar(cur, """SELECT COUNT(*) FROM evidence e
                       WHERE NOT EXISTS (SELECT 1 FROM videos v WHERE v.id=e.video_id)""")
    checks.append(("Evidencias con vídeo inexistente", n, 0))

    n = scalar(cur, """SELECT COUNT(*) FROM trades t
                       WHERE t.video_id IS NOT NULL
                         AND NOT EXISTS (SELECT 1 FROM videos v WHERE v.id=t.video_id)""")
    checks.append(("Operaciones con vídeo inexistente", n, 0))

    n = scalar(cur, """SELECT COUNT(*) FROM (SELECT name FROM concepts GROUP BY name HAVING COUNT(*)>1)""")
    checks.append(("Conceptos duplicados", n, 0))

    n = scalar(cur, """SELECT COUNT(*) FROM (SELECT name FROM rules GROUP BY name HAVING COUNT(*)>1)""")
    checks.append(("Reglas duplicadas", n, 0))

    n = scalar(cur, """SELECT COUNT(*) FROM rules r
                       WHERE r.status='obsoleto'
                         AND NOT EXISTS (SELECT 1 FROM rules x WHERE x.supersedes=r.id)""")
    checks.append(("Reglas obsoletas sin sustituto declarado", n, 0))

    n = scalar(cur, """SELECT COUNT(*) FROM rules r
                       WHERE r.supersedes IS NOT NULL AND r.supersedes <> ''
                         AND NOT EXISTS (SELECT 1 FROM rules x WHERE x.id=r.supersedes)""")
    checks.append(("Referencias 'supersedes' rotas", n, 0))

    for label, n, expected in checks:
        ok = (n == expected)
        print(f"{'OK ' if ok else 'FALLO'} {label}: {n}")
        if not ok:
            failures.append(label)

    print("\n== COBERTURA ==")
    videos = scalar(cur, "SELECT COUNT(*) FROM videos")
    with_segments = scalar(cur, "SELECT COUNT(DISTINCT video_id) FROM segments")
    with_frames = scalar(cur, "SELECT COUNT(DISTINCT video_id) FROM frames")
    ann_path = os.path.join(BASE, "03_FRAMES", "annotations.json")
    with open(ann_path, encoding="utf-8") as fh:
        ann = json.load(fh)
    entries = [(vid, item) for vid, items in ann.items() if vid != "_meta" for item in items]
    annotated = len(entries)
    print(f"Vídeos catalogados:                 {videos}")
    print(f"Vídeos con transcripción indexada:  {with_segments}")
    print(f"Vídeos con fotogramas:              {with_frames}")
    print(f"Fotogramas anotados manualmente:    {annotated}")

    missing_files = 0
    for vid, item in entries:
        path = os.path.join(BASE, "03_FRAMES", vid, item.get("file", ""))
        if not os.path.exists(path):
            missing_files += 1
            print(f"  falta: {vid}/{item.get('file')}")
    print(f"Fotogramas anotados sin archivo:    {missing_files}")
    if missing_files:
        failures.append("Fotogramas anotados sin archivo")

    print("\n== VERSIONES ==")
    for row in cur.execute("""SELECT r.id, r.name, r.status, x.id,
                                     x.name AS successor_name
                              FROM rules r LEFT JOIN rules x ON x.supersedes=r.id
                              WHERE r.status='obsoleto'"""):
        print(f"obsoleto: {row[1]} -> sustituido por id {row[3]} ({row[4]})")

    print("\n== ÚLTIMA PUBLICACIÓN CATALOGADA ==")
    row = cur.execute("SELECT id, upload_date, title FROM videos ORDER BY upload_date DESC LIMIT 1").fetchone()
    print(row)

    con.close()

    print("\n== RESULTADO ==")
    if failures:
        print("FALLOS CRÍTICOS: " + ", ".join(failures))
        return 1
    print("Sin fallos críticos. La base pasa las comprobaciones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

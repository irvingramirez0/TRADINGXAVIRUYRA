#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa los recaps analizados en 06_TRADES/*.json a la tabla `trades`.

- No duplica vídeos ya presentes.
- Conserva la clasificación y las citas en `notes`.
- Marca certeza OBSERVADO: son operaciones mostradas/relatadas por Xavi,
  no verificadas con extractos de cuenta.
"""

import json
import os
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
FILES = [
    os.path.join(BASE, "06_TRADES", "perdidas_errores.json"),
    os.path.join(BASE, "06_TRADES", "ganadores_gestion.json"),
]


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    con.execute("PRAGMA synchronous=OFF")
    return con


def clean(value):
    if value is None:
        return "no consta"
    if isinstance(value, list):
        return "; ".join(str(v) for v in value if v)
    return str(value)


def main():
    con = connect()
    cur = con.cursor()
    existing = {r[0] for r in cur.execute("SELECT video_id FROM trades")}
    inserted = 0
    skipped = 0

    for path in FILES:
        if not os.path.exists(path):
            print(f"AVISO: no existe {path}")
            continue
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for t in data.get("trades", []):
            vid = t.get("video_id")
            if not vid:
                continue
            if vid in existing:
                skipped += 1
                continue
            citas = t.get("citas") or []
            quote_note = " | ".join(
                f"[{c.get('timestamp')}s] {c.get('texto')}" for c in citas[:4]
            )
            notes = (
                f"Fuente: recap del vídeo. {clean(t.get('errores') or t.get('lecciones'))}. "
                f"Citas: {quote_note}"
            ).strip()
            cur.execute(
                """INSERT INTO trades
                   (video_id, date, instrument, timeframe, session, context, reasoning,
                    setup, entry, stop, target, result, management, post_analysis,
                    classification, certainty, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    vid,
                    t.get("fecha"),
                    clean(t.get("instrumento")),
                    clean(t.get("timeframe")),
                    clean(t.get("sesion")),
                    clean(t.get("contexto")),
                    clean(t.get("entrada_justificacion")),
                    clean(t.get("setup")),
                    clean(t.get("entry")),
                    clean(t.get("stop")),
                    clean(t.get("take_profit")),
                    clean(t.get("resultado")),
                    clean(t.get("gestion")),
                    clean(t.get("lecciones") or t.get("errores")),
                    clean(t.get("clasificacion")),
                    "OBSERVADO",
                    notes,
                ),
            )
            existing.add(vid)
            inserted += 1

    con.commit()
    total = cur.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    con.close()
    print(f"Insertados: {inserted}; omitidos por duplicado: {skipped}; total en DB: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

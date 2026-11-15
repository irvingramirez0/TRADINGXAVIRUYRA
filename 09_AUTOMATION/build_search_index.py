"""Reconstruye el índice full-text de fotogramas anotados.

Uso:
    python3 09_AUTOMATION/build_search_index.py

El índice de transcripciones (`segments_fts`) se construye en `build_transcripts.py`.
Este script añade `frames_fts` para poder buscar por lo que se ve en una captura
(descripción y análisis), no solo por lo que se dice.
"""

import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")

SKIP = ("keyword", "periodic", "scene", "frame de contexto")
# Los fotogramas nuevos de la Fase 0 se guardan con esta marca hasta que se
# anoten a mano; no deben entrar en el índice de búsqueda como si fueran prosa.
PENDIENTE = "pendiente de anotaci"


def main():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    con.execute("PRAGMA synchronous=OFF")
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS frames_fts")
    cur.execute(
        """CREATE VIRTUAL TABLE frames_fts USING fts5(
            description, analysis, video_id UNINDEXED, timestamp_sec UNINDEXED,
            path UNINDEXED, tokenize='unicode61'
        )"""
    )

    rows = cur.execute(
        "SELECT video_id, timestamp_sec, path, description, analysis FROM frames"
    ).fetchall()

    inserted = 0
    for video_id, ts, path, description, analysis in rows:
        if not description or description in SKIP:
            continue
        if description.lower().startswith(PENDIENTE):
            continue
        if description.lower().startswith("frame de contexto"):
            continue
        if not (description or analysis):
            continue
        cur.execute(
            "INSERT INTO frames_fts (description, analysis, video_id, timestamp_sec, path) "
            "VALUES (?,?,?,?,?)",
            (description or "", analysis or "", video_id, ts, path),
        )
        inserted += 1

    con.commit()
    print(f"frames_fts reconstruido: {inserted} fotogramas anotados indexados")
    con.close()


if __name__ == "__main__":
    main()

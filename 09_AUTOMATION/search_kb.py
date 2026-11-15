"""Búsqueda combinada en la base de conocimiento de Xavi Ruyra.

Uso:
    python3 09_AUTOMATION/search_kb.py "stop en mechas"
    python3 09_AUTOMATION/search_kb.py "primer IFVG" --limit 5

Busca en:
- transcripciones (`segments_fts`)
- reglas y conceptos (LIKE sobre nombre, descripción e interpretación)
- citas de evidencia (`evidence.quote`)
- fotogramas anotados (`frames_fts`: descripción y análisis visual)

No inventa: devuelve lo que hay almacenado, con vídeo y timestamp.
"""

import argparse
import os
import re
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    con.execute("PRAGMA synchronous=OFF")
    return con


def fts_query(text):
    tokens = [t for t in re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", text) if len(t) > 2]
    if not tokens:
        return None
    return " OR ".join(f'"{t}"*' for t in tokens)


def mmss(sec):
    if sec is None:
        return "?"
    sec = int(float(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()

    con = connect()
    cur = con.cursor()
    q = args.query.strip()
    fq = fts_query(q)

    print(f"== BÚSQUEDA: {q!r} ==")

    print("\n-- TRANSCRIPCIONES --")
    if fq:
        try:
            rows = cur.execute(
                """SELECT video_id, start_sec, text FROM segments_fts
                   WHERE segments_fts MATCH ? ORDER BY rank LIMIT ?""",
                (fq, args.limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    else:
        rows = []
    if not rows:
        print("  sin coincidencias")
    for vid, start, text in rows:
        snippet = " ".join((text or "").split())
        print(f"  [{vid} {mmss(start)}] {snippet[:260]}")

    print("\n-- REGLAS --")
    like = f"%{q}%"
    rows = cur.execute(
        """SELECT id, name, status, certainty FROM rules
           WHERE name LIKE ? OR description LIKE ? OR conditions LIKE ?
           ORDER BY status='vigente' DESC, id LIMIT ?""",
        (like, like, like, args.limit),
    ).fetchall()
    if not rows:
        print("  sin coincidencias")
    for rid, name, status, certainty in rows:
        print(f"  #{rid} {name} [{status}; {certainty}]")

    print("\n-- CONCEPTOS --")
    rows = cur.execute(
        """SELECT name, category, certainty FROM concepts
           WHERE name LIKE ? OR definition LIKE ? OR xavi_interpretation LIKE ?
           ORDER BY name LIMIT ?""",
        (like, like, like, args.limit),
    ).fetchall()
    if not rows:
        print("  sin coincidencias")
    for name, category, certainty in rows:
        print(f"  {name} [{category}; {certainty}]")

    print("\n-- CITAS DE EVIDENCIA --")
    rows = cur.execute(
        """SELECT video_id, timestamp_sec, quote, source_type FROM evidence
           WHERE quote LIKE ? ORDER BY date DESC LIMIT ?""",
        (like, args.limit),
    ).fetchall()
    if not rows:
        print("  sin coincidencias")
    for vid, ts, quote, stype in rows:
        print(f"  [{vid} {mmss(ts)}; {stype}] {' '.join((quote or '').split())[:260]}")

    print("\n-- FOTOGRAMAS ANOTADOS --")
    has_fts = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='frames_fts'"
    ).fetchone()
    if has_fts and fq:
        try:
            rows = cur.execute(
                """SELECT video_id, timestamp_sec, description, path FROM frames_fts
                   WHERE frames_fts MATCH ? ORDER BY rank LIMIT ?""",
                (fq, args.limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    else:
        rows = []
    if not rows:
        print("  sin coincidencias (ejecuta build_search_index.py si acabas de anotar)")
    for vid, ts, description, path in rows:
        print(f"  [{vid} {mmss(ts)}] {' '.join((description or '').split())[:240]}")
        print(f"      {path}")

    con.close()


if __name__ == "__main__":
    main()

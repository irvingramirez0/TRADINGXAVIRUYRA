#!/usr/bin/env python3
"""Inicializa la base de conocimiento SQLite de Xavi Ruyra.

Fuentes:
- 01_CATALOG/channel_videos_es.jsonl  (catálogo completo del canal)
- 02_TRANSCRIPTS/bootcamp/*.info.json (metadatos exactos del bootcamp)
- 02_TRANSCRIPTS/clean/*.segments.json (transcripciones limpias con timestamps)
"""
import glob
import json
import os
import sqlite3
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")

SCHEMA = """
PRAGMA journal_mode=DELETE;
PRAGMA locking_mode=EXCLUSIVE;
PRAGMA synchronous=OFF;

CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    upload_date TEXT,
    duration_sec INTEGER,
    url TEXT,
    channel TEXT,
    description TEXT,
    view_count INTEGER,
    category TEXT,
    priority INTEGER DEFAULT 3,
    transcript_path TEXT,
    status TEXT DEFAULT 'catalogado',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    start_sec REAL NOT NULL,
    end_sec REAL,
    text TEXT NOT NULL,
    source TEXT DEFAULT 'auto_sub_es',
    FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS segments_fts USING fts5(
    text, video_id UNINDEXED, start_sec UNINDEXED, tokenize='unicode61'
);

CREATE TABLE IF NOT EXISTS frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    path TEXT NOT NULL,
    description TEXT,
    analysis TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    aliases TEXT,
    category TEXT CHECK(category IN ('CORE','SUPPORTING','CONTEXTUAL','NOT USED','UNKNOWN')) DEFAULT 'UNKNOWN',
    definition TEXT,
    xavi_interpretation TEXT,
    how_identify TEXT,
    when_used TEXT,
    conditions TEXT,
    timeframes TEXT,
    combinations TEXT,
    application TEXT,
    common_errors TEXT,
    exceptions TEXT,
    status TEXT DEFAULT 'vigente',
    certainty TEXT CHECK(certainty IN ('EXPLICITO','OBSERVADO','INFERIDO','NO CONFIRMADO')) DEFAULT 'NO CONFIRMADO',
    first_seen_video TEXT,
    first_seen_ts REAL,
    last_updated TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    context TEXT,
    conditions TEXT,
    confirmations TEXT,
    entry_conditions TEXT,
    invalidation TEXT,
    risk_management TEXT,
    targets TEXT,
    exceptions TEXT,
    status TEXT DEFAULT 'vigente',
    certainty TEXT CHECK(certainty IN ('EXPLICITO','OBSERVADO','INFERIDO','NO CONFIRMADO')) DEFAULT 'NO CONFIRMADO',
    first_seen_video TEXT,
    first_seen_ts REAL,
    version INTEGER DEFAULT 1,
    supersedes INTEGER,
    last_updated TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    video_id TEXT NOT NULL,
    timestamp_sec REAL,
    frame_id INTEGER,
    quote TEXT,
    source_type TEXT DEFAULT 'EXPLICITO',
    date TEXT,
    url TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    date TEXT,
    instrument TEXT,
    timeframe TEXT,
    session TEXT,
    context TEXT,
    reasoning TEXT,
    setup TEXT,
    entry TEXT,
    stop TEXT,
    target TEXT,
    result TEXT,
    management TEXT,
    post_analysis TEXT,
    classification TEXT,
    certainty TEXT DEFAULT 'OBSERVADO',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    change_type TEXT NOT NULL,
    description TEXT,
    old_value TEXT,
    new_value TEXT,
    source_video TEXT,
    source_ts REAL
);

CREATE TABLE IF NOT EXISTS curriculum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_num INTEGER NOT NULL,
    module TEXT,
    lesson TEXT,
    video_id TEXT,
    concepts TEXT,
    status TEXT DEFAULT 'pendiente',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TEXT NOT NULL,
    new_videos INTEGER DEFAULT 0,
    status TEXT,
    notes TEXT
);
"""


def categorize(title: str) -> str:
    t = title.lower()
    if "bootcamp" in t:
        return "BOOTCAMP"
    if "trade recap" in t or "road to payout" in t or "bias " in t:
        return "TRADE_RECAP"
    if any(k in t for k in ["psicolog", "mentalidad", "disciplina", "miedo", "reglas", "sistema"]):
        return "PSYCHOLOGY"
    if any(k in t for k in ["miami", "dubai", "cumplea", "paraca", "coche", "vida de", "compras", "viaje"]):
        return "VLOG"
    if any(k in t for k in ["estrategia", "concepto", "liquidez", "fvg", "ifvg", "cisd", "po3", "dol",
                            "equilibrium", "backtest", "gestion", "gestión", "riesgo", "calcular",
                            "empezar", "guia", "guía", "explico", "como ", "cómo "]):
        return "EDUCATIONAL"
    return "OTHER"


def priority(title: str, category: str) -> int:
    t = title.lower()
    if category == "BOOTCAMP":
        return 1
    if any(k in t for k in ["simple estrategia", "ifvg updated", "aplicando la mejor estrategia",
                            "cisd", "dol", "equilibrium", "fvg", "po3", "gestion de riesgo",
                            "gestión de riesgo", "break-even", "daily bias", "masterclass"]):
        return 1
    if category in ("EDUCATIONAL", "TRADE_RECAP"):
        return 2
    return 3


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    cur = con.cursor()

    # 1. Catálogo completo
    catalog_path = os.path.join(BASE, "01_CATALOG", "channel_videos_es.jsonl")
    rows = [json.loads(l) for l in open(catalog_path, encoding="utf-8") if l.strip()]
    for r in rows:
        cat = categorize(r.get("title", ""))
        cur.execute(
            """INSERT OR IGNORE INTO videos
               (id,title,upload_date,duration_sec,url,channel,description,view_count,category,priority)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                r.get("id"),
                r.get("title"),
                r.get("upload_date"),
                r.get("duration"),
                f"https://www.youtube.com/watch?v={r.get('id')}",
                "Xavi Ruyra",
                r.get("description"),
                r.get("view_count"),
                cat,
                priority(r.get("title", ""), cat),
            ),
        )

    # 2. Metadatos exactos + segmentos (bootcamp y selección educativa)
    info_files = []
    for folder in ("bootcamp", "selected"):
        info_files.extend(sorted(glob.glob(os.path.join(BASE, "02_TRANSCRIPTS", folder, "*.info.json"))))
    for info_path in info_files:
        d = json.load(open(info_path, encoding="utf-8"))
        is_bootcamp = "bootcamp" in info_path
        cur.execute(
            """UPDATE videos SET title=?, upload_date=?, duration_sec=?, description=?, view_count=?,
               category=CASE WHEN ? THEN 'BOOTCAMP' ELSE category END,
               priority=CASE WHEN ? THEN 1 ELSE priority END,
               status=CASE WHEN status='analizado' THEN 'analizado' ELSE 'transcrito' END,
               updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (d.get("title"), d.get("upload_date"), d.get("duration"), d.get("description"),
             d.get("view_count"), is_bootcamp, is_bootcamp, d.get("id")),
        )
        # segmentos
        base_name = os.path.basename(info_path).replace(".info.json", "")
        seg_path = os.path.join(BASE, "02_TRANSCRIPTS", "clean", base_name + ".segments.json")
        if os.path.exists(seg_path):
            segs = json.load(open(seg_path, encoding="utf-8"))
            cur.execute("DELETE FROM segments WHERE video_id=?", (d.get("id"),))
            for s in segs:
                cur.execute(
                    "INSERT INTO segments(video_id,start_sec,end_sec,text) VALUES (?,?,?,?)",
                    (d.get("id"), s["start"], s["end"], s["text"]),
                )
            cur.execute("UPDATE videos SET transcript_path=? WHERE id=?", (seg_path, d.get("id")))

    # 3. Índice FTS
    #
    # Se confirma ANTES de reconstruir el FTS, no después. El 2026-11-15 el
    # INSERT del índice falló (el proyecto se ejecutaba sobre un montaje
    # 9p/sandbox, donde `locking_mode=EXCLUSIVE` es frágil) y, como el único
    # `con.commit()` estaba al final, se revirtió también el catálogo y los
    # segmentos ya insertados. Se daba por perdida una clase entera por un
    # índice que se puede reconstruir. El índice es derivado: si falla, se
    # avisa y se sigue; los datos de origen no se tocan.
    con.commit()
    try:
        cur.execute("DELETE FROM segments_fts")
        cur.execute(
            "INSERT INTO segments_fts(text,video_id,start_sec) SELECT text,video_id,start_sec FROM segments"
        )
        con.commit()
        fts_ok = True
        fts_error = ""
    except sqlite3.Error as exc:
        con.rollback()
        fts_ok = False
        fts_error = f"{type(exc).__name__}: {exc}"

    print("Videos:", cur.execute("SELECT COUNT(*) FROM videos").fetchone()[0])
    print("Segmentos:", cur.execute("SELECT COUNT(*) FROM segments").fetchone()[0])
    print("Bootcamp:", cur.execute("SELECT COUNT(*) FROM videos WHERE category='BOOTCAMP'").fetchone()[0])
    if fts_ok:
        print("Índice de búsqueda:", cur.execute("SELECT COUNT(*) FROM segments_fts").fetchone()[0], "segmentos")
    else:
        # Salida reconocible por `sync_bootcamp.py`, que la refleja en el
        # reporte diario. Reconstruible con `build_search_index.py` no: ese
        # rehace `frames_fts`, no `segments_fts`; se rehace reejecutando esto.
        print(f"AVISO FTS: no se pudo reconstruir segments_fts ({fts_error}). "
              "Los vídeos y segmentos SÍ quedaron guardados.")
    print("DB:", DB_PATH)
    con.close()
    return 0 if fts_ok else 2


if __name__ == "__main__":
    # `sys.exit` con el código de `main()`: antes se llamaba y se descartaba,
    # así que un fallo del índice terminaba en exit 0 y `sync_bootcamp` lo
    # reportaba como «init_db.py: OK».
    import sys

    sys.exit(main())

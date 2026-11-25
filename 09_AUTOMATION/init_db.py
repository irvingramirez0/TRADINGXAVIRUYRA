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
PRAGMA locking_mode=NORMAL;
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

-- Relaciones entre conceptos para la ruta por dependencia (N3 del rediseño).
CREATE TABLE IF NOT EXISTS concepto_relaciones (
    concepto_id INTEGER NOT NULL,
    requiere_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('requiere','se_combina_con')),
    PRIMARY KEY (concepto_id, requiere_id, tipo)
);

-- Reels citados: tablas propias. Nunca se mezclan con `videos`/`evidence`
-- de YouTube: validate_kb exige que todo vídeo citado exista en `videos`.
CREATE TABLE IF NOT EXISTS reel_items (
    code TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    date_utc TEXT,
    duration_sec INTEGER,
    tono TEXT,
    clasificacion TEXT NOT NULL CHECK(clasificacion IN ('RELEVANTE','IRRELEVANTE','DESCARTADO')),
    certainty TEXT NOT NULL,
    motivo TEXT,
    estado_sitio TEXT NOT NULL DEFAULT 'pendiente',
    in_window INTEGER NOT NULL DEFAULT 1,
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reel_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reel_code TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    quote TEXT NOT NULL,
    entity_tipo TEXT NOT NULL CHECK(entity_tipo IN ('concept','rule')),
    entity_id INTEGER NOT NULL,
    certainty TEXT NOT NULL,
    FOREIGN KEY(reel_code) REFERENCES reel_items(code),
    UNIQUE (reel_code, timestamp_sec, quote)
);
"""


# Relaciones derivadas de la metodología y de los campos `definition`,
# `conditions` y `how_identify` de `concepts`. Cada fila se apoya en el mapa
# metodológico o en una combinación descrita en la propia ficha; no se usa la
# frecuencia para inventar un orden.
RELACIONES_REQUIERE = [
    (42, 40),
    (42, 41),
    (46, 42),
    (48, 40),
    (48, 41),
    (56, 42),
    (57, 42),
    (58, 40),
    (59, 40),
    (59, 58),
    (60, 40),
    (63, 42),
    (64, 40),
    (64, 42),
    (44, 40),
    (44, 42),
    (45, 42),
    (47, 48),
    (53, 41),
    (53, 42),
    (54, 44),
    (55, 44),
    (61, 40),
    (79, 41),
    (79, 40),
    (86, 40),
    (88, 40),
    (88, 42),
    (43, 42),
    (43, 44),
    (52, 42),
    (52, 44),
    (93, 42),
    (93, 44),
    (96, 45),
    (96, 44),
    (96, 93),
    (95, 44),
    (66, 40),
    (67, 44),
    (81, 95),
    (82, 95),
    (87, 95),
    (89, 82),
    (90, 95),
    (92, 95),
    (65, 40),
    (62, 42),
    (62, 44),
    (49, 47),
    (50, 47),
    (51, 47),
    (80, 63),
    (94, 42),
    (84, 83),
    (85, 84),
    (97, 44),
]

RELACIONES_COMBINA = [
    (40, 44),
    (40, 47),
    (40, 42),
    (41, 40),
    (42, 43),
    (42, 44),
    (42, 47),
    (42, 53),
    (43, 52),
    (43, 47),
    (44, 45),
    (44, 47),
    (44, 54),
    (44, 55),
    (45, 96),
    (46, 47),
    (47, 49),
    (47, 50),
    (47, 51),
    (52, 47),
    (53, 47),
    (55, 54),
    (56, 42),
    (57, 42),
    (58, 44),
    (59, 47),
    (61, 44),
    (62, 42),
    (63, 47),
    (66, 97),
    (68, 97),
    (84, 85),
    (93, 96),
    (95, 81),
    (95, 82),
    (95, 87),
    (95, 89),
    (95, 90),
    (95, 92),
    (96, 44),
    (97, 83),
]

def sembrar_relaciones(con):
    """Insertar relaciones conocidas sin borrar las añadidas después por revisión."""
    con.executemany(
        "INSERT OR IGNORE INTO concepto_relaciones(concepto_id,requiere_id,tipo) VALUES(?,?,?)",
        [(a, b, "requiere") for a, b in RELACIONES_REQUIERE]
        + [(a, b, "se_combina_con") for a, b in RELACIONES_COMBINA],
    )
    con.commit()


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
    processed_video_ids = []
    for folder in ("bootcamp", "selected"):
        info_files.extend(sorted(glob.glob(os.path.join(BASE, "02_TRANSCRIPTS", folder, "*.info.json"))))
    for info_path in info_files:
        d = json.load(open(info_path, encoding="utf-8"))
        is_bootcamp = "bootcamp" in info_path
        cur.execute(
            """UPDATE videos SET title=?, upload_date=?, duration_sec=?, description=?, view_count=?,
               category=CASE WHEN ? THEN 'BOOTCAMP' ELSE category END,
               priority=CASE WHEN ? THEN 1 ELSE priority END,
               -- Solo se ASCIENDE a 'transcrito'. Antes esta rama era
               -- `CASE WHEN status='analizado' THEN 'analizado' ELSE
               -- 'transcrito' END`, que DEGRADABA dos estados:
               --   'analizado'    -> se conservaba (única excepción)
               --   'procesado'    -> volvía a 'transcrito' (Día 20)
               --   'no_disponible'-> volvía a 'transcrito', y un vídeo
               --                     caído reaparecía como si tuviera
               --                     transcripción
               -- `frames_selectivos.py` y `reporte_cobertura.py` filtran por
               -- esos estados, así que la degradación cambiaba lo que el
               -- pipeline intentaba descargar. Los estados no se pisan desde
               -- aquí: reindexar segmentos no dice nada sobre si el vídeo se
               -- procesó o sigue accesible.
               status=CASE
                   WHEN status IN ('analizado','procesado','no_disponible') THEN status
                   ELSE 'transcrito'
               END,
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
            processed_video_ids.append(d.get("id"))

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
    fts_ok = True
    fts_error = ""
    # Reindexado INCREMENTAL por vídeo. El rebuild completo
    # (`DELETE FROM segments_fts` + un único INSERT de toda la tabla) falló
    # el 2026-11-21 con «database or disk is full» sobre el montaje del
    # proyecto: el journal temporal de una transacción tan grande no cabe
    # en ese sistema de ficheros. Además dejaba el índice vacío si fallaba
    # a mitad. Ahora cada vídeo procesado se refresca en su propia
    # transacción; lo que no se ha tocado conserva su índice.
    for vid in processed_video_ids:
        try:
            cur.execute("DELETE FROM segments_fts WHERE video_id=?", (vid,))
            cur.execute(
                "INSERT INTO segments_fts(text,video_id,start_sec) "
                "SELECT text,video_id,start_sec FROM segments WHERE video_id=?",
                (vid,),
            )
            con.commit()
        except sqlite3.Error as exc:
            con.rollback()
            fts_ok = False
            fts_error = f"{type(exc).__name__}: {exc}"
            break

    sembrar_relaciones(con)
    print("Relaciones:", cur.execute("SELECT COUNT(*) FROM concepto_relaciones").fetchone()[0])
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica las anotaciones manuales de 03_FRAMES/annotations.json a la tabla `frames`
y enlaza cada evidencia con el fotograma más cercano de su mismo vídeo.

Uso:
    python3 09_AUTOMATION/annotate_frames.py
"""

import json
import os
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
ANNOTATIONS = os.path.join(BASE, "03_FRAMES", "annotations.json")


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    con.execute("PRAGMA synchronous=OFF")
    return con


def main():
    with open(ANNOTATIONS, encoding="utf-8") as fh:
        data = json.load(fh)

    con = connect()
    cur = con.cursor()
    applied = 0
    missing = []

    for video_id, entries in data.items():
        if video_id.startswith("_"):
            continue
        for entry in entries:
            ts = float(entry["timestamp"])
            row = cur.execute(
                "SELECT id FROM frames WHERE video_id=? AND ABS(timestamp_sec-?) < 1.0 "
                "ORDER BY ABS(timestamp_sec-?) LIMIT 1",
                (video_id, ts, ts),
            ).fetchone()
            if not row:
                missing.append((video_id, ts))
                continue
            cur.execute(
                "UPDATE frames SET description=?, analysis=? WHERE id=?",
                (entry["description"], entry["analysis"], row[0]),
            )
            applied += 1

    # Enlazar evidencia con el fotograma más cercano (máximo 20 s de diferencia).
    # Se hace en Python para evitar problemas de resolución de columnas en UPDATE.
    frame_rows = cur.execute(
        "SELECT id, video_id, timestamp_sec FROM frames ORDER BY video_id, timestamp_sec"
    ).fetchall()
    by_video = {}
    for fid, vid, fts in frame_rows:
        by_video.setdefault(vid, []).append((fts, fid))

    evidence_rows = cur.execute(
        "SELECT id, video_id, timestamp_sec FROM evidence WHERE timestamp_sec IS NOT NULL"
    ).fetchall()
    for eid, vid, ets in evidence_rows:
        candidates = by_video.get(vid)
        if not candidates:
            continue
        fts, fid = min(candidates, key=lambda x: abs(x[0] - ets))
        if abs(fts - ets) <= 20:
            cur.execute("UPDATE evidence SET frame_id=? WHERE id=?", (fid, eid))
    linked = cur.execute("SELECT COUNT(*) FROM evidence WHERE frame_id IS NOT NULL").fetchone()[0]
    total = cur.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]

    con.commit()
    con.close()

    print(f"Anotaciones aplicadas: {applied}")
    if missing:
        print("No encontradas:")
        for vid, ts in missing:
            print(f"  {vid} @ {ts}")
    print(f"Evidencias enlazadas a fotograma: {linked}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

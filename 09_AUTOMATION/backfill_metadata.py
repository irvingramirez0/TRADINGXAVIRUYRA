#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rellena videos.upload_date que faltan usando yt-dlp, en tandas.

Uso:
    python3 09_AUTOMATION/backfill_metadata.py --limit 50
    python3 09_AUTOMATION/backfill_metadata.py --limit 50 --sleep 2

Notas:
- No descarga vídeo ni subtítulos: solo metadatos (upload_date).
- Espacia las peticiones y reintenta con backoff si YouTube devuelve 429.
- Escribe el progreso en 09_AUTOMATION/logs/backfill_dates.log.
"""

import argparse
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
LOG = os.path.join(BASE, "09_AUTOMATION", "logs", "backfill_dates.log")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"[{now()}] {msg}\n")


def connect():
    con = sqlite3.connect(DB, timeout=30)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA synchronous=OFF")
    return con


def fetch_upload_date(video_id, attempts=4):
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--skip-download", "--no-warnings",
        "--extractor-args", "youtube:player_client=android",
        "--print", "%(id)s|%(upload_date)s",
        url,
    ]
    for attempt in range(1, attempts + 1):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            log(f"{video_id}: timeout (intento {attempt})")
            time.sleep(5 * attempt)
            continue
        if proc.returncode == 0:
            lines = [ln.strip() for ln in proc.stdout.splitlines() if "|" in ln]
            if lines:
                _, date = lines[-1].split("|", 1)
                date = date.strip()
                if re.fullmatch(r"\d{8}", date):
                    return date
            return None
        err = (proc.stderr or "").strip().splitlines()
        err_tail = err[-1] if err else f"exit {proc.returncode}"
        log(f"{video_id}: fallo intento {attempt}: {err_tail[:180]}")
        permanent = (
            "not available" in (proc.stderr or "").lower()
            or "private video" in (proc.stderr or "").lower()
            or "has been removed" in (proc.stderr or "").lower()
            or "account associated with this video has been terminated" in (proc.stderr or "").lower()
        )
        if permanent:
            return "NO_DISPONIBLE"
        if "429" in (proc.stderr or "") or "Too Many Requests" in (proc.stderr or ""):
            time.sleep(20 * attempt)
        else:
            time.sleep(5 * attempt)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--sleep", type=float, default=2.0)
    args = ap.parse_args()

    con = connect()
    cur = con.cursor()
    rows = cur.execute(
        "SELECT id FROM videos WHERE upload_date IS NULL OR upload_date = '' ORDER BY rowid LIMIT ?",
        (args.limit,),
    ).fetchall()

    log(f"tanda iniciada: {len(rows)} vídeos, sleep={args.sleep}s")
    ok = fail = unavailable = 0
    for i, (video_id,) in enumerate(rows, 1):
        date = fetch_upload_date(video_id)
        if date == "NO_DISPONIBLE":
            cur.execute("UPDATE videos SET status = 'no_disponible' WHERE id = ?", (video_id,))
            unavailable += 1
            print(f"[{i}/{len(rows)}] {video_id} -> no disponible", flush=True)
        elif date:
            iso = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
            cur.execute("UPDATE videos SET upload_date = ? WHERE id = ?", (iso, video_id))
            ok += 1
            print(f"[{i}/{len(rows)}] {video_id} -> {iso}", flush=True)
        else:
            fail += 1
            print(f"[{i}/{len(rows)}] {video_id} -> sin fecha", flush=True)
        if i % 5 == 0:
            con.commit()
        time.sleep(args.sleep)
    con.commit()

    pending = cur.execute(
        "SELECT COUNT(*) FROM videos WHERE upload_date IS NULL OR upload_date = ''"
    ).fetchone()[0]
    log(f"tanda terminada: ok={ok}, fallos={fail}, no_disponibles={unavailable}, pendientes={pending}")
    print(f"\nok={ok} fallos={fail} no_disponibles={unavailable} pendientes={pending}")
    con.close()


if __name__ == "__main__":
    main()

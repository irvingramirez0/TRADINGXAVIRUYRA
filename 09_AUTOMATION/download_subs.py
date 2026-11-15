#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descarga subtítulos automáticos en español de los vídeos en alcance que aún no
tienen transcripción, en tandas y con reintentos.

Uso:
    python3 09_AUTOMATION/download_subs.py --limit 25 --sleep 2.5

- Guarda los VTT y el info.json en 02_TRANSCRIPTS/selected/.
- Usa el cliente android de YouTube: el cliente por defecto falla en vídeos antiguos.
- Si YouTube devuelve 429, espera y reintenta.
- No descarga vídeo.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
OUT_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "selected")
LOG = os.path.join(BASE, "09_AUTOMATION", "logs", "download_subs.log")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"[{now()}] {msg}\n")


def already_downloaded(video_id):
    hits = glob.glob(os.path.join(OUT_DIR, f"{video_id}_*.es-orig.vtt"))
    hits += glob.glob(os.path.join(OUT_DIR, f"{video_id}_*.es.vtt"))
    return bool(hits)


def run_ytdlp(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--skip-download",
        "--write-auto-subs",
        "--sub-langs", "es-orig,es",
        "--sub-format", "vtt",
        "--write-info-json",
        "--no-warnings",
        "--extractor-args", "youtube:player_client=android",
        "-o", "%(id)s_%(title)s.%(ext)s",
        "-P", OUT_DIR,
        url,
    ]
    for attempt in range(1, 4):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            log(f"{video_id}: timeout (intento {attempt})")
            time.sleep(5 * attempt)
            continue
        if proc.returncode == 0:
            return True, (proc.stderr or "").strip()[:200]
        err = (proc.stderr or "").strip()
        if "429" in err or "Too Many Requests" in err:
            wait = 30 * attempt
            log(f"{video_id}: 429, esperando {wait}s")
            time.sleep(wait)
            continue
        return False, err[-200:]
    return False, "reintentos agotados"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--sleep", type=float, default=2.5)
    args = ap.parse_args()

    import sqlite3
    con = sqlite3.connect(DB, timeout=30)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA synchronous=OFF")
    cur = con.cursor()
    rows = cur.execute("""
        SELECT v.id FROM videos v
        WHERE v.in_scope = 1
          AND NOT EXISTS (SELECT 1 FROM segments s WHERE s.video_id = v.id)
        ORDER BY v.upload_date DESC, v.rowid
        LIMIT ?
    """, (args.limit,)).fetchall()
    con.close()

    os.makedirs(OUT_DIR, exist_ok=True)
    log(f"tanda iniciada: {len(rows)} vídeos, sleep={args.sleep}s")
    ok = skipped = fail = 0
    for i, (video_id,) in enumerate(rows, 1):
        if already_downloaded(video_id):
            skipped += 1
            print(f"[{i}/{len(rows)}] {video_id} -> ya existe", flush=True)
            continue
        success, msg = run_ytdlp(video_id)
        if success:
            # Si solo bajó .es.vtt, duplicarlo como .es-orig.vtt para el pipeline.
            es_orig = glob.glob(os.path.join(OUT_DIR, f"{video_id}_*.es-orig.vtt"))
            es_only = glob.glob(os.path.join(OUT_DIR, f"{video_id}_*.es.vtt"))
            if not es_orig and es_only:
                src = es_only[0]
                shutil.copyfile(src, src.replace(".es.vtt", ".es-orig.vtt"))
            if glob.glob(os.path.join(OUT_DIR, f"{video_id}_*.es-orig.vtt")):
                ok += 1
                print(f"[{i}/{len(rows)}] {video_id} -> ok", flush=True)
            else:
                fail += 1
                print(f"[{i}/{len(rows)}] {video_id} -> sin subtítulos ES", flush=True)
                log(f"{video_id}: sin subtítulos ES. {msg}")
        else:
            fail += 1
            print(f"[{i}/{len(rows)}] {video_id} -> fallo", flush=True)
            log(f"{video_id}: fallo. {msg}")
        time.sleep(args.sleep)

    log(f"tanda terminada: ok={ok}, ya_existian={skipped}, fallos={fail}")
    print(f"\nok={ok} ya_existian={skipped} fallos={fail}")


if __name__ == "__main__":
    main()

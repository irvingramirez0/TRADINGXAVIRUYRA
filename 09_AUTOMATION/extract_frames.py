#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae fotogramas relevantes de un vídeo de Xavi Ruyra.

Tres fuentes de fotogramas:
1. Cambios de escena (FFmpeg scene detection).
2. Menciones de conceptos clave en la transcripción (FVG, liquidez, DOL, PO3...).
3. Muestreo periódico de seguridad (cada 90 s).

Salida:
    03_FRAMES/<video_id>/<timestamp>_<motivo>.jpg
    03_FRAMES/<video_id>/index.csv
    Tabla `frames` de la base de conocimiento.

Uso:
    python3 09_AUTOMATION/extract_frames.py <video_id>
    python3 09_AUTOMATION/extract_frames.py <video_id> --scene-threshold 0.35
"""

import argparse
import csv
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
VIDEO_DIR = os.path.join(BASE, "03_FRAMES", "videos")
FRAMES_DIR = os.path.join(BASE, "03_FRAMES")

KEYWORDS = [
    "liquidez", "bsl", "ssl", "swing", "fair value", "fvg", "ifvg", "inverse",
    "dol", "draw on liquidity", "po3", "power of 3", "amd", "manipulaci",
    "distribuci", "judas", "9:30", "9:45", "10:00", "10:15", "10:30",
    "cisd", "equilibrium", "premium", "descuento", "gann", "smt",
    "true manipulation", "break-even", "break even", "stop", "target",
    "entrada", "gap", "nwog", "ndog", "equal high", "equal low", "lrl",
    "data high", "data low", "vela", "mecha", "cuerpo", "temporalidad",
    "tradingview", "cuadr", "colores", "fondeo", "evaluaci",
]


def hhmmss(sec):
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}-{m:02d}-{s:02d}"
    return f"{m:02d}-{s:02d}"


def find_transcript(video_id):
    pattern = os.path.join(BASE, "02_TRANSCRIPTS", "clean", f"*{video_id}*.segments.json")
    matches = sorted(glob.glob(pattern))
    return matches[0] if matches else None


def load_segments(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def scene_timestamps(video_path, threshold):
    """Devuelve timestamps de cambios de escena usando showinfo."""
    cmd = [
        "ffmpeg", "-hide_banner", "-i", video_path,
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-vsync", "vfr", "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    times = []
    for line in proc.stderr.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            times.append(float(m.group(1)))
    return times


def extract_at(video_path, ts, out_path):
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-ss", f"{ts:.3f}", "-i", video_path,
        "-frames:v", "1", "-q:v", "2", "-y", out_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return proc.returncode == 0 and os.path.exists(out_path)


def keyword_hits(segments):
    hits = []
    for seg in segments:
        text = (seg.get("text") or "").lower()
        if any(k in text for k in KEYWORDS):
            hits.append((float(seg["start"]), seg.get("text", "")))
    return hits


def dedupe(candidates, min_gap=1.5):
    """candidates: (ts, reason, text). Conserva el primero de cada grupo."""
    candidates = sorted(candidates, key=lambda x: x[0])
    out = []
    for ts, reason, text in candidates:
        if not out or ts - out[-1][0] > min_gap:
            out.append((ts, reason, text))
        else:
            # Si el nuevo tiene motivo keyword y el anterior no, lo sustituye.
            if reason.startswith("keyword") and not out[-1][1].startswith("keyword"):
                out[-1] = (ts, reason, text)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    parser.add_argument("--scene-threshold", type=float, default=0.32)
    parser.add_argument("--period", type=float, default=90.0)
    parser.add_argument("--max-scene", type=int, default=80)
    parser.add_argument("--max-keyword", type=int, default=60)
    args = parser.parse_args()

    vid = args.video_id
    video_path = os.path.join(VIDEO_DIR, f"{vid}.mp4")
    if not os.path.exists(video_path):
        print(f"ERROR: no existe {video_path}")
        return 1

    out_dir = os.path.join(FRAMES_DIR, vid)
    os.makedirs(out_dir, exist_ok=True)

    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", video_path,
    ]).decode().strip())

    segments = load_segments(find_transcript(vid))
    print(f"Vídeo {vid}: {duration:.0f}s; segmentos: {len(segments)}")

    candidates = []

    # 1. Escenas
    print("Detectando cambios de escena...")
    scenes = scene_timestamps(video_path, args.scene_threshold)
    print(f"  escenas detectadas: {len(scenes)}")
    for ts in scenes[:args.max_scene]:
        candidates.append((ts, "scene", ""))

    # 2. Keywords
    hits = keyword_hits(segments)
    print(f"  segmentos con keywords: {len(hits)}")
    # Distribuir: no quedarse solo con los primeros.
    if len(hits) > args.max_keyword:
        step = len(hits) / args.max_keyword
        hits = [hits[int(i * step)] for i in range(args.max_keyword)]
    for ts, text in hits:
        candidates.append((ts, "keyword", text))

    # 3. Periódico
    ts = 5.0
    while ts < duration:
        candidates.append((ts, "periodic", ""))
        ts += args.period

    chosen = dedupe(candidates, min_gap=2.0)
    print(f"  fotogramas a extraer: {len(chosen)}")

    index_path = os.path.join(out_dir, "index.csv")
    rows = []
    for i, (ts, reason, text) in enumerate(chosen, start=1):
        name = f"{i:04d}_{hhmmss(ts)}_{reason}.jpg"
        path = os.path.join(out_dir, name)
        if not extract_at(video_path, ts, path):
            print(f"  AVISO: fallo en {ts:.1f}s")
            continue
        rows.append({
            "video_id": vid,
            "timestamp_sec": round(ts, 3),
            "timestamp": hhmmss(ts),
            "path": path,
            "reason": reason,
            "transcript": text,
        })

    with open(index_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "video_id", "timestamp_sec", "timestamp", "path", "reason", "transcript",
        ])
        writer.writeheader()
        writer.writerows(rows)

    # DB
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    con.execute("PRAGMA synchronous=OFF")
    cur = con.cursor()
    cur.execute("DELETE FROM frames WHERE video_id=?", (vid,))
    for r in rows:
        cur.execute(
            "INSERT INTO frames(video_id, timestamp_sec, path, description, analysis) VALUES (?,?,?,?,?)",
            (vid, r["timestamp_sec"], r["path"], r["reason"], r["transcript"] or None),
        )
    con.commit()
    con.close()

    print(f"OK: {len(rows)} fotogramas en {out_dir}")
    print(f"Índice: {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

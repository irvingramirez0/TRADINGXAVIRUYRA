#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumen del estado de la ingesta de reels de Instagram."""

import json
import os
from collections import Counter
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_state.jsonl")
META_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_meta.jsonl")
TRANS_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "instagram")
REPORT_PATH = os.path.join(BASE, "10_REPORTS", "instagram_reels_progreso.md")


def load_jsonl(path):
    rows = {}
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("code"):
                rows[row["code"]] = row
    return rows


def main():
    meta = load_jsonl(META_PATH)
    state = load_jsonl(STATE_PATH)
    transcripts = [f for f in os.listdir(TRANS_DIR) if f.endswith(".json")] if os.path.isdir(TRANS_DIR) else []
    counts = Counter(v.get("status", "?") for v in state.values())
    total = len(meta)
    resolved = counts.get("transcribed", 0) + counts.get("no_speech", 0) + counts.get("skipped", 0)
    pending = total - resolved
    chars = sum(v.get("chars") or 0 for v in state.values())
    lines = [
        "# PROGRESO DE LA INGESTA DE REELS",
        "",
        f"**Actualizado:** {datetime.now().isoformat(timespec='seconds')}  ",
        f"**Total catalogado:** {total}  ",
        f"**Resueltos:** {resolved}  ",
        f"**Pendientes:** {pending}  ",
        f"**Transcripciones en disco:** {len(transcripts)}  ",
        f"**Caracteres transcritos (estado):** {chars:,}  ",
        "",
        "## Estados",
        "",
        "| Estado | Reels |",
        "|---|---:|",
    ]
    for key, value in counts.most_common():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Últimos procesados",
        "",
        "| Fecha | Código | Dur. | Caracteres | Estado |",
        "|---|---|---:|---:|---|",
    ]
    recent = sorted(
        [v for v in state.values() if v.get("processed_at")],
        key=lambda v: v.get("processed_at") or "",
        reverse=True,
    )[:20]
    for row in recent:
        lines.append(
            f"| {(row.get('date_utc') or '')[:10]} | {row.get('code')} | "
            f"{row.get('duration_sec') or ''} | {row.get('chars') or 0} | "
            f"{row.get('status')} |"
        )
    lines += [
        "",
        "## Cómo seguir",
        "",
        "```bash",
        "python3 09_AUTOMATION/instagram_reels_batch.py --minutes 8 --limit 40 --model small --sleep 2",
        "```",
        "",
        "El script es reanudable: omite lo ya transcrito y para si Instagram devuelve 429.",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

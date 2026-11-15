#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cola de revisión de tono para los reels de Instagram.

No clasifica solo: detecta los reels transcritos que aún no tienen etiqueta
en 01_CATALOG/instagram_reels_tono.jsonl y los ordena por señales de riesgo
(bromas, ratios extremos, promesas, lifestyle, etc.) para revisarlos a mano.

Uso:
    python3 09_AUTOMATION/instagram_reels_tono.py
    python3 09_AUTOMATION/instagram_reels_tono.py --queue
    python3 09_AUTOMATION/instagram_reels_tono.py --code DfXU-KGswFv

El catálogo lo sigue decidiendo una persona/LLM; este script solo evita
que se queden reels sin revisar según avanza la ingesta.
"""

import argparse
import glob
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "instagram")
TONO_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_tono.jsonl")
STATE_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_state.jsonl")
META_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_meta.jsonl")
QUEUE_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_tono_cola.jsonl")

# Señales que no prueban nada por sí solas, pero ayudan a priorizar la lectura.
SEÑALES = [
    (r"\bes broma\b|\b broma \b|\bhumor\b|#humor|jaja|🤡|😂|POV\b", "broma/humor"),
    (r"\breto\b|quien pierda|libre albedr|challenge|apuesta", "reto/juego"),
    (r"\b1\s*a\s*(\d{2,3})\b", "ratio 1:N"),
    (r"100\s*%|garantiz|asegur|m[ií]nimo|imposible|seguro que", "promesa"),
    (r"\bpayout|retiro|retirar|fondead|eval\b", "payout/eval"),
    (r"\bcoche|supra|ferrari|lambor|dubai|viaje|hotel|restaurante|cena|comida", "lifestyle"),
]


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
            code = row.get("code")
            if code:
                rows[code] = row
    return rows


def transcript_text(path):
    d = json.load(open(path, encoding="utf-8"))
    text = (d.get("text") or "").strip()
    if not text and d.get("segments"):
        text = " ".join(s.get("text", "") for s in d["segments"]).strip()
    return d, re.sub(r"\s+", " ", text)


def flags_for(text):
    found = []
    for pattern, label in SEÑALES:
        if re.search(pattern, text, re.I):
            found.append(label)
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", action="store_true",
                        help="escribe la cola de no etiquetados")
    parser.add_argument("--code", default=None,
                        help="muestra la transcripción y la etiqueta de un reel")
    args = parser.parse_args()

    tono = load_jsonl(TONO_PATH)
    state = load_jsonl(STATE_PATH)
    meta = load_jsonl(META_PATH)

    if args.code:
        code = args.code.strip()
        path = os.path.join(TRANS_DIR, f"{code}.json")
        if not os.path.exists(path):
            print(f"No hay transcripción para {code}.")
            return 1
        d, text = transcript_text(path)
        print(f"Código: {code}")
        print(f"Fecha: {d.get('date_utc')}")
        print(f"Duración: {d.get('duration_sec') or d.get('duration')} s")
        print(f"Etiqueta: {json.dumps(tono.get(code, {}), ensure_ascii=False)}")
        print(f"Señales: {', '.join(flags_for(text)) or 'ninguna'}")
        print("\nTranscripción:\n" + (text or "(sin texto)"))
        return 0

    paths = glob.glob(os.path.join(TRANS_DIR, "*.json"))
    disponibles = {}
    for path in paths:
        code = os.path.basename(path)[:-5]
        disponibles[code] = path

    pending = [c for c in disponibles if c not in tono]
    print(f"Reels catalogados: {len(meta)}")
    print(f"Transcripciones disponibles: {len(disponibles)}")
    print(f"Etiquetados en tono: {len(set(tono) & set(disponibles))}")
    print(f"Transcritos sin etiqueta de tono: {len(pending)}")

    if not pending:
        print("No hay transcripciones pendientes de etiquetar.")
        return 0

    rows = []
    for code in pending:
        d, text = transcript_text(disponibles[code])
        flags = flags_for(text)
        score = len(flags)
        rows.append({
            "code": code,
            "date_utc": d.get("date_utc"),
            "duration_sec": d.get("duration_sec") or d.get("duration"),
            "chars": len(text),
            "flags": flags,
            "score": score,
            "snippet": text[:240],
        })
    rows.sort(key=lambda r: (-r["score"], r["date_utc"] or ""))

    print("\nCandidatos prioritarios (señales, no veredictos):")
    for r in rows[:25]:
        print(f"  {r['code']} {str(r['date_utc'])[:10]} {r['chars']}c "
              f"[{', '.join(r['flags']) or 'sin señales'}] {r['snippet'][:120]}")

    if args.queue:
        with open(QUEUE_PATH, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"\nCola escrita en {os.path.relpath(QUEUE_PATH, BASE)} ({len(rows)} filas).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

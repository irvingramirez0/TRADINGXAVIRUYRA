#!/usr/bin/env python3
"""Convierte los VTT automáticos de YouTube en transcripciones limpias con timestamps.

Los subtítulos automáticos de YouTube son "rolling captions": cada cue repite
las líneas anteriores y añade una nueva. Este script conserva solo la línea
nueva de cada cue, elimina las etiquetas <...> y agrupa el resultado en
segmentos de ~30 s para facilitar la lectura y la trazabilidad.

Uso:
    python3 build_transcripts.py
"""
import glob
import json
import os
import re
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOTCAMP_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "bootcamp")
SELECTED_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "selected")
OUT_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "clean")
os.makedirs(OUT_DIR, exist_ok=True)

TAG_RE = re.compile(r"<[^>]+>")


def ts_to_seconds(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def fmt(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def parse_vtt(path: str):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    blocks = re.split(r"\n\s*\n", raw.replace("\r\n", "\n"))
    cues = []
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if not lines or "-->" not in lines[0]:
            continue
        header = lines[0]
        start_s, end_s = [x.strip().split(" ")[0] for x in header.split("-->")]
        text_lines = [TAG_RE.sub("", ln).strip() for ln in lines[1:]]
        text_lines = [ln for ln in text_lines if ln]
        if not text_lines:
            continue
        # La última línea es la nueva; las anteriores son contexto repetido.
        new_text = text_lines[-1]
        cues.append(
            {
                "start": ts_to_seconds(start_s),
                "end": ts_to_seconds(end_s),
                "text": new_text,
            }
        )
    # Deduplicar líneas consecutivas idénticas o ya incluidas en la anterior.
    cleaned = []
    prev = ""
    for cue in cues:
        text = re.sub(r"\s+", " ", cue["text"]).strip()
        if not text or text == prev:
            continue
        if cleaned and text.startswith(cleaned[-1]["text"] + " "):
            # La nueva línea contiene la anterior + texto nuevo.
            text = text[len(cleaned[-1]["text"]) :].strip()
            if not text:
                continue
        cleaned.append({"start": cue["start"], "end": cue["end"], "text": text})
        prev = text
    return cleaned


def group_segments(cues, window=30):
    segments = []
    current = None
    for cue in cues:
        if current is None or cue["start"] - current["start"] >= window:
            if current:
                segments.append(current)
            current = {
                "start": cue["start"],
                "end": cue["end"],
                "text": cue["text"],
            }
        else:
            current["text"] += " " + cue["text"]
            current["end"] = cue["end"]
    if current:
        segments.append(current)
    return segments


def main():
    files = []
    for folder in (BOOTCAMP_DIR, SELECTED_DIR):
        files.extend(sorted(glob.glob(os.path.join(folder, "*.es-orig.vtt"))))
    for path in files:
        name = os.path.basename(path).replace(".es-orig.vtt", "")
        cues = parse_vtt(path)
        segments = group_segments(cues)
        # Guardar JSON con segmentos
        json_path = os.path.join(OUT_DIR, name + ".segments.json")
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(segments, fh, ensure_ascii=False, indent=2)
        # Guardar texto legible con marcas de tiempo
        txt_path = os.path.join(OUT_DIR, name + ".txt")
        with open(txt_path, "w", encoding="utf-8") as fh:
            fh.write(f"# {name}\n\n")
            for seg in segments:
                fh.write(f"[{fmt(seg['start'])}] {seg['text']}\n\n")
        words = sum(len(s["text"].split()) for s in segments)
        # Los títulos de YouTube traen «：» (U+FF1A, dos puntos de ancho
        # completo; el canal usa ese carácter en «Bootcamp Día 21： …»). En una
        # consola Windows con cp1252 eso lanza UnicodeEncodeError y aborta el
        # script a mitad, dejando el Día 21 sin transcripción aunque los
        # subtítulos estuvieran descargados. Se imprime saneado: el archivo en
        # disco conserva el nombre original.
        try:
            print(f"{name}: {len(segments)} segmentos, {words} palabras -> {txt_path}")
        except UnicodeEncodeError:
            seguro = name.encode("ascii", "replace").decode("ascii")
            print(f"{seguro}: {len(segments)} segmentos, {words} palabras")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesa por lotes los reels de Instagram ya catalogados.

Por cada reel:
1. Lo descarga con yt-dlp; si se pasa --cookies, usa esa sesión (el lanzador
   pasa las cookies de la cuenta secundaria en www.instagram.com_cookies.txt).
2. Lee la duración con ffprobe.
3. Lo transcribe con faster-whisper en español.
4. Guarda el JSON de transcripción en 02_TRANSCRIPTS/instagram/.
5. Borra el vídeo para no llenar el disco.
6. Actualiza el estado en 01_CATALOG/instagram_reels_state.jsonl.

El estado permite cortar y reanudar. Los reels sin habla se marcan como
`no_speech` y no se vuelven a procesar.

Uso:
    python3 09_AUTOMATION/instagram_reels_batch.py --minutes 2.2 --limit 10
    python3 09_AUTOMATION/instagram_reels_batch.py --minutes 2.2 --limit 10 --keep-video

Requiere:
    yt-dlp, ffmpeg, faster-whisper
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS_PATH = os.path.join(BASE, "reels_xaviruyra.txt")
META_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_meta.jsonl")
STATE_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_state.jsonl")
TRANS_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "instagram")
LOG_PATH = os.path.join(BASE, "09_AUTOMATION", "logs", "instagram_reels_batch.log")
# Directorio temporal propio del usuario: /tmp/reels_batch puede quedar de una
# ejecución anterior con otro uid y no ser escribible.
TMP_DIR = os.environ.get("REELS_TMP_DIR") or os.path.join(
    tempfile.gettempdir(), f"reels_batch_{os.getuid()}"
)
# Guardar el modelo en la carpeta del proyecto para que sobreviva al reinicio
# del VM entre tareas programadas.
os.environ.setdefault(
    "HF_HOME", os.path.join(BASE, "09_AUTOMATION", ".cache", "huggingface")
)


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def log(msg):
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


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
            key = row.get("code")
            if key:
                rows[key] = row
    return rows


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as fh:
        for code in sorted(state):
            fh.write(json.dumps(state[code], ensure_ascii=False) + "\n")


def find_video(code):
    for name in os.listdir(TMP_DIR):
        if name.startswith(code + ".") and not name.endswith((".part", ".ytdl")):
            return os.path.join(TMP_DIR, name)
    return None


def ffprobe_duration(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30,
        )
        return round(float(out.stdout.strip()), 2)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=2.2,
                        help="presupuesto de tiempo de esta tanda")
    parser.add_argument("--limit", type=int, default=10,
                        help="máximo de reels nuevos en esta tanda")
    parser.add_argument(
        "--model",
        default=os.path.join(BASE, "09_AUTOMATION", "models", "faster-whisper-small"),
    )
    parser.add_argument("--sleep", type=float, default=3.0)
    parser.add_argument("--cookies", default=None,
                        help="cookies.txt opcional para yt-dlp")
    parser.add_argument("--keep-video", action="store_true")
    parser.add_argument("--order", choices=["newest", "oldest", "views", "random"],
                        default="newest")
    parser.add_argument("--start", type=int, default=0,
                        help="índice inicial en la lista ordenada")
    args = parser.parse_args()

    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(TRANS_DIR, exist_ok=True)
    state = load_jsonl(STATE_PATH)
    meta = load_jsonl(META_PATH)
    with open(URLS_PATH, encoding="utf-8") as fh:
        urls = [line.strip() for line in fh if line.strip().startswith("https://")]
    codes = []
    for url in urls:
        code = url.rstrip("/").split("/")[-1]
        codes.append(code)

    if args.order == "newest":
        codes.sort(key=lambda c: (meta.get(c, {}).get("date_utc") or ""), reverse=True)
    elif args.order == "oldest":
        codes.sort(key=lambda c: (meta.get(c, {}).get("date_utc") or ""))
    elif args.order == "views":
        codes.sort(key=lambda c: (meta.get(c, {}).get("play_count") or 0), reverse=True)
    else:
        import random
        random.shuffle(codes)

    codes = codes[args.start:]
    # Saltar ya resueltos o con transcripción existente.
    pending = []
    for code in codes:
        st = state.get(code, {})
        if st.get("status") in ("transcribed", "no_speech", "skipped"):
            continue
        if os.path.exists(os.path.join(TRANS_DIR, f"{code}.json")):
            state.setdefault(code, {"code": code})["status"] = "transcribed"
            state[code]["transcript_path"] = f"02_TRANSCRIPTS/instagram/{code}.json"
            state[code]["processed_at"] = state[code].get("processed_at") or now()
            continue
        pending.append(code)

    save_state(state)
    log(f"Pendientes: {len(pending)} | estado previo: {len(state)} | modelo: {args.model}")

    if not pending:
        print("No queda nada pendiente.")
        return 0

    from faster_whisper import WhisperModel
    log("Cargando modelo faster-whisper...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    started = time.monotonic()
    processed = 0
    transcribed = 0
    no_speech = 0
    failed = 0
    rate_limited = 0
    consecutive_errors = 0

    for code in pending:
        if processed >= args.limit:
            break
        if time.monotonic() - started > args.minutes * 60:
            log("Presupuesto de tiempo agotado; se puede reanudar.")
            break
        url = f"https://www.instagram.com/reel/{code}/"
        video = find_video(code)
        st = state.setdefault(code, {"code": code})
        st["status"] = "downloading"
        st["url"] = url
        st["date_utc"] = (meta.get(code) or {}).get("date_utc")
        st["play_count"] = (meta.get(code) or {}).get("play_count")
        st["like_count"] = (meta.get(code) or {}).get("like_count")
        save_state(state)

        if not video:
            cmd = [
                sys.executable, "-m", "yt_dlp", "--no-playlist", "--no-warnings",
                "--sleep-requests", "2", "-f", "best[height<=720]/best",
                "-o", os.path.join(TMP_DIR, "%(id)s.%(ext)s"), url,
            ]
            if args.cookies:
                cmd += ["--cookies", args.cookies]
            try:
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            except subprocess.TimeoutExpired:
                st["status"] = "failed"
                st["error"] = "timeout de descarga"
                failed += 1
                consecutive_errors += 1
                save_state(state)
                log(f"{code}: timeout de descarga")
                continue
            text = (out.stdout or "") + (out.stderr or "")
            if any(x in text for x in ("429", "Too Many Requests", "login required",
                                       "Please wait a few minutes")):
                st["status"] = "rate_limited"
                st["error"] = text[-400:]
                rate_limited += 1
                save_state(state)
                log(f"{code}: límite de Instagram; paro la tanda.")
                break
            video = find_video(code)
            if not video:
                st["status"] = "failed"
                st["error"] = text[-400:]
                failed += 1
                # Un reel con restricción de audiencia es un fallo permanente
                # del propio contenido; si cuenta como fallo consecutivo, tres
                # de ellos al inicio del orden "newest" abortan todas las
                # tandas sin procesar nada. Se reintenta, pero no corta.
                audience_restricted = any(
                    x in text for x in ("isn't available to everyone",
                                        "not available to everyone",
                                        "can't be seen by certain audiences")
                )
                if audience_restricted:
                    log(f"{code}: restricción de audiencia (no corta la tanda)")
                else:
                    consecutive_errors += 1
                    log(f"{code}: descarga fallida")
                save_state(state)
                if consecutive_errors >= 3:
                    log("Tres fallos seguidos; paro la tanda.")
                    break
                continue

        consecutive_errors = 0
        duration = ffprobe_duration(video)
        st["duration_sec"] = duration
        st["status"] = "transcribing"
        save_state(state)

        try:
            segments, info = model.transcribe(
                video, language="es", vad_filter=True, beam_size=5
            )
            segs = [
                {"start": round(s.start, 2), "end": round(s.end, 2),
                 "text": s.text.strip()}
                for s in segments if s.text.strip()
            ]
            text = " ".join(s["text"] for s in segs).strip()
            payload = {
                "code": code,
                "date_utc": (meta.get(code) or {}).get("date_utc"),
                "duration_sec": duration,
                "language": info.language,
                "model": args.model,
                "text": text,
                "segments": segs,
                "transcribed_at": now(),
            }
            trans_path = os.path.join(TRANS_DIR, f"{code}.json")
            with open(trans_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            st["transcript_path"] = os.path.relpath(trans_path, BASE)
            st["chars"] = len(text)
            st["status"] = "transcribed" if text else "no_speech"
            st["processed_at"] = now()
            if text:
                transcribed += 1
                log(f"{code}: transcrito ({duration}s, {len(text)} chars)")
            else:
                no_speech += 1
                log(f"{code}: sin habla ({duration}s)")
        except Exception as exc:
            st["status"] = "failed"
            st["error"] = f"transcripción: {type(exc).__name__}: {exc}"[:500]
            failed += 1
            log(f"{code}: fallo de transcripción: {exc}")
        finally:
            if not args.keep_video:
                try:
                    os.remove(video)
                except OSError:
                    pass

        processed += 1
        save_state(state)
        time.sleep(args.sleep)

    remaining = sum(
        1 for code in codes
        if state.get(code, {}).get("status") not in ("transcribed", "no_speech", "skipped")
    )
    log(
        f"Tanda: procesados={processed} transcritos={transcribed} "
        f"sin_habla={no_speech} fallos={failed} rate_limited={rate_limited} "
        f"pendientes={remaining}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

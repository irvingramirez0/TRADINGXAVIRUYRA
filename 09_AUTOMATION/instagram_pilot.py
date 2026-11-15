#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Piloto de reels de Instagram para la base de Xavi Ruyra.

Objetivo:
- Catalogar los reels públicos de una cuenta (por defecto @xaviruyra).
- Descargar el vídeo de cada reel (opcional).
- Transcribirlo con faster-whisper (opcional).
- Medir solapamiento literal contra las transcripciones de YouTube ya
  almacenadas en `segments` y generar un informe en 10_REPORTS/.

No toca la base de conocimiento: solo escribe catálogo, vídeos, transcripciones
y un informe. La importación a `videos`/`evidence` se decide después de revisar
el informe.

Uso:
    python3 09_AUTOMATION/instagram_pilot.py --catalog --limit 50
    python3 09_AUTOMATION/instagram_pilot.py --catalog --limit 50 --cookies instagram_cookies.txt --download
    python3 09_AUTOMATION/instagram_pilot.py --transcribe
    python3 09_AUTOMATION/instagram_pilot.py --report

Requisitos:
    pip install --break-system-packages instaloader faster-whisper

Notas:
- Instagram limita agresivamente las peticiones anónimas (HTTP 429). El script
  duerme entre peticiones y se detiene con un mensaje claro si lo bloquean.
- Para cuentas que exigen sesión, exporta una sesión de Instaloader:
      python3 -m instaloader --login TU_USUARIO
  y pasa --sessionfile con la ruta del archivo generado.
- Los reels solo se pueden leer si son públicos. No se saltan restricciones.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import unicodedata
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
CATALOG = os.path.join(BASE, "01_CATALOG", "instagram_reels.jsonl")
MEDIA_DIR = os.path.join(BASE, "03_FRAMES", "videos", "instagram")
TRANS_DIR = os.path.join(BASE, "02_TRANSCRIPTS", "instagram")
REPORT_DIR = os.path.join(BASE, "10_REPORTS")
DEFAULT_PROFILE = "xaviruyra"

TRADING_TERMS = {
    "nq", "nasdaq", "es", "sp500", "futuros", "futures", "trade", "trading",
    "trader", "entrada", "stop", "target", "tp", "sl", "break", "even",
    "liquidez", "liquidity", "fvg", "ifvg", "imbalance", "ineficiencia",
    "dol", "bias", "po3", "amd", "judas", "manipulacion", "manipulation",
    "equilibrium", "equilibrio", "payout", "cuenta", "fondeo", "prop",
    "lucid", "fundednext", "myfunded", "takeprofit", "riesgo", "risk",
    "backtest", "backtesting", "sesion", "londres", "london", "asia",
    "premarket", "vela", "velas", "grafico", "chart", "mercado", "market",
    "swing", "high", "low", "bsl", "ssl", "smt", "cisd", "order", "block",
    "breaker", "rdr", "nwog", "ndog", "gann", "recap", "winrate", "win",
    "loss", "rr", "lotaje", "contrato", "micro", "mini",
}


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_dirs():
    for d in (os.path.dirname(CATALOG), MEDIA_DIR, TRANS_DIR, REPORT_DIR):
        os.makedirs(d, exist_ok=True)


def norm(text):
    text = unicodedata.normalize("NFKD", (text or "").lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9ñ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def read_catalog():
    rows = []
    if os.path.exists(CATALOG):
        with open(CATALOG, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def write_catalog(rows):
    with open(CATALOG, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def catalog_reels(profile_name, limit, download, sleep_sec, sessionfile, cookies_path=None):
    import instaloader
    from instaloader.exceptions import ConnectionException, ProfileNotExistsException

    loader = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=download,
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        dirname_pattern=os.path.join(MEDIA_DIR, "{profile}"),
        filename_pattern="{shortcode}",
    )
    try:
        loader.context.max_connection_attempts = 1
    except Exception:
        pass

    if sessionfile:
        try:
            loader.load_session_from_file(profile_name, sessionfile)
            print(f"Sesión cargada desde {sessionfile}")
        except Exception as exc:
            print(f"No se pudo cargar la sesión: {exc}")
            return 2

    if cookies_path:
        try:
            cookies = load_netscape_cookies(cookies_path, domain_filter="instagram.com")
            loader.context._session.cookies.update(cookies)
            loader.context._session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                ),
                "x-ig-app-id": "936619743392459",
                "x-asbd-id": "129477",
                "x-ig-www-claim": "0",
                "Referer": f"https://www.instagram.com/{profile_name}/reels/",
            })
            print(f"Cookies de Instagram cargadas en Instaloader: {len(cookies)}")
        except Exception as exc:
            print(f"No se pudieron cargar las cookies: {exc}")
            return 2

    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
    except ProfileNotExistsException:
        print(f"El perfil @{profile_name} no existe o no es público.")
        return 2
    except ConnectionException as exc:
        print(f"Instagram rechazó la petición: {exc}")
        print("Espera unos minutos y vuelve a intentarlo con menos --limit.")
        return 3

    rows = read_catalog()
    seen = {row.get("shortcode") for row in rows if row.get("shortcode")}
    try:
        for index, post in enumerate(profile.get_reels()):
            if limit and len(rows) >= limit:
                break
            node = post._node
            shortcode = post.shortcode
            if shortcode in seen:
                continue
            seen.add(shortcode)
            row = {
                "shortcode": shortcode,
                "profile": profile_name,
                "date_utc": post.date_utc.isoformat(),
                "caption": (post.caption or "").strip(),
                "typename": post.typename,
                "product_type": node.get("product_type"),
                "is_video": bool(post.is_video),
                "duration_sec": post.video_duration,
                "view_count": post.video_view_count,
                "like_count": post.likes,
                "permalink": f"https://www.instagram.com/reel/{shortcode}/",
                "cataloged_at": now_iso(),
                "downloaded": False,
            }
            if download:
                try:
                    loader.download_post(post, target=profile_name)
                    row["downloaded"] = True
                except Exception as exc:
                    row["download_error"] = str(exc)[:300]
                    print(f"  descarga fallida {shortcode}: {exc}")
            rows.append(row)
            print(f"[{len(rows)}] {row['date_utc'][:10]} {shortcode} "
                  f"{row['duration_sec']}s | {row['caption'][:60]!r}")
            if len(rows) % 5 == 0:
                write_catalog(rows)
            if sleep_sec:
                time.sleep(sleep_sec)
    except ConnectionException as exc:
        print(f"Instagram cortó la lista: {exc}")
        print("Se guarda lo catalogado hasta ahora.")
    except Exception as exc:
        print(f"Error inesperado durante el catálogo: {type(exc).__name__}: {exc}")
        print("Se guarda lo catalogado hasta ahora.")

    if rows:
        write_catalog(rows)
        print(f"Catálogo escrito: {CATALOG} ({len(rows)} reels)")
    else:
        print("No se catalogó ningún reel.")
    return 0 if rows else 1


def load_netscape_cookies(path, domain_filter=None):
    """Lee un cookies.txt en formato Netscape y devuelve {nombre: valor}.

    domain_filter permite quedarse solo con las cookies de un dominio, por
    ejemplo "instagram.com". Sin filtro, un export completo del navegador
    puede superar el límite de cabeceras de requests.
    """
    cookies = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#HttpOnly_"):
                line = line[len("#HttpOnly_"):]
            elif line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                parts = line.split()
            if len(parts) < 7:
                continue
            domain = parts[0]
            if domain_filter and domain_filter not in domain:
                continue
            cookies[parts[5]] = parts[6]
    return cookies


def download_video(session, url, path):
    if not url:
        return False, "sin video_url"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return True, "ya existía"
    try:
        with session.get(url, stream=True, timeout=90) as resp:
            resp.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        fh.write(chunk)
        return True, "descargado"
    except Exception as exc:
        return False, str(exc)[:250]


def catalog_reels_api(cookies_path, user_id, limit, download, sleep_sec):
    """Lee la pestaña de reels con la API web usando cookies de una sesión."""
    import requests

    cookies = load_netscape_cookies(cookies_path, domain_filter="instagram.com")
    if "sessionid" not in cookies:
        print("El cookies.txt no contiene 'sessionid' para instagram.com. "
              "Exporta las cookies con la sesión abierta.")
        return 2
    print(f"Cookies de Instagram cargadas: {len(cookies)}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "x-ig-app-id": "936619743392459",
        "Referer": f"https://www.instagram.com/{DEFAULT_PROFILE}/reels/",
        "X-Requested-With": "XMLHttpRequest",
    })
    session.cookies.update(cookies)
    if "csrftoken" in cookies:
        session.headers["x-csrftoken"] = cookies["csrftoken"]

    rows = read_catalog()
    seen = {row.get("shortcode") for row in rows if row.get("shortcode")}
    max_id = None
    page = 0
    while len(rows) < limit:
        page += 1
        data = {
            "target_user_id": str(user_id),
            "page_size": "12",
            "include_feed_video": "true",
        }
        if max_id:
            data["max_id"] = max_id
        try:
            resp = session.post(
                "https://www.instagram.com/api/v1/clips/user/",
                data=data,
                timeout=45,
            )
        except Exception as exc:
            print(f"Error de red en la página {page}: {exc}")
            break
        if resp.status_code != 200:
            print(f"HTTP {resp.status_code} en la página {page}: {resp.text[:200]}")
            break
        try:
            payload = resp.json()
        except Exception:
            print(f"Respuesta no JSON en la página {page}: {resp.text[:200]}")
            break

        items = payload.get("items") or []
        if not items:
            print("La API no devolvió items.")
            break

        for item in items:
            media = item.get("media", item)
            shortcode = media.get("code")
            if not shortcode or shortcode in seen:
                continue
            seen.add(shortcode)
            date_utc = None
            if media.get("taken_at"):
                date_utc = (
                    datetime.utcfromtimestamp(media["taken_at"]).isoformat() + "Z"
                )
            row = {
                "shortcode": shortcode,
                "profile": DEFAULT_PROFILE,
                "date_utc": date_utc,
                "caption": ((media.get("caption") or {}).get("text") or "").strip(),
                "typename": media.get("__typename"),
                "product_type": media.get("product_type"),
                "is_video": media.get("media_type") == 2,
                "duration_sec": media.get("video_duration"),
                "view_count": media.get("play_count") or media.get("view_count"),
                "like_count": media.get("like_count"),
                "permalink": f"https://www.instagram.com/reel/{shortcode}/",
                "cataloged_at": now_iso(),
                "downloaded": False,
                "source": "reels_tab",
            }
            if download:
                target_dir = os.path.join(MEDIA_DIR, DEFAULT_PROFILE)
                os.makedirs(target_dir, exist_ok=True)
                target = os.path.join(target_dir, f"{shortcode}.mp4")
                ok, note = download_video(session, media.get("video_url"), target)
                row["downloaded"] = ok
                if not ok:
                    row["download_error"] = note
            rows.append(row)
            print(
                f"[{len(rows)}] {(date_utc or '')[:10]} {shortcode} "
                f"{row['duration_sec']}s | {row['caption'][:60]!r}"
            )
            if len(rows) >= limit:
                break

        write_catalog(rows)
        print(f"  página {page}: {len(rows)} reels acumulados")
        paging = payload.get("paging_info") or {}
        max_id = paging.get("max_id")
        if not paging.get("more_available") or not max_id:
            break
        if sleep_sec:
            time.sleep(sleep_sec)

    if len(rows) > 0:
        write_catalog(rows)
        print(f"Catálogo escrito: {CATALOG} ({len(rows)} reels)")
    return 0 if rows else 1


def transcribe_all(model_size, language):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Falta faster-whisper. Instálalo con:")
        print("  pip install --break-system-packages faster-whisper")
        return 2

    videos = []
    for root, _, files in os.walk(MEDIA_DIR):
        for name in files:
            if name.lower().endswith((".mp4", ".mkv", ".webm", ".mov")):
                videos.append(os.path.join(root, name))
    if not videos:
        print(f"No hay vídeos en {MEDIA_DIR}. Ejecuta antes --catalog --download.")
        return 1

    print(f"Cargando modelo faster-whisper '{model_size}' (CPU, int8)...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    done = 0
    for path in sorted(videos):
        shortcode = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(TRANS_DIR, f"{shortcode}.json")
        if os.path.exists(out):
            print(f"  ya transcrito: {shortcode}")
            continue
        print(f"  transcribiendo {shortcode}...")
        segments, info = model.transcribe(
            path, language=language, vad_filter=True, beam_size=5
        )
        segs = [
            {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
            for s in segments
            if s.text.strip()
        ]
        payload = {
            "shortcode": shortcode,
            "source_path": os.path.relpath(path, BASE),
            "language": info.language,
            "duration_sec": round(info.duration, 2),
            "text": " ".join(s["text"] for s in segs).strip(),
            "segments": segs,
            "transcribed_at": now_iso(),
        }
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        done += 1
        print(f"    {len(segs)} segmentos, {payload['duration_sec']}s")
    print(f"Transcripciones nuevas: {done}. Carpeta: {TRANS_DIR}")
    return 0


def ngrams(text, n=5):
    words = norm(text).split()
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def load_corpus():
    con = sqlite3.connect(DB)
    try:
        text = " ".join(row[0] for row in con.execute("SELECT text FROM segments"))
    finally:
        con.close()
    return ngrams(text, 5), len(text.split())


def fts_matches(text, limit=5):
    con = sqlite3.connect(DB)
    try:
        terms = [w for w in norm(text).split() if len(w) > 4][:25]
        if not terms:
            return []
        query = " OR ".join(f'"{w}"' for w in dict.fromkeys(terms))
        rows = con.execute(
            "SELECT video_id, start_sec, text FROM segments_fts "
            "WHERE segments_fts MATCH ? LIMIT ?",
            (query, limit),
        ).fetchall()
        return [
            {"video_id": r[0], "start_sec": r[1], "text": (r[2] or "")[:220]}
            for r in rows
        ]
    except sqlite3.Error:
        return []
    finally:
        con.close()


def trading_hits(text):
    words = set(norm(text).split())
    return sorted(words & TRADING_TERMS)


def build_report():
    catalog = read_catalog()
    if not catalog:
        print("No hay catálogo. Ejecuta antes --catalog.")
        return 1
    corpus_ngrams, corpus_words = load_corpus()
    rows = []
    for item in catalog:
        shortcode = item["shortcode"]
        trans_path = os.path.join(TRANS_DIR, f"{shortcode}.json")
        text = ""
        if os.path.exists(trans_path):
            with open(trans_path, encoding="utf-8") as fh:
                text = json.load(fh).get("text", "")
        hits = trading_hits(text) if text else []
        reel_ngrams = ngrams(text, 5) if text else set()
        overlap = (
            round(100 * len(reel_ngrams & corpus_ngrams) / len(reel_ngrams), 1)
            if reel_ngrams else None
        )
        matches = fts_matches(text, 3) if text else []
        rows.append({
            **item,
            "transcript_chars": len(text),
            "trading_hits": hits,
            "literal_overlap_pct": overlap,
            "top_matches": matches,
        })

    date_tag = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(REPORT_DIR, f"instagram_pilot_{date_tag}.md")
    lines = [
        "# PILOTO DE REELS DE INSTAGRAM",
        "",
        f"**Fecha:** {date_tag}  ",
        f"**Perfil:** @{catalog[0].get('profile', DEFAULT_PROFILE)}  ",
        f"**Reels catalogados:** {len(rows)}  ",
        f"**Corpus de comparación:** {corpus_words:,} palabras en `segments`  ",
        "",
        "El solapamiento es literal (5-gramas Exactos). Un valor bajo no prueba que el "
        "contenido sea nuevo: puede ser una paráfrasis. Un valor alto sí indica repetición "
        "de frases ya presentes en YouTube.",
        "",
        "| Fecha | Shortcode | Dur. | Caption | Términos de trading | Solapamiento |",
        "|---|---|---:|---|---:|---:|",
    ]
    for row in rows:
        caption = (row.get("caption") or "").replace("|", "/")[:50]
        overlap = "s/d" if row["literal_overlap_pct"] is None else f"{row['literal_overlap_pct']}%"
        lines.append(
            f"| {row['date_utc'][:10]} | {row['shortcode']} | "
            f"{row.get('duration_sec') or 's/d'} | {caption} | "
            f"{len(row['trading_hits'])} | {overlap} |"
        )
    lines += ["", "## Detalle", ""]
    for row in rows:
        lines.append(f"### {row['shortcode']} — {row['date_utc'][:10]}")
        lines.append("")
        lines.append(f"- URL: {row['permalink']}")
        lines.append(f"- Caption: {(row.get('caption') or '(sin texto)')[:300]}")
        lines.append(f"- Duración: {row.get('duration_sec') or 's/d'} s")
        lines.append(f"- Términos de trading detectados: {', '.join(row['trading_hits']) or 'ninguno'}")
        lines.append(f"- Solapamiento literal con YouTube: "
                     f"{'s/d' if row['literal_overlap_pct'] is None else str(row['literal_overlap_pct']) + '%'}")
        if row["top_matches"]:
            lines.append("- Coincidencias más cercanas en la base:")
            for match in row["top_matches"]:
                lines.append(
                    f"  - `{match['video_id']}` {match['start_sec']}s — {match['text']}"
                )
        lines.append("")
    lines += [
        "## Lectura",
        "",
        "Este informe solo mide repetición literal y presencia de vocabulario. "
        "La decisión de importar un reel como evidencia requiere revisar su transcripción "
        "y comprobar si aporta una afirmación nueva, no solo una frase parecida.",
        "",
    ]
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"Informe escrito: {report_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Piloto de reels de Instagram.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--catalog", action="store_true")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--transcribe", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--sleep", type=float, default=8.0)
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="es")
    parser.add_argument("--sessionfile", default=None)
    parser.add_argument("--cookies", default=None,
                        help="cookies.txt en formato Netscape exportado del navegador")
    parser.add_argument("--user-id", default="77867812474",
                        help="ID numérico de Instagram del perfil")
    args = parser.parse_args()

    ensure_dirs()
    if not any([args.catalog, args.transcribe, args.report]):
        parser.print_help()
        return 1
    code = 0
    if args.catalog:
        if args.cookies:
            code = catalog_reels_api(
                args.cookies, args.user_id, args.limit, args.download, args.sleep
            )
            if code != 0:
                print("La API de reels no respondió; pruebo la ruta de Instaloader "
                      "con las mismas cookies...")
                code = catalog_reels(
                    args.profile, args.limit, args.download, args.sleep,
                    args.sessionfile, cookies_path=args.cookies
                )
        else:
            code = catalog_reels(
                args.profile, args.limit, args.download, args.sleep, args.sessionfile
            )
    if code == 0 and args.transcribe:
        code = transcribe_all(args.model, args.language)
    if code == 0 and args.report:
        code = build_report()
    return code


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Captura metadatos (fecha, caption, duración, métricas) de todos los reels de un
perfil usando la misma consulta GraphQL que la web de Instagram.

No descarga vídeos. Guarda un JSONL en 01_CATALOG/instagram_reels_meta.jsonl.
Se apoya en el navegador real y en la sesión exportada, porque la API directa
responde 429/302 desde el sandbox.

Uso:
    LD_LIBRARY_PATH=/tmp/chromelibs/usr/lib/x86_64-linux-gnu \
    python3 09_AUTOMATION/instagram_reels_metadata.py \
        --cookies www.instagram.com_cookies.txt --max-steps 130 --wait-ms 900
"""

import argparse
import json
import os
import sys
import urllib.parse
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_meta.jsonl")
REPORT_PATH = os.path.join(BASE, "10_REPORTS", "instagram_reels_metadata.txt")
DEFAULT_PROFILE = "xaviruyra"
DEFAULT_USER_ID = "77867812474"
PAGINATION_DOC_ID = "28937525862583478"


def load_cookie_dicts(path, domain_filter="instagram.com"):
    cookies = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
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
            domain, _flag, cpath, secure, expiry, name, value = parts[:7]
            if domain_filter and domain_filter not in domain:
                continue
            try:
                expires = int(expiry)
            except ValueError:
                expires = -1
            cookies.append({
                "name": name,
                "value": value,
                "domain": domain if domain.startswith(".") else "." + domain,
                "path": cpath or "/",
                "secure": secure.upper() == "TRUE",
                "expires": expires if expires > 0 else -1,
            })
    return cookies


def load_meta():
    meta = {}
    if os.path.exists(META_PATH):
        with open(META_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("code"):
                    meta[row["code"]] = row
    return meta


def save_meta(meta):
    os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
    with open(META_PATH, "w", encoding="utf-8") as fh:
        for code in sorted(meta):
            fh.write(json.dumps(meta[code], ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--user-id", default=DEFAULT_USER_ID)
    parser.add_argument("--cookies", required=True)
    parser.add_argument("--max-steps", type=int, default=130)
    parser.add_argument("--wait-ms", type=int, default=900)
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    cookies = load_cookie_dicts(args.cookies)
    meta = load_meta()
    print(f"Metadatos previos: {len(meta)}")
    pages = 0
    last_page_info = {}

    def handle_route(route):
        req = route.request
        if "api/graphql" in req.url and req.post_data:
            q = urllib.parse.parse_qs(req.post_data, keep_blank_values=True)
            if (q.get("doc_id") or [""])[0] == PAGINATION_DOC_ID:
                try:
                    variables = json.loads((q.get("variables") or ["{}"])[0])
                    variables["first"] = 50
                    variables.setdefault("data", {})["page_size"] = 50
                    q["variables"] = [json.dumps(variables, separators=(",", ":"))]
                    route.continue_(post_data=urllib.parse.urlencode(q, doseq=True))
                    return
                except Exception:
                    pass
        route.continue_()

    def on_response(resp):
        nonlocal pages, last_page_info
        if "api/graphql" not in resp.url:
            return
        try:
            data = resp.json()
        except Exception:
            return
        conn = ((data.get("data") or {}).get("fetch__XDTUserDict") or {}).get(
            "clips_connection"
        ) or {}
        edges = conn.get("edges") or []
        if not edges:
            return
        pages += 1
        new = 0
        for edge in edges:
            media = (edge.get("node") or {}).get("media") or {}
            code = media.get("code")
            if not code:
                continue
            caption = media.get("caption") or {}
            row = {
                "code": code,
                "pk": media.get("pk"),
                "taken_at": media.get("taken_at"),
                "date_utc": (
                    datetime.utcfromtimestamp(media["taken_at"]).isoformat() + "Z"
                    if media.get("taken_at")
                    else None
                ),
                "video_duration": media.get("video_duration"),
                "caption": (caption.get("text") if isinstance(caption, dict) else caption) or "",
                "like_count": media.get("like_count"),
                "play_count": media.get("play_count") or media.get("view_count"),
                "media_type": media.get("media_type"),
                "product_type": media.get("product_type"),
                "url": f"https://www.instagram.com/reel/{code}/",
            }
            if code not in meta:
                new += 1
            meta[code] = row
        page_info = conn.get("page_info") or {}
        if page_info:
            last_page_info = page_info
        if new:
            save_meta(meta)
        print(f"  página {pages}: +{new} -> {len(meta)} (has_next={page_info.get('has_next_page')})")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1366, "height": 900},
            locale="es-ES",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
        )
        context.add_cookies(cookies)
        page = context.new_page()
        page.route("**/api/graphql", handle_route)
        page.on("response", on_response)
        page.goto(
            f"https://www.instagram.com/{args.profile}/reels/",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(9000)

        for step in range(args.max_steps):
            page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight);"
                "if(document.scrollingElement)"
                " document.scrollingElement.scrollTop=document.scrollingElement.scrollHeight;"
            )
            page.wait_for_timeout(args.wait_ms)
            if not last_page_info.get("has_next_page", True):
                print("Última página alcanzada.")
                break

        browser.close()

    save_meta(meta)
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write("METADATOS DE REELS DE INSTAGRAM\n")
        fh.write(f"Fecha: {datetime.now().isoformat(timespec='seconds')}\n")
        fh.write(f"Perfil: @{args.profile} ({args.user_id})\n")
        fh.write(f"Reels con metadatos: {len(meta)}\n")
        fh.write(f"Páginas: {pages}\n")
        fh.write(f"Última página: {json.dumps(last_page_info, ensure_ascii=False)}\n")
    print(f"TOTAL metadatos: {len(meta)}")
    print(f"Archivo: {META_PATH}")
    return 0 if meta else 1


if __name__ == "__main__":
    sys.exit(main())

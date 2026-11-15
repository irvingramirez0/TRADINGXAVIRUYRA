#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Captura la lista completa de reels de un perfil usando un navegador real.

La página de Instagram carga los reels con la consulta GraphQL
`PolarisProfileReelsTabContentQuery_connection`. Este script abre la pestaña,
intercepta esa consulta para pedir más elementos por página, escucha las
respuestas y acumula los shortcodes. Guarda el progreso después de cada
respuesta, así que se puede cortar y volver a ejecutar sin perder lo obtenido.

Uso:
    LD_LIBRARY_PATH=/tmp/chromelibs/usr/lib/x86_64-linux-gnu \
    python3 09_AUTOMATION/instagram_reels_capture.py \
        --cookies www.instagram.com_cookies.txt \
        --max-steps 120 --wait-ms 1000

Salidas:
    - 01_CATALOG/instagram_reels_codes.txt  (un shortcode por línea)
    - reels_xaviruyra.txt                   (una URL por línea)
    - 10_REPORTS/instagram_reels_capture.txt (resumen de la ejecución)
"""

import argparse
import json
import os
import sys
import urllib.parse
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES_PATH = os.path.join(BASE, "01_CATALOG", "instagram_reels_codes.txt")
URLS_PATH = os.path.join(BASE, "reels_xaviruyra.txt")
REPORT_PATH = os.path.join(BASE, "10_REPORTS", "instagram_reels_capture.txt")
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


def load_codes():
    if not os.path.exists(CODES_PATH):
        return set()
    with open(CODES_PATH, encoding="utf-8") as fh:
        return {line.strip() for line in fh if line.strip()}


def save_codes(codes):
    os.makedirs(os.path.dirname(CODES_PATH), exist_ok=True)
    ordered = sorted(codes)
    with open(CODES_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(ordered) + ("\n" if ordered else ""))
    with open(URLS_PATH, "w", encoding="utf-8") as fh:
        for code in ordered:
            fh.write(f"https://www.instagram.com/reel/{code}/\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--user-id", default=DEFAULT_USER_ID)
    parser.add_argument("--cookies", required=True)
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--wait-ms", type=int, default=1000)
    parser.add_argument("--stable-limit", type=int, default=15)
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    cookies = load_cookie_dicts(args.cookies)
    if not any(c["name"] == "sessionid" for c in cookies):
        print("El archivo no contiene sessionid para instagram.com.")
        return 2

    codes = load_codes()
    print(f"Shortcodes previos: {len(codes)}")
    responses = []
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
        nonlocal last_page_info
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
        new = 0
        for edge in edges:
            media = (edge.get("node") or {}).get("media") or {}
            code = media.get("code")
            if code and code not in codes:
                codes.add(code)
                new += 1
        page_info = conn.get("page_info") or {}
        if page_info:
            last_page_info = page_info
        responses.append((resp.status, len(edges), new, page_info.get("has_next_page")))
        if new:
            save_codes(codes)
            print(f"  +{new} -> {len(codes)} reels (has_next={page_info.get('has_next_page')})")

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

        stable = 0
        for step in range(args.max_steps):
            before = len(codes)
            page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight);"
                "if(document.scrollingElement)"
                " document.scrollingElement.scrollTop=document.scrollingElement.scrollHeight;"
            )
            page.wait_for_timeout(args.wait_ms)
            if len(codes) == before:
                stable += 1
            else:
                stable = 0
            if step % 10 == 0:
                print(f"paso {step}: {len(codes)} reels, stable={stable}")
            if stable >= args.stable_limit:
                print(f"Sin novedades durante {stable} pasos; paro.")
                break

        browser.close()

    save_codes(codes)
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write("CAPTURA DE REELS DE INSTAGRAM\n")
        fh.write(f"Fecha: {datetime.now().isoformat(timespec='seconds')}\n")
        fh.write(f"Perfil: @{args.profile} ({args.user_id})\n")
        fh.write(f"Reels únicos: {len(codes)}\n")
        fh.write(f"Última página: {json.dumps(last_page_info, ensure_ascii=False)}\n")
        fh.write("Respuestas GraphQL:\n")
        for status, edges, new, more in responses[-30:]:
            fh.write(f"  {status} edges={edges} nuevos={new} has_next={more}\n")
    print(f"TOTAL: {len(codes)} reels")
    print(f"Lista: {URLS_PATH}")
    print(f"Informe: {REPORT_PATH}")
    return 0 if codes else 1


if __name__ == "__main__":
    sys.exit(main())

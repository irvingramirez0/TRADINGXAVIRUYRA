#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Piloto con navegador real para la pestaña de reels de Instagram.

Abre instagram.com/<perfil>/reels/ en Chromium headless con las cookies de una
sesión, deja que la página cargue su propio JavaScript, hace scroll sobre el
contenedor que realmente se desplaza y acumula los enlaces /reel/ que aparecen.

No sustituye al catálogo por API: sirve para comprobar qué ve un navegador real
y para sacar la lista de URLs cuando la API responde 429/302.

Uso:
    python3 09_AUTOMATION/instagram_browser_pilot.py \
        --cookies www.instagram.com_cookies.txt \
        --out reels_xaviruyra.txt

Requiere:
    pip install --break-system-packages playwright
    python3 -m playwright install chromium
"""

import argparse
import os
import re
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(BASE, "reels_xaviruyra.txt")
SCREENSHOT = "/tmp/instagram_reels.png"
HTML_DUMP = "/tmp/instagram_reels.html"


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="xaviruyra")
    parser.add_argument("--cookies", required=True)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--max-steps", type=int, default=80)
    parser.add_argument("--wait-ms", type=int, default=1800)
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    cookies = load_cookie_dicts(args.cookies)
    if not any(c["name"] == "sessionid" for c in cookies):
        print("El archivo no contiene sessionid para instagram.com.")
        return 2
    print(f"Cookies cargadas: {len(cookies)}")

    url = f"https://www.instagram.com/{args.profile}/reels/"
    api_log = []
    links = set()

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

        def on_response(resp):
            u = resp.url
            if "clips/user" in u or "/graphql" in u or "web_profile_info" in u:
                api_log.append(
                    (resp.status, resp.headers.get("content-type", ""), u[:160])
                )

        page.on("response", on_response)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as exc:
            print(f"No se pudo abrir la página: {exc}")
            browser.close()
            return 3
        page.wait_for_timeout(9000)

        print("URL final:", page.url)
        print("Título:", page.title())
        try:
            page.screenshot(path=SCREENSHOT, full_page=False)
            print("Captura:", SCREENSHOT)
        except Exception:
            pass

        login_wall = (
            "/accounts/login" in page.url
            or page.locator('input[name="username"]').count() > 0
        )
        if login_wall:
            print("La página muestra el muro de login: la sesión no es válida aquí.")

        stable = 0
        last_count = 0
        for step in range(args.max_steps):
            try:
                hrefs = page.eval_on_selector_all(
                    'a[href*="/reel/"]',
                    "els => els.map(e => e.href.split('?')[0])",
                )
            except Exception:
                hrefs = []
            for href in hrefs:
                if "/reel/" in href:
                    links.add(href)
            before = len(links)

            try:
                scroll_info = page.evaluate(
                    """() => {
                        const els = [...document.querySelectorAll('*')]
                          .filter(e => e.scrollHeight > e.clientHeight + 300);
                        els.sort((a, b) => b.scrollHeight - a.scrollHeight);
                        const el = els[0];
                        if (el) {
                            el.scrollTop = el.scrollHeight;
                            return {tag: el.tagName, cls: String(el.className || '').slice(0, 50),
                                    sh: el.scrollHeight, ch: el.clientHeight};
                        }
                        window.scrollTo(0, document.body.scrollHeight);
                        return {tag: 'window', sh: document.body.scrollHeight,
                                ch: window.innerHeight};
                    }"""
                )
            except Exception:
                scroll_info = {}

            page.wait_for_timeout(args.wait_ms)
            if len(links) == before:
                stable += 1
            else:
                stable = 0
            if step % 10 == 0 or len(links) != last_count:
                print(f"  paso {step}: {len(links)} reels | scroll {scroll_info}")
                last_count = len(links)
            if stable >= 10:
                break

        try:
            with open(HTML_DUMP, "w", encoding="utf-8") as fh:
                fh.write(page.content())
        except Exception:
            pass

        browser.close()

    text = "\n".join(sorted(links))
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(text + ("\n" if text else ""))

    print(f"Total de URLs únicas: {len(links)}")
    print(f"Lista escrita en: {args.out}")
    print("Últimas llamadas API observadas:")
    for status, ctype, u in api_log[-15:]:
        print(f"  {status} | {ctype[:30]} | {u}")
    return 0 if links else 1


if __name__ == "__main__":
    sys.exit(main())

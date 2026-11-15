#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba la integridad del vault generado.

- Frontmatter obligatorio: tipo, confianza, estado, video, timestamp.
- Todos los enlaces [[...]] apuntan a una nota existente.
- Todas las imágenes incrustadas existen.
- Recuento por tipo de nota.

Uso: python 09_AUTOMATION/verificar_vault.py
"""

import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT = os.path.join(BASE, "12_VAULT")
REQUIRED = ("tipo", "confianza", "estado", "video", "timestamp")


def notas():
    out = {}
    for root, _, files in os.walk(VAULT):
        if ".obsidian" in root:
            continue
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            out[os.path.splitext(name)[0]] = path
    return out


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    data = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def main():
    index = notas()
    links_bad = []
    images_bad = []
    fm_bad = []
    counts = {}
    for stem, path in index.items():
        rel = os.path.relpath(path, VAULT)
        if rel in ("LEEME.md",):
            continue
        text = open(path, encoding="utf-8").read()
        fm = frontmatter(text)
        # Ignorar el contenido de código en línea y bloques: ahí puede haber
        # ejemplos literales de enlaces.
        sin_codigo = re.sub(r"`[^`]*`", "", text)
        sin_codigo = re.sub(r"```.*?```", "", sin_codigo, flags=re.S)
        tipo = fm.get("tipo", "")
        if tipo in ("concepto", "regla", "operacion", "cambio", "pregunta"):
            counts[tipo] = counts.get(tipo, 0) + 1
            for key in REQUIRED:
                if key not in fm:
                    fm_bad.append((rel, key))
        for target in re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", sin_codigo):
            t = os.path.splitext(os.path.basename(target.strip()))[0]
            if t not in index:
                links_bad.append((rel, target))
        for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", sin_codigo):
            if img.startswith("http"):
                continue
            p = os.path.normpath(os.path.join(os.path.dirname(path), img))
            if not os.path.exists(p):
                images_bad.append((rel, img))

    print("Notas:", len(index))
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print("Frontmatter incompleto:", len(fm_bad))
    for x in fm_bad[:10]:
        print("  ", x)
    print("Enlaces rotos:", len(links_bad))
    for x in links_bad[:20]:
        print("  ", x)
    print("Imágenes rotas:", len(images_bad))
    for x in images_bad[:20]:
        print("  ", x)
    return 1 if (fm_bad or links_bad or images_bad) else 0


if __name__ == "__main__":
    sys.exit(main())

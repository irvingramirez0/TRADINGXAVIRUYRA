#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenera el sitio y lo publica cuando hay algo nuevo, sin intervención.

Por qué existe
--------------
La tarea diaria de Claude Desktop transcribía la clase nueva, pero el sitio no
se enteraba: `12_VAULT/` se regenera a mano y el deploy lo dispara un push. Una
clase podía estar transcrita días y seguir sin aparecer.

Qué hace, en este orden
-----------------------
1. Comprueba que no haya cambios a medias en el repositorio (`git status`).
   Si los hay, **para**: mezclar tu trabajo en curso con una publicación
   automática es la forma más fácil de subir algo que no querías.
2. Regenera el vault desde SQLite.
3. Verifica el vault (enlaces, imágenes, frontmatter).
4. Si `git diff 12_VAULT` está vacío, termina sin hacer nada: no hay
   publicación que hacer y no se crea un commit vacío cada día.
5. Compila el sitio en local. Si el build falla, no se publica nada.
6. Hace commit solo de lo que cambió dentro de `12_VAULT/` y `public/` no se
   toca (lo compila CI), y hace push.

Qué NO hace
-----------
- No extrae conceptos ni reglas de una transcripción: eso es leer y decidir,
  y un heurístico ahí sería inventar. Si la clase nueva solo está transcrita,
  la página dirá «transcrita, sin trabajar» y el commit lo reflejará así.
- No toca archivos fuera de `12_VAULT/`. Los scripts y este documento se
  commitean a mano.

Uso
---
    python 09_AUTOMATION/publicar_sitio.py            # regenerar y publicar
    python 09_AUTOMATION/publicar_sitio.py --simular  # dice qué haría
    python 09_AUTOMATION/publicar_sitio.py --forzar   # ignora cambios locales
"""

import argparse
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT = "12_VAULT"
QUARTZ = os.path.join(BASE, "13_SITE", "quartz")


def correr(cmd, cwd=BASE, timeout=1800):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        timeout=timeout, encoding="utf-8", errors="replace",
    )


def git(*args, **kw):
    return correr(["git", *args], **kw)


def hay_cambios_fuera_del_vault():
    """Archivos modificados que no son el vault generado.

    El vault cambia en cada regeneración y es el objeto de esta publicación.
    Cualquier otra cosa modificada es trabajo en curso de una persona.
    """
    r = git("status", "--porcelain")
    if r.returncode != 0:
        return []
    ajenos = []
    for linea in r.stdout.splitlines():
        if len(linea) < 4:
            continue
        ruta = linea[3:].strip()
        # `12_VAULT/` y el directorio de salida del build son esperados.
        if ruta.startswith(VAULT + "/") or ruta.startswith("13_SITE/quartz/public"):
            continue
        ajenos.append(ruta)
    return ajenos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true", help="No escribe ni publica")
    ap.add_argument("--forzar", action="store_true",
                    help="Publica aunque haya cambios locales en otros archivos")
    ap.add_argument("--sin-build", action="store_true",
                    help="No compila en local (CI lo hará); útil si falta npm")
    args = ap.parse_args()

    ajenos = hay_cambios_fuera_del_vault()
    if ajenos and not args.forzar:
        print("Hay cambios locales fuera del vault. No se publica nada:")
        for a in ajenos[:20]:
            print(f"  {a}")
        print("\nCommitea o descarta esos cambios, o usa --forzar.")
        return 3

    python = [sys.executable, "-I"]
    print("=== Regenerando el vault ===")
    r = correr(python + [os.path.join(BASE, "09_AUTOMATION", "regenerar_vault.py")])
    if r.returncode != 0:
        print("FALLO al regenerar:")
        print((r.stderr or r.stdout)[-1500:])
        return 1

    print("=== Verificando el vault ===")
    r = correr(python + [os.path.join(BASE, "09_AUTOMATION", "verificar_vault.py")])
    if r.returncode != 0:
        print("FALLO en la verificación:")
        print((r.stdout or r.stderr)[-1500:])
        return 1

    diff = git("status", "--porcelain", VAULT)
    cambiados = [l for l in diff.stdout.splitlines() if l.strip()]
    if not cambiados:
        print("El vault no cambió. No hay nada que publicar.")
        return 0
    print(f"El vault cambió en {len(cambiados)} archivo(s).")

    if args.sin_build:
        print("(--sin-build: se salta el build local; lo hará CI)")
    else:
        print("=== Compilando el sitio en local ===")
        r = correr(
            ["node", "./quartz/bootstrap-cli.mjs", "build",
             "-d", "../../12_VAULT", "-o", "public"],
            cwd=QUARTZ, timeout=900,
        )
        if r.returncode != 0:
            # No se publica un sitio que no compila: el deploy de GitHub
            # Actions fallaría igual, pero entonces el error queda en un log
            # remoto y el repositorio ya tendría el commit.
            print("FALLO al compilar. No se publica:")
            print((r.stderr or r.stdout)[-2000:])
            return 1
        print("Build correcto.")

    resumen = []
    for linea in cambiados:
        estado, ruta = linea[:2].strip(), linea[3:].strip()
        resumen.append(f"{estado or 'M'} {ruta}")

    if args.simular:
        print("\n(--simular) Se habría publicado:")
        for l in resumen[:40]:
            print("  " + l)
        return 0

    print("=== Publicando ===")
    for paso in (["add", VAULT], ["commit", "-m", mensaje_commit(cambiados)]):
        r = git(*paso)
        if r.returncode != 0:
            print(f"FALLO en git {paso[0]}:")
            print((r.stderr or r.stdout)[-800:])
            return 1
    r = git("push", "origin", "HEAD")
    if r.returncode != 0:
        print("FALLO al hacer push:")
        print((r.stderr or r.stdout)[-800:])
        return 1
    print("Publicado. GitHub Actions compilará y desplegará.")
    return 0


def mensaje_commit(cambiados):
    """Mensaje con lo que de verdad cambió, no una plantilla fija."""
    notas = []
    nuevos = [l for l in cambiados if l.startswith("??") or l[:2].strip() == "A"]
    if nuevos:
        notas.append(f"{len(nuevos)} archivo(s) nuevo(s)")
    if not notas:
        notas.append(f"{len(cambiados)} archivo(s) actualizado(s)")
    return (
        "Publicar el sitio con el estado actual de la base\n\n"
        "Regenerado con 09_AUTOMATION/publicar_sitio.py tras verificar el vault.\n"
        + "; ".join(notas)
        + "\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>"
    )


if __name__ == "__main__":
    sys.exit(main())

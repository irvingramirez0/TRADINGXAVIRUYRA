#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Informe de cobertura de fotogramas (Fase 0f).

Genera un Markdown **automático** en
`10_REPORTS/FECHA_cobertura_fotogramas_auto.md`. El informe definitivo con
lectura e interpretación es `FECHA_cobertura_fotogramas_final.md`, escrito a
mano: este script no lo sobrescribe.
  - totales por categoría y por vídeo;
  - fotogramas extraídos y anotados de verdad (prosa en `description`);
  - fotogramas nuevos «pendiente de anotación»;
  - vídeos sin fotogramas, con pocos y no disponibles;
  - prioridad pendiente (bootcamp → operaciones → educativos → resto).

Uso:
    python 09_AUTOMATION/reporte_cobertura.py
"""

import os
import sqlite3
from collections import Counter, defaultdict
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
OUT = os.path.join(BASE, "10_REPORTS", f"{date.today().isoformat()}_cobertura_fotogramas_auto.md")

SKIP = {"keyword", "periodic", "scene", "frame de contexto"}
PENDIENTE = "pendiente de anotaci"


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def es_anotado(desc):
    d = (desc or "").strip().lower()
    return bool(d) and d not in SKIP and not d.startswith(PENDIENTE) and not d.startswith("frame de contexto")


def grupo(row, con):
    if row["category"] == "BOOTCAMP":
        return 1
    tr = con.execute("SELECT COUNT(*) FROM trades WHERE video_id=?", (row["id"],)).fetchone()[0]
    if tr:
        return 2
    if row["category"] in ("EDUCATIONAL", "TRADE_RECAP"):
        return 3
    return 4


def main():
    con = connect()
    rows = con.execute(
        """SELECT v.id, v.title, v.category, v.duration_sec, v.status, v.upload_date,
                  (SELECT COUNT(*) FROM segments s WHERE s.video_id=v.id) segs,
                  (SELECT COUNT(*) FROM frames f WHERE f.video_id=v.id) fr,
                  (SELECT COUNT(*) FROM frames f WHERE f.video_id=v.id
                     AND f.description IS NOT NULL
                     AND lower(f.description) NOT IN ('keyword','periodic','scene','frame de contexto')
                     AND f.description NOT LIKE 'pendiente de anotaci%'
                     AND f.description NOT LIKE 'frame de contexto%') anot,
                  (SELECT COUNT(*) FROM frames f WHERE f.video_id=v.id
                     AND f.description LIKE 'pendiente de anotaci%') pend
           FROM videos v WHERE v.in_scope=1 AND EXISTS
             (SELECT 1 FROM segments s WHERE s.video_id=v.id)
           ORDER BY v.upload_date"""
    ).fetchall()

    total = len(rows)
    con_fr = [r for r in rows if r["fr"] > 0]
    sin_fr = [r for r in rows if r["fr"] == 0]
    no_disp = [r for r in rows if r["status"] == "no_disponible"]
    pendientes = [r for r in rows if r["fr"] == 0 and r["status"] != "no_disponible"]

    frames_total = sum(r["fr"] for r in rows)
    frames_anot = sum(r["anot"] for r in rows)
    frames_pend = sum(r["pend"] for r in rows)

    porcat = defaultdict(lambda: {"videos": 0, "con": 0, "anot": 0, "sin": 0, "no_disp": 0})
    for r in rows:
        d = porcat[r["category"]]
        d["videos"] += 1
        d["con"] += 1 if r["fr"] else 0
        d["anot"] += r["anot"]
        d["sin"] += 1 if (not r["fr"] and r["status"] != "no_disponible") else 0
        d["no_disp"] += 1 if r["status"] == "no_disponible" else 0

    L = []
    L.append("# INFORME DE COBERTURA DE FOTOGRAMAS — FASE 0f")
    L.append("")
    L.append(f"**Fecha:** {date.today().isoformat()}")
    L.append("**Base:** `07_KNOWLEDGE_BASE/xavi_ruyra.db`")
    L.append("**Alcance:** vídeos con `in_scope=1` y transcripción indexada.")
    L.append("**Criterio de anotación:** solo cuenta como anotado el fotograma con prosa")
    L.append("descriptiva en `description`; los valores `keyword`, `periodic`, `scene` y")
    L.append("`frame de contexto` no son anotación. Los nuevos llevan el prefijo")
    L.append("`pendiente de anotación`.")
    L.append("")
    L.append("## 1. Totales")
    L.append("")
    L.append("| Métrica | Valor |")
    L.append("|---|---:|")
    L.append(f"| Vídeos con transcripción | {total} |")
    L.append(f"| Vídeos con fotogramas | {len(con_fr)} |")
    L.append(f"| Vídeos sin fotogramas (pendientes) | {len(pendientes)} |")
    L.append(f"| Vídeos no disponibles en YouTube | {len(no_disp)} |")
    L.append(f"| Fotogramas totales | {frames_total} |")
    L.append(f"| Fotogramas anotados | {frames_anot} |")
    L.append(f"| Fotogramas pendientes de anotación | {frames_pend} |")
    L.append("")
    L.append("## 2. Por categoría")
    L.append("")
    L.append("| Categoría | Vídeos | Con frames | Frames anotados | Pendientes | No disponibles |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for cat, d in sorted(porcat.items(), key=lambda x: -x[1]["videos"]):
        L.append(f"| {cat} | {d['videos']} | {d['con']} | {d['anot']} | {d['sin']} | {d['no_disp']} |")
    L.append("")
    L.append("## 3. Vídeos con fotogramas")
    L.append("")
    L.append("| Vídeo | Cat. | Duración | Frames | Anotados | Pendientes | frames/min |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    for r in sorted(con_fr, key=lambda x: -(x["fr"] or 0)):
        dur = r["duration_sec"] or 1
        L.append(f"| `{r['id']}` | {r['category']} | {dur//60}:{dur%60:02d} | {r['fr']} | "
                 f"{r['anot']} | {r['pend']} | {r['fr']/(dur/60):.2f} |")
    L.append("")
    L.append("## 4. Vídeos sin fotogramas")
    L.append("")
    L.append("### 4.1 No disponibles en YouTube (no se pueden cubrir)")
    L.append("")
    for r in no_disp:
        L.append(f"- `{r['id']}` — {r['category']} — {r['title']}")
    L.append("")
    L.append("### 4.2 Pendientes de procesar")
    L.append("")
    L.append("| Grupo | Vídeos | Horas |")
    L.append("|---|---:|---:|")
    gcount = Counter()
    ghours = defaultdict(float)
    for r in pendientes:
        g = grupo(r, con)
        gcount[g] += 1
        ghours[g] += (r["duration_sec"] or 0) / 3600
    for g in sorted(gcount):
        L.append(f"| {g} | {gcount[g]} | {ghours[g]:.2f} |")
    L.append("")
    L.append("| Vídeo | Cat. | Grupo | Duración | Título |")
    L.append("|---|---|---:|---:|---|")
    for r in sorted(pendientes, key=lambda x: (grupo(x, con), x["upload_date"] or "")):
        dur = r["duration_sec"] or 0
        L.append(f"| `{r['id']}` | {r['category']} | {grupo(r, con)} | {dur//60}:{dur%60:02d} | {r['title']} |")
    L.append("")
    L.append("## 5. Notas")
    L.append("")
    L.append("- Los 9 vídeos `no_disponible` respondieron «This video is not available» en la")
    L.append("  comprobación con yt-dlp del 2026-11-14. No se pueden extraer fotogramas.")
    L.append("- Los fotogramas nuevos se han guardado en `03_FRAMES/<video>/` y en la tabla")
    L.append("  `frames` con `description = 'pendiente de anotación | concepto: … | motivo: …'`.")
    L.append("  No se ha inventado ninguna anotación.")
    L.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"Informe: {OUT}")
    print(f"Vídeos: {total} | con frames: {len(con_fr)} | sin frames: {len(pendientes)} | "
          f"no disponibles: {len(no_disp)}")
    print(f"Frames: {frames_total} | anotados: {frames_anot} | pendientes: {frames_pend}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

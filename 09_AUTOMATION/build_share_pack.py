#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenera el pack para NotebookLM/GPT desde documentos y SQLite.

Uso desde la raíz del proyecto:
    python3 09_AUTOMATION/build_share_pack.py

Actualiza las fuentes metodológicas 01–04, la tabla de evidencias, las cifras
principales del README y el ZIP distribuible. No incluye transcripciones, frames
ni la base SQLite.
"""

from __future__ import annotations

import re
import sqlite3
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = ROOT / "05_METHODOLOGY"
SHARE = ROOT / "11_COMPARTIR"
PACK = SHARE / "PACK_FUENTES"
DB = ROOT / "07_KNOWLEDGE_BASE" / "xavi_ruyra.db"
ZIP_PATH = SHARE / "XAVI_RUYRA_KIT_2026-11-02.zip"

SOURCE_GROUPS = {
    "02_EVOLUCION.md": ["10_EVOLUCION.md"],
    "03_PREGUNTAS_ABIERTAS.md": ["11_PREGUNTAS_ABIERTAS.md"],
    "04_INVENTARIO_CONCEPTOS.md": ["12_INVENTARIO_CONCEPTOS.md"],
}
METHODOLOGY_FILES = [
    "00_MAPA_METODOLOGIA.md",
    "01_LIQUIDEZ_BSL_SSL.md",
    "02_FVG_IFVG.md",
    "03_DOL_BIAS.md",
    "04_PO3_AMD.md",
    "05_ENTRADAS.md",
    "06_EQUILIBRIO.md",
    "07_GESTION_RIESGO.md",
    "08_PSICOLOGIA_ERRORES.md",
    "09_PROCESO_ANALISIS.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def format_timestamp(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    total = int(float(seconds))
    return f"{total // 60}:{total % 60:02d}"


def escape_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def assemble_methodology() -> str:
    preamble = """# METODOLOGÍA DE XAVI RUYRA — DOCUMENTO DE ESTUDIO

**Versión del pack:** 2026-11-02.
**Qué es:** reconstrucción documentada de la metodología que Xavi Ruyra usa y enseña, con fuentes de vídeo y timestamps.
**Qué no es:** un curso oficial, un curso de ICT genérico ni asesoramiento financiero. Es una base de consulta privada para estudio.

Las rutas internas que aparecen en algunos documentos (`03_FRAMES/...`, `07_KNOWLEDGE_BASE/...`) se conservan para trazabilidad del proyecto original; no son necesarias para consultar este pack.

---"""
    documents = [read_text(METHODOLOGY / name).rstrip() for name in METHODOLOGY_FILES]
    return preamble + "\n\n" + "\n\n---\n\n".join(documents) + "\n"


def assemble_evidence() -> tuple[str, int, int, int]:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """SELECT e.id, e.entity_type, e.entity_id, e.video_id, e.timestamp_sec,
                  e.quote, e.source_type, e.frame_id, e.notes,
                  c.name AS concept_name, r.name AS rule_name,
                  v.url
           FROM evidence e
           LEFT JOIN concepts c ON e.entity_type='concept' AND c.id=e.entity_id
           LEFT JOIN rules r ON e.entity_type='rule' AND r.id=e.entity_id
           LEFT JOIN videos v ON v.id=e.video_id
           ORDER BY CASE e.entity_type WHEN 'concept' THEN 1 WHEN 'rule' THEN 2 ELSE 3 END,
                    e.entity_id, e.id"""
    ).fetchall()
    linked = sum(row["frame_id"] is not None for row in rows)
    unlinked = len(rows) - linked

    lines = [
        "# TABLA DE EVIDENCIAS",
        "",
        f"**Qué contiene:** las {len(rows)} evidencias de conceptos, reglas y operaciones. Cada fila incluye vídeo, timestamp, cita, certeza y una nota de alcance cuando la fuente solo apoya una parte o introduce una tensión.",
        "",
        "**Cómo se usa:** si una respuesta no tiene una fila aquí, no está confirmada. No se debe completar con conocimiento externo.",
        "",
        "**Tipos:** `EXPLICITO` = él lo dice; `OBSERVADO` = se deduce de lo que muestra; `INFERIDO` = reconstrucción propia (no debería usarse como cita); `NO CONFIRMADO` = pendiente.",
        "",
        "| ID | Entidad | Tipo | Vídeo | Timestamp | Cita | Certeza | Alcance / nota | ¿Fotograma? |",
        "|---:|---|---|---|---:|---|---|---|---|",
    ]
    type_labels = {"concept": "concepto", "rule": "regla", "trade": "operación"}
    for row in rows:
        kind = type_labels.get(row["entity_type"], row["entity_type"])
        if row["entity_type"] == "concept":
            entity = row["concept_name"] or f"Concepto {row['entity_id']}"
        elif row["entity_type"] == "rule":
            entity = row["rule_name"] or f"Regla {row['entity_id']}"
        else:
            entity = f"Operación {row['entity_id']}"
        video = f"`{row['video_id']}`"
        if row["url"]:
            video = f"[`{row['video_id']}`]({row['url']})"
        frame = "sí" if row["frame_id"] is not None else "no"
        values = [
            row["id"], entity, kind, video, format_timestamp(row["timestamp_sec"]),
            row["quote"] or "—", row["source_type"] or "—", row["notes"] or "—", frame,
        ]
        # The video cell already contains Markdown formatting and should stay intact.
        cells = [escape_cell(v) for v in values]
        cells[3] = video
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend([
        "",
        "---",
        "",
        f"**Enlaces visuales:** {linked} evidencias tienen un fotograma asociado; {unlinked} se apoyan solo en transcripción. La columna indica que existe una captura en el proyecto original; el pack no incluye las imágenes.",
        "",
        "**Nota:** las citas son extractos cortos o paráfrasis de la transcripción automática. No sustituyen al vídeo original; la fuente última es el vídeo enlazado por su ID.",
    ])
    con.close()
    return "\n".join(lines) + "\n", len(rows), linked, unlinked


def update_share_readme(segment_count: int, frame_count: int, evidence_count: int) -> None:
    path = SHARE / "README.md"
    text = read_text(path)
    text = re.sub(
        r"sin exponer (?:las|los) [\d.]+ (?:transcripciones|segmentos de transcripción) ni los [\d.]+ fotogramas",
        f"sin exponer las transcripciones crudas ni los {frame_count:,} fotogramas".replace(",", "."),
        text,
    )
    text = re.sub(r"\| `PACK_FUENTES/06_EVIDENCIAS\.md` \| Las \d+ evidencias", f"| `PACK_FUENTES/06_EVIDENCIAS.md` | Las {evidence_count} evidencias", text)
    text = text.replace(
        "3. Se actualizan los documentos 00–12.\n4. Se vuelve a ejecutar el generador del pack.\n5. En NotebookLM, se sustituyen las fuentes modificadas; en el GPT, se actualiza el conocimiento.\n6. Se avisa a los compas de la versión nueva.",
        "3. Se actualizan los documentos 00–12.\n4. Se ejecuta `python3 09_AUTOMATION/build_share_pack.py` para regenerar las fuentes y el ZIP.\n5. En NotebookLM, se sustituyen las fuentes modificadas; en el GPT, se actualiza el conocimiento.\n6. Se avisa a los compas de la versión nueva.",
    )
    write_text(path, text)


def main() -> None:
    PACK.mkdir(parents=True, exist_ok=True)
    write_text(PACK / "01_METODOLOGIA.md", assemble_methodology())
    for destination, sources in SOURCE_GROUPS.items():
        content = "\n\n---\n\n".join(read_text(METHODOLOGY / name).rstrip() for name in sources)
        write_text(PACK / destination, content)

    evidence_text, evidence_count, linked, unlinked = assemble_evidence()
    write_text(PACK / "06_EVIDENCIAS.md", evidence_text)

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    segments = con.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
    frame_count = con.execute("SELECT COUNT(*) FROM frames").fetchone()[0]
    con.close()
    update_share_readme(segments, frame_count, evidence_count)

    files = [p for p in SHARE.rglob("*") if p.is_file() and p != ZIP_PATH and ".zip" not in p.suffix.lower()]
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT))

    print(f"Fuentes del pack regeneradas: 01–04 y 06; evidencias={evidence_count} ({linked} con frame, {unlinked} sin frame).")
    print(f"README sincronizado: {segments} segmentos; {frame_count} fotogramas.")
    print(f"ZIP actualizado: {ZIP_PATH}")


if __name__ == "__main__":
    main()

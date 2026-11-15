# LEEME — vault generado

Esta carpeta es un **vault de Obsidian** y la fuente del sitio Quartz. Se
regenera entera desde `07_KNOWLEDGE_BASE/xavi_ruyra.db`:

```bash
python 09_AUTOMATION/regenerar_vault.py
```

- `conceptos/`, `reglas/`, `operaciones/`, `cambios/`, `preguntas/`: notas.
- `media/`: solo los fotogramas elegidos (1–3 por concepto), en WebP y con
  ancho máximo de 1200 px. Se limpia y reconstruye en cada ejecución.
- `index.md`: portada con la fecha de corte y el aviso de proyecto no oficial.

Reglas de contenido:

- No se copian transcripciones completas ni Reels de Instagram.
- Las operaciones llevan el aviso «P&L autodeclarado, no auditado».
- La confianza de cada nota es explícito / observado / inferido / no confirmado.
- Los enlaces `[[...]]` son la estructura del grafo: regla → concepto,
  concepto → concepto, regla nueva → regla obsoleta, operación → regla.

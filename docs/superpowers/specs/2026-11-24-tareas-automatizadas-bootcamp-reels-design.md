# Especificación: tareas automatizadas diarias (bootcamp + reels) — diseño

**Fecha:** 2026-11-24
**Estado:** DESIGN — pendiente de revisión del usuario. No se ha implementado todavía.
**Alcance:** `TRADINGXAVIRUYRA`. Dos tareas programadas de Claude Desktop, pipeline de ingesta, publicación del sitio y confiabilidad.

---

## 1. Problema y decisión

El usuario sospechó que la IA de desarrollo anterior no entendió lo que quería. La auditoría confirma que la sospecha es correcta en tres puntos concretos:

1. **El prompt diario del bootcamp está incompleto.** El texto pegado en Claude Desktop termina en "extraer y reindexar". No publica, no audita la web y no formula preguntas, aunque el usuario pidió las tres cosas (2026-11-16, mensajes duplicados; conclusions de Honcho `J-PesE6coJnfSt0MK7lwb`, `JtIgmNwm137atJ0rOsls3`, `sqQnh8KNtXA6ktfhQTJVg`).
2. **La segunda tarea es de reels de Instagram, no otro bootcamp.** El usuario lo aclaró el 2026-11-24: debe transcribir reels, extraer solo lo importante, ignorar humor/estilo de vida, procesar solo los últimos 6 meses y hacerlo en lotes pequeños diarios. El texto literal de esa tarea no está en disco ni en el historial recuperable; habrá que pedirlo al usuario antes de reemplazarla (ver §8, riesgo R1).
3. **La documentación contradice el estado real.** `13_SITE/README.md` decía «Sin publicar» y describía un flag `--publicar` retirado en `914da32`; `CICLO_DE_UNA_CLASE.md` dice que faltan evidencias en los días 1, 3 y 21 y la base actual muestra 29 clases, todas con evidencia. Dos líneas del README ya se corrigieron el 2026-11-24; el resto se corrige en la implementación.

### Decisiones del usuario (2026-11-24, preguntas respondidas)

| # | Decisión |
|---|---|
| D1 | Con capítulo nuevo: **auditar, mejorar y verificar** el sitio; no solo publicar. |
| D2 | Publicación **automática al final del ciclo**, con `publicar_sitio.py`. |
| D3 | Segunda tarea = reels de Instagram: filtrar relevancia, extraer solo lo importante, **ventana móvil de 6 meses**, **lote pequeño reanudable**. |
| D4 | Reels relevantes van a **base privada y también al sitio**. Esto revierte la exclusión escrita en el spec original (fase 1, punto D) y en `13_SITE/README.md:225` y `:282`; el cambio se documenta explícitamente. |
| D5 | Filtro de relevancia **con evidencia**; los dudosos se listan en el reporte para revisión del usuario, nunca se publican solos. |
| D6 | Mecanismo de ejecución: da igual, **que sea confiable**. |

### Principios que NO cambian

- **Cero inventiva:** toda afirmación lleva `video_id`/`reel_code` + `timestamp_sec` + cita + etiqueta `EXPLICITO|OBSERVADO|INFERIDO|NO CONFIRMADO`.
- **Jerarquía de fuentes:** bootcamp > educativos > reels. Un reel que repite algo documentado aporta evidencia de apoyo, no fuente primaria.
- **No borrar historial:** `--merge`, nunca rebuild; la ventana de 6 meses se aplica con `in_window=0`, nunca `DELETE`.
- **No publicar contenido sin analizar:** la publicación va al final y exige colas limpias.
- **Commit selectivo:** `git commit -- 12_VAULT`; nunca `git add -A`.

---

## 2. Arquitectura elegida

Se evaluaron tres enfoques con `Workflow`: (a) un prompt maestro único, (b) dos tareas con orquestador determinista, (c) colas persistentes en SQLite. Dos agentes completaron (b y c); el tercero y el jurado fallaron por un 503 del proveedor, por lo que la síntesis es del analista con esos dos insumos.

**Elegido: dos tareas + orquestador determinista**, con las garantías de idempotencia y checkpoint del enfoque de colas. Razones: respeta las dos tareas que el usuario ya tiene en Desktop, reutiliza todos los scripts existentes, mantiene al agente ocupándose solo de lo que requiere criterio (leer y decidir), y evita un prompt maestro frágil donde un fallo de reels bloquease el bootcamp.

### Componentes

| Componente | Tipo | Responsabilidad |
|---|---|---|
| `09_AUTOMATION/orquestador.py` | nuevo | Único punto de entrada; subcomandos `bootcamp` y `reels`. Lock, estado atómico en SQLite, reintentos, timeouts, ejecución de scripts, paquetes de decisión para el agente y resumen final. **No contiene heurísticas de extracción.** |
| `09_AUTOMATION/sync_bootcamp.py` | existente, sin cambios | Detección y transcripción. Se llama con `--download --process`. |
| `09_AUTOMATION/populate_kb.py` | existente + extensión controlada | `--merge` para bootcamp y reels. Debe aprender a generar URLs de Instagram cuando `source='REEL'` (hoy `url()` es fija a YouTube en `populate_kb.py:37-38`). |
| `09_AUTOMATION/instagram_reels_capture.py`, `_batch.py`, `_tono.py`, `_metadata.py` | existentes, reutilizar | Captura reanudable, transcripción por lotes, cola de tono y metadatos. No se reescriben. |
| `09_AUTOMATION/publicar_sitio.py` | existente, sin cambios | Único publicador: regenera, valida, comprueba diff, compila si hay node, `git commit -- 12_VAULT` + push. |
| `09_AUTOMATION/regenerar_vault.py` / `paginas_sitio.py` | existentes + extensión | Generar sección `/reels/` desde la tabla `reels` y excluir `category='REEL'` del corte de cifras (`regenerar_vault.py:1236`). |
| `09_AUTOMATION/validate_kb.py` | existente + extensión | Checks nuevos: reel promovido sin evidencia, evidencia `ig_*` huérfana, reel fuera de ventana, duplicado de cita, capítulo transcrito sin evidencia. |
| BD `xavi_ruyra.db` | existente + tablas nuevas | `reels(code, url, date_utc, duration_sec, status, relevance, tono, riesgo, evidencia, revisor, processed_at, notas, in_window)`; `orchestrator_log(run_id, tarea, fase, status, detalle, created_at)`; `publish_batch(started_at, finished_at, resultado, commit_sha, incluidos)`. |
| `13_SITE/CICLO_DE_UNA_CLASE.md`, `README.md` | existentes | Actualizar: dos tareas, orquestador, sección `/reels/`, publicación automática, exclusión revertida. |

### Flujo de datos

```
TAREA A (bootcamp)                         TAREA B (reels)
orquestador bootcamp                       orquestador reels
  ├─ sync_bootcamp.py ── DB videos           ├─ capture/metadata ── JSONL catálogo
  ├─ agente lee transcripción               ├─ selecciona lote 3–5 (≤6 meses)
  ├─ populate_kb.py --merge                  ├─ instagram_reels_batch.py (reanudable)
  ├─ validate_kb.py                          ├─ instagram_reels_tono.py --queue
  ├─ auditoría web (D1)                      ├─ agente clasifica con evidencia
  └─ checkpoints en orchestrator_log         └─ reels(relevance=RELEVANTE) → promoción
                  \                                  /
                   \── PUBLICACIÓN (solo A, al cierre)
                       precondición: sin trabajo pendiente ni BLOQUEADA/REVISION
                       publicar_sitio.py → commit 12_VAULT → push → GitHub Actions
```

---

## 3. Tarea A — bootcamp + sitio

Pasos exactos del prompt nuevo (se entregará al usuario para que lo pegue en Desktop):

1. Ejecutar `python 09_AUTOMATION/orquestador.py bootcamp`.
2. El orquestador ejecuta `python3 09_AUTOMATION/sync_bootcamp.py --download --process` (rutas relativas al proyecto; en sandbox usa `python` si `python3` no existe). Lee `10_REPORTS/daily/<fecha>.md` y `09_AUTOMATION/logs/`.
3. Si no hay vídeo nuevo: confirmar la comprobación sin inventar nada. **Pero** si existen unidades pendientes de publicación de ejecuciones anteriores, la tarea lo dice y lanza el cierre (§5).
4. Si hay vídeo nuevo del bootcamp:
   - localizar `.txt` y `.segments.json` en `02_TRANSCRIPTS/clean/`;
   - leer completo con timestamps;
   - extraer solo lo que Xavi dice o muestra, con `video_id` + timestamp y etiqueta de certeza;
   - contrastar con `05_METHODOLOGY/00-12`; si es corrección, conservar versión anterior y registrar en `05_METHODOLOGY/10_EVOLUCION.md` y tabla `changes`;
   - actualizar `05_METHODOLOGY/11_PREGUNTAS_ABIERTAS.md`;
   - añadir entradas a `populate_kb.py` y ejecutar `python3 09_AUTOMATION/populate_kb.py --merge` (nunca sin `--merge`);
   - ejecutar `validate_kb.py`; si devuelve 1, parar y reportar.
5. **Auditoría y mejora de la web por capítulo (D1):** antes del cierre, ejecutar `verificar_vault.py`, `auditar_fotogramas.py` y, si hay node y sitio servido, `verificar_sitio.mjs`. El agente corrige los hallazgos de contenido/navegación que estén dentro del alcance y escribe en el reporte: qué revisó, qué corrigió, qué no pudo verificar y **las preguntas al usuario** cuando haya una decisión de diseño (no inventar preferencias).
6. Generar el resumen diario con: vídeo, fecha, URL, duración, temas, conceptos y reglas nuevas, cambios, relación con clases anteriores, preguntas abiertas, auditoría web y resultado literal de la publicación.
7. Cierre: `publicar_sitio.py` según §5.

**Nota de rutas:** el prompt original decía `10_EVOLUCION.md` y `11_PREGUNTAS_ABIERTAS.md` en la raíz; las rutas reales son `05_METHODOLOGY/10_EVOLUCION.md` y `05_METHODOLOGY/11_PREGUNTAS_ABIERTAS.md`, además de `12_INVENTARIO_CONCEPTOS.md`.

---

## 4. Tarea B — reels de Instagram

1. Ejecutar `python 09_AUTOMATION/orquestador.py reels`.
2. **Ventana:** `date_utc >= now - 6 meses` sobre `01_CATALOG/instagram_reels_meta.jsonl`. Hoy: 1.117 de 1.591 reels en ventana; 536 sin transcribir; 759 sin etiqueta de tono. Los reels antiguos se marcan `in_window=0`, nunca se borran.
3. **Lote:** 3–5 reels por ejecución, prioridad determinista: fecha reciente > duración ≥60 s > tono `serio` > contenido en {trading, metodología, psicología} > riesgo bajo. Excluir `sin_habla`, lifestyle y humor puro. Ejecutar `instagram_reels_batch.py --limit 5` (reanudable; parar en 429 sin perder estado).
4. **Clasificación:** `instagram_reels_tono.py --queue` da prioridad por señales, **no decide**. El agente lee la transcripción y para cada reel escribe en `10_REPORTS/reels/<fecha>-lote.md`: código, fecha, duración, URL, cita con timestamp, señales, `clasificacion: RELEVANTE|DUDOSO|IRRELEVANTE`, `motivo` y `accion: promover|revision|descartar`.
   - **RELEVANTE:** aporta concepto, regla, Procedimiento o corrección de Xavi con cita verificable.
   - **DUDOSO:** humor con idea real, promesas de payout/ROI, RR extremo, hipérbole motivacional. Va a `REVISION` con cita y motivo; **nunca** entra a la base ni al sitio sin decisión del usuario (D5).
   - **IRRELEVANTE:** broma, estilo de vida, sin habla, reto; se descarta con motivo escrito.
5. **Promoción:** solo RELEVANTE. Insertar en `reels` y en `videos` un registro sintético `ig_<code>` con `category='REEL'`, `in_scope=0`, `priority=3`, URL real de Instagram; en `evidence` una fila por idea con `timestamp_sec`, `quote`, `source_type` (valor de certeza ya usado por el proyecto) y `url=https://www.instagram.com/reel/<code>/`. La extensión de `populate_kb.py` es controlada: sus listas `EVIDENCE`/`CONCEPTS`/`RULES` aceptan un campo `source` opcional que solo cambia la URL generada cuando `source='REEL'`; la lógica de certeza y el formato de cita no cambian. Nunca shortcode como video_id de YouTube; nunca sobreescribir evidencia existente.
6. `init_db.py` + `validate_kb.py` + resumen. **La tarea B nunca publica, nunca toca `12_VAULT` y nunca hace commit.**

---

## 5. Cierre y publicación

`publicar_sitio.py` sigue siendo el único publicador. El orquestador lo invoca al final de la tarea A cuando:

- el paquete de análisis de la clase está validado y mergeado;
- `validate_kb.py`, `verificar_vault.py` y `auditar_fotogramas.py` pasan;
- `verificar_sitio.mjs` pasa, o está explícitamente diferido por ausencia de node **con aviso visible en el resumen**;
- no hay conflictos de merge;
- no quedan reels en `REVISION` ni clases en `BLOQUEADA` (en cuyo caso el resumen incluye las preguntas exactas al usuario).

Si no hay capítulo nuevo pero quedan reels promovidos pendientes, se publican en el próximo cierre; nunca se publica un reel dudoso para "aprovechar" un cierre.

Sin credenciales de git, `publicar_sitio.py` ya devuelve código 5 y deja el commit local: se reporta como `PENDIENTE_DE_PUBLICAR` con el comando exacto, sin reintentos ciegos.

---

## 6. Confiabilidad (D6)

- **Estado atómico:** `orchestrator_log` con `run_id`, tarea, fase y estado; escrituras `.tmp` + `os.replace` sobre montaje FUSE.
- **Idempotencia:** claves naturales e `INSERT OR IGNORE`; `--merge` siempre; cada fase comprueba su huella antes de actuar.
- **Lock:** archivo `09_AUTOMATION/.work/lock` con `fcntl`/`msvcrt`, timeout 30 s; si está tomado, salir con código 3 sin matar procesos (evita las dos ejecuciones del 21 a las 16:24 y 16:25).
- **Reintentos:** máximo 2 por fase con backoff 5 s/15 s, solo para errores transitorios (red, 429, HTTP 5xx, `disk I/O error` del FUSE). Errores de contenido o validación no se reintentan.
- **Journals SQLite:** mantener `journal_mode=DELETE`, `locking_mode=NORMAL` y commits explícitos (diff vigente en `sync_bootcamp.py` tras el incidente del 23).
- **Timeouts:** sync 900 s, batch reels 900 s, build 900 s, push 300 s; captura de salida con `errors='replace'` (el U+FF1A ya rompió `build_transcripts.py`).
- **Fallos visibles:** `last_error` en la tabla de estado + línea por fase en el reporte; código de salida distinto de cero en fallo real; `BLOQUEADA`/`REVISION` siempre en el resumen.
- **Sin rollback destructivo:** nunca `git reset --hard`; si una fase deja archivos a medias, el estado permite reanudar. Si el merge insertó filas y la auditoría falla, no borrar filas: bloquear publicación y avisar.

---

## 7. Verificación

| Comprobación | Cómo |
|---|---|
| Tarea A sin vídeo nuevo | Ejecutar dos veces seguidas: segunda debe decir «sin novedades», sin duplicar `sync_log` ni publicar. |
| Tarea A con vídeo nuevo | Usar un vídeo de prueba o replay controlado; verificar evidencia con timestamp, `changes`, resumen y publicación al final. |
| Tarea B lote | 3–5 reels, estado reanudable; cortar a mitad y reejecutar: no debe repetir ni perder. |
| Ventana 6 meses | Consulta SQL sobre `reels.in_window`; verificar que ningún reel antiguo fue borrado de `instagram_reels_meta.jsonl`. |
| Filtro de relevancia | Revisar que los 30 reels humor/broma etiquetados no entran; los dudosos aparecen en el reporte con cita y motivo. |
| URLs en el sitio | Las fichas de fuente de reels apuntan a `instagram.com/reel/<code>/`, nunca a YouTube con ID falso. |
| Portada | El corte de cifras sigue siendo el de las clases, no el del reel más reciente. |
| Publicación | `git log`: el commit lleva solo `12_VAULT`; `05_METHODOLOGY/` y scripts siguen sin commitear por el publicador. |
| Sitio | `verificar_sitio.mjs` sobre Chrome real; si no hay node, aviso explícito y publicación diferida o con aviso según D2. |
| Documentación | README no dice «Sin publicar» ni `--publicar`; CICLO describe las dos tareas y la sección `/reels/`. |

---

## 8. Riesgos y límites conocidos

- **R1 — Prompt de la tarea B no recuperado.** El usuario deberá pegar su texto actual o confirmar que se reemplaza por el diseño de §4. No se inventa su contenido.
- **R2 — Sandbox sin node ni credenciales git.** La publicación puede quedar `PENDIENTE_DE_PUBLICAR`; está previsto y es visible, no silencioso.
- **R3 — `populate_kb.py` sin `--merge` es destructivo.** El orquestador siempre pasa `--merge`; se añadirá una guardia explícita.
- **R4 — Mezclar fuentes en `videos`.** Mitigado con `ig_<code>`, `category='REEL'`, `in_scope=0` y adaptador único; hay que revisar `regenerar_vault.py:593`, `:1236` y `paginas_sitio.py:131`.
- **R5 — Auditoría web sin node.** `verificar_sitio.mjs` no corre en el sandbox; el diseño lo reporta. Si el usuario quiere auditoría obligatoria en cada capítulo, habrá que ejecutarla en la consola de Windows o en GitHub Actions — decisión pendiente.
- **R6 — Backlog de 536 reels.** A 3–5 por día son ~107–179 días. El usuario eligió ritmo pequeño; se respeta y se reporta el progreso.
- **R7 — Commit selectivo.** Los cambios en `05_METHODOLOGY/` y `populate_kb.py` no viajan al repo con la publicación automática; es intencionado, pero el usuario debe saberlo.

---

## 9. Lo que NO se hará

- No se transcribirán reels de más de 6 meses (se marcan `in_window=0`, no se borran).
- No se publicarán reels dudosos, bromas ni contenido sin cita verificable.
- No se reescribirán los scripts de captura/transcripción de Instagram ni `sync_bootcamp.py`.
- No se creará un segundo mecanismo de `git push`.
- No se borrará historial ni se hará rebuild destructivo de la base.
- No se introducirán conceptos de ICT genérico ni de otros creadores.
- No se activará la publicación desde Programador de tareas de Windows sin revisar antes credenciales y acceso al montaje.

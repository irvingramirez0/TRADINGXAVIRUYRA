# Especificación: ciclo diario automatizado (bootcamp + reels + sitio) — diseño

**Fecha:** 2026-11-24
**Estado:** DESIGN — pendiente de revisión y aprobación del usuario. No se ha implementado.
**Fuente:** auditoría del repo y de las tareas de Claude Desktop + `Workflow` de diseño con 3 enfoques y 3 jurados (7/7 agentes completados).

---

## 1. Problema, intención y decisiones

El usuario sospechó que la IA de desarrollo anterior no entendió lo que quería. La auditoría lo confirma:

1. **El prompt del bootcamp está incompleto.** Termina en "extraer y reindexar": no publica, no audita la web y no formula preguntas (Honcho, 2026-11-16; conclusions `J-PesE6coJnfSt0MK7lwb`, `JtIgmNwm137atJ0rOsls3`, `sqQnh8KNtXA6ktfhQTJVg`).
2. **La segunda tarea es de reels de Instagram**, no otro bootcamp. El usuario lo aclaró el 2026-11-24: transcribir, extraer solo lo importante, ignorar bromas/estilo de vida, ventana de 6 meses, lotes pequeños diarios. El texto literal de esa tarea no está en disco ni en el historial recuperable (riesgo R1).
3. **Documentación desactualizada.** `13_SITE/README.md` decía «Sin publicar» y describía un flag `--publicar` retirado en `914da32`. Dos líneas ya se corrigieron el 2026-11-24 y están commiteadas en `f2116ff`. `CICLO_DE_UNA_CLASE.md` sigue describiendo un flujo de "pasos 5–9 manuales" que ya no coincide con el estado real.

### Decisiones del usuario (2026-11-24)

| # | Decisión |
|---|---|
| D1 | Con capítulo nuevo: **auditar, mejorar y verificar** el sitio; hacer preguntas cuando haya decisiones. |
| D2 | Publicación **automática al final del ciclo** con `publicar_sitio.py`. |
| D3 | Reels: filtrar relevancia, extraer solo lo importante, ventana móvil de **6 meses**, lote pequeño **reanudable**. |
| D4 | Reels relevantes van a **base privada y también al sitio**. Revierte la exclusión del spec original (fase 1.D) y de `13_SITE/README.md:225` y `:282`. |
| D5 | Filtro **con evidencia**; dudosos a revisión, nunca publicados sin decisión. |
| D6 | Mecanismo de ejecución: da igual, **que sea confiable**. |

### Principios inmutables

Cero inventiva (`video_id`/`reel_code` + timestamp + cita + `EXPLICITO|OBSERVADO|INFERIDO|NO CONFIRMADO`); jerarquía bootcamp > educativos > reels; no borrar historial (`--merge`, nunca rebuild; ventana con `in_window=0`, nunca `DELETE`); no publicar contenido sin analizar; commit selectivo `git commit -- 12_VAULT`.

---

## 2. Arquitectura elegida

Se evaluaron: (a) prompt maestro único, (b) dos tareas + orquestador, (c) colas persistentes. **Ganó (a)** con 41/45, 41/45 y 36/45 en los tres jurados; (b) obtuvo 37/40/39 y (c) 38/40/40. La síntesis final injerta en (a) el estado/lock de (b), el cierre por lote de (c) y las correcciones de los jurados.

**Diseño final:** un único prompt de Claude Desktop encadena

```
PREFLIGHT → BOOTCAMP → REELS → AUDITORÍA CONDICIONAL → PUBLICACIÓN → CIERRE
```

con una ayuda ligera (`ciclo_estado.py`) que registra fases, `rc` y líneas significativas; **no** una máquina de siete fases ni colas que exijan resolver los 1.126 reels de la ventana antes de publicar. La publicación ocurre al final de **cada** ciclo (aunque no haya capítulo nuevo); solo se bloquea por análisis inválido, validación roja, conflictos de merge o build fallido.

### Corrección técnica frente al borrador anterior

**No se inserta `ig_<code>` en la tabla `videos` ni se escribe en `evidence`.** Verificado: las 469 filas de `evidence` apuntan a `youtube.com/watch?v=`, `validate_kb.py` exige que todo `video_id` exista en `videos`, y mezclar fuentes rompería enlaces. En su lugar: tablas propias `reel_items`, `reel_evidence`, `reel_revision`, y una sección `/reels/` separada con prefijo `IG:` en el frontmatter.

### Componentes

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `09_AUTOMATION/ciclo_estado.py` | **nuevo** | `run <FASE> -- <cmd>`, `claim`, `finish`. Captura rc + últimas 40 líneas en `10_REPORTS/ciclo_<fecha>.md`, lock atómico en `.work/ciclo.lock`, estado en `.work/ciclo/estado.json`. Sin heurísticas de extracción. |
| `09_AUTOMATION/importar_reels.py` | **nuevo** | `--import reels_<fecha>.json`. Crea `reel_items`, `reel_evidence`, `reel_revision` (`IF NOT EXISTS`), upsert por `code` y dedup por `(code,timestamp_sec,quote)`. Valida la cita contra el segmento real. No toca `videos`/`concepts`/`rules`/`evidence`. |
| `09_AUTOMATION/validate_kb.py` | ampliar | Checks de reels: huérfanos, sin cita, cita sin segmento, fecha fuera de ventana, duplicados, contradicción no enviada a revisión. Conserva los actuales. |
| `09_AUTOMATION/regenerar_vault.py` | editar | Cambiar la frase de exclusión (~línea 1135) y llamar a `generar_reels(con)`. El corte de cifras sigue siendo `MAX(upload_date)` de vídeos de YouTube con evidencia: los reels no lo alteran. |
| `09_AUTOMATION/paginas_sitio.py` | ampliar | `generar_reels(con)`: `12_VAULT/reels/index.md` + nota por reel con `tipo: reel`, `video: IG:<code>`, `timestamp`, `confianza`, `fuente_url` y cita enlazada a concepto existente. Sin conceptos ni reglas nuevas. |
| 3 × `quartz-plugins/*/dist/components/index.js` | editar | `urlYoutube` detecta prefijo `IG:` → `https://www.instagram.com/reel/<code>/?t=<seg>` y etiqueta «Ver en Instagram». Rama YouTube intacta (27 casos). |
| `sync_bootcamp.py`, `publicar_sitio.py`, `instagram_batch_bootstrap.sh`, `populate_kb.py` | reutilizar | Sin cambios de infraestructura. `populate_kb.py` siempre con `--merge`; añadir `VIDEO_DATES[<id>]=<fecha_real>` por `TODAY` fijo. |
| `13_SITE/CICLO_DE_UNA_CLASE.md`, `README.md` | actualizar | Documentar cierre por lote, `/reels/`, prefijo `IG:`, publicación automática. El prompt solo detecta y avisa si siguen desactualizados. |

---

## 3. Fases del ciclo

### PREFLIGHT

`estado.json` con `lote_id=<fecha>`, fases `PREFLIGHT|BOOTCAMP|REELS|AUDITORIA|PUBLICACION|CIERRE`, `rc`, `ultima_linea_util`, `errores`. Lock con PID/timestamp; huérfano >2 h se recupera, lock activo → salir con aviso sin matar procesos. `git status --porcelain` solo detecta conflictos `UU|AA|DD|AU|UA|DU|UD`: frena publicación, nunca `git add -A`. Ante `disk I/O error`, **conservar el journal**, nunca borrar la BD.

### BOOTCAMP

1. `python3 09_AUTOMATION/sync_bootcamp.py --download --process` por el wrapper. Un solo reintento (backoff 5/15 s) para red, HTTP 5xx, 429 o `disk I/O error`. Registrar literalmente `NUEVO`, `REINTENTO`, `init_db.py: ERROR`, `AVISO FTS`, `Sin publicaciones nuevas`.
2. Clase nueva = una sola consulta comprobable: `SELECT v.id, v.upload_date FROM videos v WHERE v.category='BOOTCAMP' AND v.status<>'no_disponible' AND NOT EXISTS (SELECT 1 FROM evidence e WHERE e.video_id=v.id) ORDER BY v.upload_date DESC LIMIT 1`, más existencia de `.segments.json` y `.txt`. Hoy devuelve 0 filas. **Máximo una clase por ejecución**; las demás quedan explícitas en el reporte.
3. Sin clase: escribir `SIN CLASE NUEVA — metodología intacta` y saltar a REELS. No ejecutar `populate_kb.py`.
4. Con clase: construir `.work/ciclo/analisis_<video_id>.json` con contrato `{"video_id","upload_date","transcript_path","sha256","extracciones":[{tipo,nombre,certainty,timestamp_sec,quote,nota,accion,target}]}`. Validación: la `quote` normalizada debe aparecer en el segmento que cubre el timestamp; `INFERIDO`/`NO CONFIRMADO` solo a `11_PREGUNTAS_ABIERTAS.md`, nunca a reglas; `OBSERVADO` puede ser evidencia, no regla nueva sin formulación literal.
5. Escribir en los ocho documentos de `05_METHODOLOGY/` y añadir filas a `CONCEPTS/RULES/EVIDENCE/CHANGES/CURRICULUM/VIDEO_DATES`. `TODAY = "2026-11-15"` es fijo en `populate_kb.py`: usar `VIDEO_DATES` con la fecha real y dejar aviso en el reporte.
6. En orden: `populate_kb.py --merge` (nunca sin `--merge`, nunca con `XAVI_ALLOW_REBUILD=1`) → `validate_kb.py` → `PRAGMA integrity_check` → `init_db.py` solo si `sync --process` no lo hizo → `build_search_index.py` solo si cambiaron anotaciones. Registrar conteos antes/después.
7. Fallo de extracción, merge, validación o integridad → fase `BLOQUEADA`, sin publicación, error literal y pregunta solo si hay decisión nueva.

### REELS

1. `bash 09_AUTOMATION/instagram_batch_bootstrap.sh 3 4` (3–4 reels, reanudable; modelo y cookies dentro del proyecto). Ante 429/red: registrar y reintentar **una vez** al final del ciclo. Si el bootstrap sale 2 por falta de modelo: avisar con la ruta, no simular transcripción.
2. Solo si faltan códigos en ventana: `instagram_reels_capture.py --cookies www.instagram.com_cookies.txt --max-steps 120` + `instagram_reels_metadata.py`. Ante 429/302 parar conservando los JSONL. Ventana móvil 6 meses sobre `date_utc` (hoy ~1.126 reels, 517 transcritos, 358 etiquetados, 201 transcritos sin etiqueta); marcar `in_window=0`, nunca borrar.
3. `instagram_reels_status.py` + `instagram_reels_tono.py --queue`. Las señales (broma/humor, payout/eval, ratio 1:N, promesa, lifestyle) son **prioridad, no veredicto**.
4. Hasta 4 códigos por ejecución: en ventana, `transcribed`, sin tono útil o con `evidencia` vacía, duración preferentemente ≥60 s, fecha reciente primero. Leer `02_TRANSCRIPTS/instagram/<code>.json`.
5. Contrato `.work/ciclo/reels_<fecha>.json` por reel: `{code,url,date_utc,duration_sec,tono,contenido,riesgo,clasificacion,certainty,evidencia:[{timestamp_sec,quote,entity_name,accion}],motivo,revisor,fecha_revision}`. Cita normalizada obligatoria en el segmento; sin cita → `DUDOSO` automático.
6. Criterios:
   - **RELEVANTE:** tono serio u humor con fondo docente verificable, cita literal de concepto/regla/procedimiento/corrección, riesgo bajo o medio. Si repite bootcamp/vídeo educativo → `accion=secundario`, `certainty=OBSERVADO`, sin regla nueva. Si es nuevo → solo `reel_evidence`, nunca concepto/regla nueva sin decisión.
   - **DUDOSO:** `tono=dudoso`, riesgo alto, promesas de payout/ROI, RR extremo, hipérbole, humor sin lección, cita ambigua o contradicción con `05_METHODOLOGY`. Va a `10_REPORTS/instagram_reels_revision_<fecha>.md` con cita y motivo; **no bloquea** el cierre del lote.
   - **IRRELEVANTE:** sin habla, música, lifestyle puro, reto, <60 s sin concepto. Se guarda con motivo, no se publica.
7. `python3 09_AUTOMATION/importar_reels.py --import .work/ciclo/reels_<fecha>.json`. `estado_sitio=pendiente` solo para RELEVANTE. Reindexar solo si cambiaron vídeos/segmentos; repetir `validate_kb.py` + `integrity_check`. Fin de fase: resumen; **sin publicar, sin tocar `12_VAULT`, sin commit**.

### AUDITORÍA (solo si hubo capítulo nuevo)

`verificar_vault.py`, `auditar_fotogramas.py --detalle`, `revisar_capturas.py` (revisión visual del día nuevo). Si `auditar_fotogramas` marca `contradice`, corregir con `vetar_fotogramas.py` antes de publicar. Si hay node + Chrome + sitio servido: build Quartz, `python -m http.server 8899 --directory public`, `node verificar_sitio.mjs http://127.0.0.1:8899 build` (27 casos; el tercer argumento es obligatorio con `http.server`). Sin node/Chrome: `AUDITORIA_DIFERIDA`, **no afirmar verificación**. Mejoras de UI solo con evidencia del test.

### PUBLICACIÓN

`python3 09_AUTOMATION/publicar_sitio.py` por el wrapper. **No copiar solo la última línea** (`sys.exit(main())`): registrar rc y líneas significativas.

| rc + línea | Interpretación |
|---|---|
| 0 + `Publicado. GitHub Actions compilará y despleará.` | PUBLICADO |
| 0 + `El vault no cambió. No hay nada que publicar.` | SIN CAMBIOS (no es fallo) |
| 5 + `Sin credenciales de git…` | PENDIENTE_DE_PUBLICAR (commit local hecho, **no** éxito de deploy) |
| 3 | Conflictos / `--estricto`, bloqueado |
| 1 + `FALLO al…` | Bloqueado |

Antes del push, si hay reels aceptados, aplicar y commitear **selectivamente** los cambios de código de reels (regenerar_vault, paginas_sitio, 3 plugins) con `git commit -m "Habilitar reels citados en el sitio" -- <rutas>`; nunca `git add -A`. Si chocan con trabajo ajeno, frenar y avisar.

Cerrar `lote_id` en `estado.json` con `clase`, `reels[]`, `auditoria=OK|DIFERIDA|FALLO|NO_APLICA`, `publicacion=<rc + línea>`, `reporte=<ruta>`. Cuando no haya clase, reels aceptados ni cambios en el vault: decir explícitamente «nada que publicar».

---

## 4. Confiabilidad (D6)

- Estado atómico `.tmp` + `os.replace` sobre montaje FUSE; lock con PID/timestamp y recuperación de huérfanos >2 h.
- Timeouts: sync 900 s, bootstrap reels 900 s, build 900 s, push 300 s; captura UTF-8 con `errors='replace'` (U+FF1A ya rompió `build_transcripts.py`).
- Idempotencia: `INSERT OR IGNORE`, `--merge`, dedup por `(code,timestamp,quote)`, sin commits vacíos.
- **Un solo reintento** por fase y solo para transitorios (red, 429, HTTP 5xx, `disk I/O error`); errores de contenido/validación/compilación no se reintentan.
- Todo rc ≠ 0 y toda línea `ERROR`, `FALLO`, `AVISO FTS`, `no publicado`, `BLOQUEADA`, `Sin credenciales` se copia literalmente al reporte; la fase dependiente se detiene.
- Prohibido: `git reset --hard`, matar procesos por lock ajeno, exigir que toda la ventana esté resuelta para cerrar, dejar que un dudoso bloquee la publicación, afirmar verificación sin node/Chrome, interpretar rc 5 como éxito, preguntar salvo ante decisiones nuevas.

---

## 5. Verificación antes de aprobar la implementación

| Comprobación | Cómo |
|---|---|
| Sin clase ni reels | Ejecutar dos veces: segunda dice «sin novedades», sin duplicar `sync_log` ni publicar. |
| Con clase | Replay controlado; verificar `analisis_<id>.json`, citas con timestamp, `changes`, resumen y publicación al final. |
| Lote reels | 3–4 reels; cortar a mitad y reejecutar: sin repetir ni perder. |
| Ventana | `reels.in_window`; ningún reel antiguo borrado de los JSONL. |
| Filtro | Los 30 reels humor/broma etiquetados no entran; dudosos aparecen con cita y motivo. |
| Enlaces | Fichas de fuente de reels → `instagram.com/reel/<code>/?t=<seg>`, nunca YouTube con ID falso; botón «Ver en Instagram». |
| Portada | Fecha de corte igual a la de las clases. |
| Sitio | `verificar_sitio.mjs` 27/27 sobre Chrome real (o `AUDITORIA_DIFERIDA` explícita). |
| Commit | `git log`: solo `12_VAULT` entra en el commit automático. |

---

## 6. Riesgos

- **R1:** prompt literal de la tarea B no recuperado; el usuario debe pegarlo o confirmar su reemplazo por §3 REELS.
- **R2:** sandbox sin node ni credenciales git → `PENDIENTE_DE_PUBLICAR` o `BUILD_DIFERIDO`, visibles, no silenciosos.
- **R3:** `populate_kb.py` sin `--merge` es destructivo y tiene `TODAY` fijo en 2026-11-15; se fuerza `--merge` + `VIDEO_DATES`.
- **R4:** ~471 archivos modificados en el árbol de trabajo → prohibido `git add -A`; los cambios de código se commitean aparte.
- **R5:** si un reel dudoso contiene metodología real envuelta en humor, solo se acepta con cita que demuestre la lección; si no, a revisión.
- **R6:** backlog de 536 reels sin transcribir en ventana → a 3–4/día son ~134–179 días; ritmo elegido por el usuario.
- **R7:** commit selectivo deja `05_METHODOLOGY/` y scripts sin subir con la publicación; intencionado, debe saberlo el usuario.

---

## 7. Lo que NO se hará

No transcribir reels de >6 meses (se marcan, no se borran); no publicar dudosos, bromas ni contenido sin cita; no reescribir `sync_bootcamp.py` ni los scripts de Instagram; no crear un segundo publicador; no insertar `ig_<code>` en `videos` ni escribir en `evidence` desde reels; no borrar historial; no introducir ICT genérico; no activar Programador de Windows sin revisar credenciales y montaje.

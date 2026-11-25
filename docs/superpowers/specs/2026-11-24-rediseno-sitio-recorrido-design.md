# Especificación: rediseño del sitio como recorrido de aprendizaje — diseño

**Fecha:** 2026-11-24
**Estado:** DESIGN — pendiente de revisión. No se ha implementado.
**Fuente:** workflow `cuestionar-diseno-sitio` (5/5 agentes, 496.555 tokens) + 20 decisiones confirmadas por el usuario en ronda de preguntas.

---

## 1. Veredicto

El jurado lo dice sin rodeos: **el sitio es un archivo, no un método**. Tiene 412 páginas, 0 enlaces rotos y 200 OK, pero la experiencia real es «un repositorio de datos disfrazado de sitio». La causa raíz de que al usuario «no le termine de encantar»:

1. La única síntesis que explica la metodología (`05_METHODOLOGY/00_MAPA_METODOLOGIA.md:104-170`) **no está publicada**: `/05_METHODOLOGY/00_MAPA_METODOLOGIA` → 404 (verificado por HTTP).
2. Los 29 botones «Ver en YouTube» del bootcamp enlazan al **segundo 0**, aunque la portada promete salto al minuto exacto (`t=0s` aparece 30 veces en el HTML compilado).
3. El flujo de conceptos es **taxonómico** (CORE/CONTEXTUAL/NOT USED/SUPPORTING), no pedagógico.
4. Solo 3 de 29 clases tienen capturas; FVG, PO3 y AMD no tienen imagen **pese a tener candidatos anotados**.
5. El «Comprobador de fuentes» dice «Todo tiene fuente» mientras ignora las 54 operaciones con P&L autodeclarado.
6. Cada índice muestra dos listas (tarjetas propias + `page-listing` de Quartz: 156 + 156 en reglas).
7. Cada nota tiene 12–13 apartados, 5 chips, blockquote duplicado, grafo, backlinks, TOC y un formulario de anotaciones con 0 usos.
8. Las cifras se contradicen (34 vs 38 preguntas, 67 vs 68 cambios) y hay 4 preguntas duplicadas con información incompatible.
9. Las contradicciones metodológicas (9:30–10:30 vs 9:30–11:00, CISD) conviven sin jerarquía visible.
10. El QA `verificar_sitio.mjs` exige 21 días cuando hay 29: fallo garantizado que enmascara los defectos reales.

**Hallazgo añadido durante este diseño:** `publicar_sitio.py --simular` terminó con «Build correcto» y código 0 aunque `regenerar_vault.py` había agotado un timeout de 1800 s. El pipeline puede publicar sobre una regeneración fallida. Esto se corrige antes de cualquier deploy (§5).

---

## 2. Decisiones del usuario (2026-11-24)

| # | Decisión |
|---|---|
| N1 | Publicar «Empieza aquí» con la secuencia real del método como **ruta principal** (primera tarjeta de la portada). |
| N2 | Extraer el **minuto real** de las 29 clases y fallar el QA si aparece `t=0s`. |
| N3 | Organizar conceptos por **dependencia, nivel 1→4**; la categoría queda como etiqueta secundaria. |
| N4 | Corregir el **reparto de fotogramas**: priorizar CORE, permitir un frame para varios conceptos si la anotación lo nombra, retirar imágenes cuyo pie diga «no se ve», rellenar FVG/PO3/AMD y anotar las 14 clases pendientes con la hoja existente. |
| N5 | Comprobador honesto: barras separadas, conceptos/reglas con cita formal y **0/54 operaciones** con cita formal + aviso de P&L autodeclarado. Quitar «Todo tiene fuente». |
| N6 | **Desactivar `page-listing`** donde ya hay índice propio. |
| N7 | Recortar notas a **4–5 apartados**, colapsar anotaciones en un botón, desactivar grafo/backlinks por defecto en notas. |
| N8 | **Una sola fuente de cifras** + tabla pública de contradicciones «Vigente / Histórica / Clase que la resuelve». |
| N9 | QA arreglado (días desde el índice, no hardcodeado) y ampliado a `t=0s`, cobertura CORE y pies «no se ve». |
| N10 | Dos fases: **rediseño primero, ciclo automático después**, sobre la web ya corregida. |
| N11 | Publicar primero una **versión congelada** conocida; nunca decidir UX sobre un estado local que no coincide con el visitante. |

---

## 3. Arquitectura de la nueva experiencia

### 3.1 Ruta principal: «Empieza aquí»

`regenerar_vault.py` genera `12_VAULT/00-empieza-aqui.md` desde la sección §3 de `00_MAPA_METODOLOGIA.md`, **sin copiar el texto a mano**: el generador lee el bloque delimitado y lo transforma en una página con enlaces `[[...]]` a conceptos y clases existentes. Secuencia:

`4H/1H → DOL → liquidez (BSL/SSL) → PO3/tiempo → entradas (FVG/IFVG) → gestión → riesgo → psicología`

El frontmatter incluye `corte` con la fecha real de `MAX(upload_date)` de vídeos con evidencia. La portada (`12_VAULT/index.md`) pone esta página como **primera tarjeta**; el panel de cifras pasa a的状态 secundario. Cuando el mapa local cambie, la página se regenera: ya no habrá cifras desincronizadas.

### 3.2 Ruta de conceptos por dependencia

Nueva tabla en `07_KNOWLEDGE_BASE/xavi_ruyra.db`:

```sql
concepto_relaciones(
  concepto_id INTEGER, requiere_id INTEGER, tipo TEXT,  -- 'requiere' | 'se_combina_con'
  PRIMARY KEY (concepto_id, requiere_id, tipo)
)
```

Niveles derivados (no escritos a mano):

| Nivel | Contenido |
|---|---|
| 1 | Liquidez, swings, estructura de velas |
| 2 | FVG, PO3, equilibrium |
| 3 | IFVG, CISD, DOL |
| 4 | Sesiones, noticias, psicología |

`paginas_sitio.py` genera `12_VAULT/conceptos/ruta.md` con los cuatro niveles y enlaces a cada nota; `conceptos/index.md` mantiene CORE/CONTEXTUAL/NOT USED/SUPPORTING como **filtro secundario** con etiqueta visible. Los 8 conceptos `NOT USED` (RSI, MACD, Elliott…) se agrupan en un bloque «Xavi no los usa» con una línea, no 11 apartados.

### 3.3 Vídeos: minuto real

Para cada `curriculum.video_id`, el generador toma `MIN(evidence.timestamp_sec)` de las filas con `source_type IN ('EXPLICITO','OBSERVADO')` y rellena el frontmatter `timestamp`. Regla:

- Con evidencia → `timestamp = MM:SS` real, botón «Ver en YouTube · MM:SS».
- Sin evidencia → **sin atributo de tiempo**, botón «Ver clase completa» (nunca `00:00`).
- Los días 28–29, con `duration_sec=NULL` y `status='catalogado'`, se marcan «duración desconocida» hasta que `init_db.py` tenga metadatos reales; no se inventa duración.

### 3.4 Fotogramas: reparto y calidad

Cambios en `regenerar_vault.py` (sección `build_media`, ~526-570):

1. **Prioridad de categoría:** `CORE` > `SUPPORTING` > `CONTEXTUAL`, a igualdad de anotación válida. Un frame ya asignado a un concepto CONTEXTUAL se reasigna al CORE que lo nombra (casos #734/#707 → FVG, #402 → AMD).
2. **Multi-propiedad permitida** cuando la anotación nombra literalmente más de un concepto CORE; se elimina la regla de «dueño único» para esos casos.
3. **Sustituir `es_pantalla()`** (mide saturación de color, falla con cámara sobre gráfico) por detección de zonas de TradingView + regiones anotadas. `frame_vacio()` se ajusta para esquemas claros.
4. **Veto por negación:** ampliar `NEGACIONES/_AUSENCIA` con «no hay etiquetas de», «no se distingue», «muy alejado», «no muestra». Las 5 notas con pie confesivo (#383, #669, #681, #689 y similares) dejan de publicar imagen. «Contexto» pasa a estado de espera, no de ilustración.
5. **Cobertura mínima:** todo concepto CORE con evidencia válida tiene ≥1 imagen. Si no hay candidato anotado, se muestra un estado explícito «pendiente de anotación» con enlace a `revisar_capturas.py --tanda`.
6. **Reglas:** reutilizar `build_media()` para reglas con el mismo filtro, ampliando `frame_vetos` con `entity_type`; 27 reglas tienen candidato verificado.
7. **Calidad:** recapturar en 1080p los 7 vídeos con WebP nativo 640x360 (`recapturar_1080p.py`); mantener 1200 px como ancho mínimo.
8. **Bootcamp:** ejecutar `frames_selectivos.py --prioridad BOOTCAMP` para los 14 vídeos elegibles y usar `revisar_capturas.py` para anotar antes de publicar. Solo se publica lo anotado y verificado.

### 3.5 Comprobador, índices y notas

- `comprobador_fuentes()` pasa `slugs_trade` y `slugs_cambio` reales; muestra barras: «Conceptos 58/58», «Reglas 156/156», «Operaciones 0/54 con cita formal (P&L autodeclarado)». Se elimina el bloque «Todo tiene fuente — Todas las entidades».
- `quartz.config.yaml`: desactivar `folder-page` para las carpetas con `index.md` propio (deja una sola lista).
- Notas: `regenerar_vault.py` colapsa las 13 secciones en 4–5 (`Qué es`, `Cómo usarlo`, `Errores`, `Evidencia`), elimina el blockquote duplicado y deja el formulario de anotaciones detrás de un botón «✎ anotar» (ya existe en `index.js:521-536`). `graph` y `backlinks` se desactivan por defecto en notas; la portada conserva el grafo global.

### 3.6 Cifras y contradicciones

- Una sola función de conteo en `regenerar_vault.py`; `paginas_sitio.py` consume esos números en vez de volver a contar. `generate_preguntas()` elimina los 4 ficheros huérfanos y separa «Abiertas» de «Cerradas» con fecha.
- Publicar `12_VAULT/contradicciones.md` desde la tabla de 7 contradicciones de `05_METHODOLOGY/11_PREGUNTAS_ABIERTAS.md:357-370`, con columnas «Vigente / Histórica / Clase que la resuelve». Cada regla muestra `vigencia: vigente|histórica|en-tensión` en su ficha.

---

## 4. Orden de ejecución (dos fases)

**Fase 0 — congelación:** corregir el timeout silencioso de `publicar_sitio.py` (si una fase agota el timeout, rc ≠ 0 y **no** se publica); verificar los 472 cambios; publicar una versión congelada y confirmar 200 en producción. Solo entonces empezar el diseño.

**Fase 1 — rediseño (este spec):** N1 → N3 → N2 → N4 → N5/N6/N7 → N8 → N9. Cada paso se verifica con build + QA antes de seguir.

**Fase 2 — ciclo automático:** retomar `2026-11-24-tareas-automatizadas-bootcamp-reels-design.md` (spec `e6eca19`) sobre la web ya corregida. El único cambio de alcance: la auditoría del ciclo usa el QA ampliado de N9.

---

## 5. Verificación

| Criterio | Comprobación |
|---|---|
| Método publicado | `curl` a `/00-empieza-aqui` → 200; contiene las 8 etapas y enlaces reales. |
| Minuto real | 0 ocurrencias de `t=0s` en `/bootcamp/`; 29 botones con minuto o etiqueta «clase completa». |
| Ruta conceptos | `/conceptos/ruta` con 4 niveles; ningún concepto CORE sin enlace. |
| Fotogramas | 16/16 CORE con evidencia tienen imagen; FVG/PO3/AMD publicadas; 0 pies con «no se ve». |
| Reglas | >0 reglas con imagen verificada. |
| Comprobador | Muestra «0/54 operaciones con cita formal» y no dice «Todo tiene fuente». |
| Índices | 1 lista por sección (0 `page-listing` duplicado). |
| Notas | ≤5 apartados por nota; anotaciones colapsadas. |
| Cifras | Una sola cifra por concepto en portada/índices; 0 preguntas duplicadas. |
| Contradicciones | `/contradicciones` con 7 filas y vigencia visible. |
| QA | `verificar_sitio.mjs` pasa con 29 días y nuevos criterios; falla a propósito si se inserta `t=0s`. |
| Publicación | `publicar_sitio.py` no publica si una fase interna agota el timeout. |

---

## 6. Riesgos

- **R1:** el timeout de `regenerar_vault.py` (1800 s) puede deberse al montaje FUSE o al volumen de notas; hay que medirlo antes de culpar al QA.
- **R2:** permitir un frame para varios conceptos rompe la regla documentada «1 fotograma = 1 concepto»; se acota solo a conceptos CORE nombrados literalmente y se documenta el cambio.
- **R3:** publicar el mapa metodológico puede desactualizarse si alguien edita `05_METHODOLOGY` a mano; el generador debe derivar, no copiar.
- **R4:** desactivar `page-listing` puede ocultar notas huérfanas; verificar que todas las notas siguen siendo alcanzables desde algún índice.
- **R5:** 471+ archivos sin commitear → publicar solo lo verificado, nunca `git add -A`.

---

## 7. Lo que NO se hará

No inventar minutos ni duraciones; no publicar imágenes que no ilustren; no borrar historial ni duplicados (se marcan «Cerradas»); no reescribir la metodología a mano en el vault; no automatizar el ciclo hasta que el rediseño esté verificado; no publicar sobre una regeneración que haya agotado un timeout.

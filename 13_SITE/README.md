# 13 — SITIO DE CONOCIMIENTO (OBSIDIAN + QUARTZ + GITHUB PAGES)

**Estado:** montado y verificado en local a 2026-11-14. **Sin publicar.**
**Coste:** cero (GitHub Pages en repositorio público + Quartz estático).

---

## 1. Qué hay

| Ruta | Función |
|---|---|
| `12_VAULT/` | Vault de Obsidian **y** fuente del sitio. Se regenera desde SQLite. |
| `13_SITE/quartz/` | Quartz 5.1.0 (framework del sitio). |
| `13_SITE/quartz/quartz.config.yaml` | Título, idioma `es-ES`, `baseUrl`, analítica desactivada. |
| `.github/workflows/publicar-sitio.yml` | Compila y publica en GitHub Pages. |

El sitio se construye **directamente** desde `12_VAULT/`; no hay copia intermedia.

## 2. Regenerar y ver

```bash
python 09_AUTOMATION/regenerar_vault.py        # 53 conceptos + 135 reglas + 54 ops + 55 cambios + 31 preguntas
python 09_AUTOMATION/verificar_vault.py        # frontmatter, enlaces e imágenes
cd 13_SITE/quartz && npx quartz build --serve -d ../../12_VAULT
# http://localhost:8080
```

Vista de grafo, búsqueda, explorador y backlinks están activos. El grafo local
tiene `depth: -1` (todo el grafo); en cada nota, `depth: 1`.

## 3. Qué incluye el vault

- **Conceptos**: definición, interpretación de Xavi, identificación, condiciones,
  temporalidades, aplicación, errores y excepciones; evidencia con vídeo y minuto;
  1–3 fotogramas WebP (máx. 1200 px) con pie de vídeo, timestamp y confianza.

### Regla de las imágenes (estricta)

Un fotograma solo ilustra un concepto si **su anotación lo dice**. Se aplica así:

1. **Solo fotogramas anotados.** Un fotograma «pendiente de anotación» no se
   publica como ilustración: nadie ha verificado qué se ve en él.
2. **Manda `description`, no `analysis`.** La descripción es lo que el anotador
   vio en pantalla; `analysis` es la transcripción, y dice lo que se hablaba.
3. **Alias distintivo.** Vale el nombre o un alias que pertenezca solo a ese
   concepto. Que una captura muestre «FVG» no la convierte en prueba de «IFVG».
4. **Se descarta lo que se contradice.** Si la anotación dice del concepto «no
   hay un rótulo que lo identifique» o «no muestra las tres fases», la imagen no
   se usa, aunque tenga fila de `evidence`.
5. **El contexto se etiqueta.** Si la anotación no nombra el concepto pero
   tampoco lo niega, la imagen se publica con la etiqueta «imagen de contexto, no
   muestra el concepto».

Motivo: antes bastaba con que hubiera una fila de `evidence` con `frame_id`, y
la nota de IFVG llegó a mostrar una captura de Judas Swing cuyo propio
comentario decía que no identificaba el IFVG.

Auditoría: `python 09_AUTOMATION/auditar_fotogramas.py [--bootcamp] [--detalle]`.
- **Reglas**: descripción, contexto, condiciones, invalidación, riesgo, objetivos;
  enlaces automáticos a los conceptos que menciona; enlace a la regla que
  **reemplaza** (campo `supersedes`).
- **Operaciones**: ficha completa con el aviso **«P&L autodeclarado, no auditado»**
  y enlaces a conceptos y reglas relacionadas.
- **Cambios**: tipo, valor anterior, valor nuevo, entidad afectada y fuente.
- **Preguntas abiertas**: leídas de `05_METHODOLOGY/11_PREGUNTAS_ABIERTAS.md`,
  con su estado de confirmación.

Frontmatter mínimo en cada nota: `tipo`, `titulo`/`title`, `confianza`
(explícito / observado / inferido / no confirmado), `estado` (vigente / obsoleta),
`video`, `timestamp`.

## 4. Exclusiones deliberadas

- Transcripciones completas (`02_TRANSCRIPTS/`): fuera.
- Reels de Instagram: fuera.
- Vídeos descargados y copias de backup de la base: fuera del repo vía `.gitignore`.
- Datos personales: no se ha encontrado ninguno en el texto que se publica
  (revisión de `trades`, `concepts`, `rules`, `evidence` y `changes`).

## 5. Publicación

**Publicado:** <https://irvingramirez0.github.io/TRADINGXAVIRUYRA>

| Pieza | Valor |
|---|---|
| Repositorio | <https://github.com/irvingramirez0/TRADINGXAVIRUYRA> (público) |
| Rama de publicación | `main` |
| Origen de Pages | GitHub Actions (`build_type: workflow`) |
| `baseUrl` | `irvingramirez0.github.io/TRADINGXAVIRUYRA` |

> **Historial del dominio.** La cuenta tenía `madelove.me` como dominio
> personalizado en `irvingramirez0.github.io`. Ese dominio lo sirve **Vercel**
> (SyncLove), no GitHub Pages, y GitHub hereda el dominio personalizado en
> todas las páginas de proyecto: cualquier URL de proyecto respondía `301`
> hacia `madelove.me`, donde no existía. Se eliminó el `CNAME` de
> `irvingramirez0.github.io` para que las páginas de proyecto vuelvan a su URL
> de `github.io`. Si algún día se recupera un dominio propio, hay que
> configurarlo **repo por repo** y apuntar el DNS a GitHub, no a Vercel.

Cada push a `main` compila y publica. Para volver a desplegar sin cambiar nada:
*Actions → Publicar el sitio en GitHub Pages → Run workflow*.

## 6. Límites conocidos

- **Resolución:** la Fase 0 descargó a 480p, así que el `.webp` salía a 854 px.
  `09_AUTOMATION/reextraer_720p.py` re-extrae a 720p solo los fotogramas que el
  sitio publica y no llegaban a 1200 px, pidiendo a yt-dlp el tramo de ±6 s en
  vez del vídeo completo. Sustituye la imagen del mismo instante; **nunca toca
  el texto de una anotación manual**.
- Los fotogramas nuevos están **sin anotar**. El vault solo muestra los que ya
  tienen anotación o, si no hay, los pendientes; la anotación manual es trabajo
  aparte y no se inventa.
- La portada declara el proyecto como **estudio no oficial** y lleva fecha de corte.

## Estado verificado (2026-11-15)

| Comprobación | Resultado |
|---|---|
| `regenerar_vault.py` | 329 notas (53 conceptos, 135 reglas, 54 operaciones, 55 cambios, 31 preguntas) |
| `verificar_vault.py` | 0 enlaces rotos, 0 imágenes rotas, frontmatter completo |
| `auditar_fotogramas.py` | 54 imágenes muestran su concepto, 13 son de contexto, 26 conceptos sin imagen |
| `auditar_fotogramas.py --bootcamp` | 5 imágenes, todas muestran el concepto; 0 de contexto |
| `quartz build` | 791 archivos, grafo y búsqueda activos |
| **`npm ci` + build en clon limpio** | 329 notas partiendo solo de los archivos rastreados en git |
| **Sitio en producción** | 200 en `/`, en las notas y en los `.webp`; grafo y búsqueda presentes |
| Auditoría de contenido | ninguna cita > 246 caracteres; ningún dato personal; sin Reels |
| Imágenes | 64 WebP; la mayoría a 1200 px de ancho y sin la interfaz del gráfico |
| Repositorio local | sin vídeos, transcripciones, base ni modelos |

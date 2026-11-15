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
| `13_SITE/quartz/quartz-plugins/` | Componentes propios: ficha de fuente, panel de avance y anotaciones. |
| `.github/workflows/publicar-sitio.yml` | Compila y publica en GitHub Pages. |

El sitio se construye **directamente** desde `12_VAULT/`; no hay copia intermedia.

## 1-bis. Secciones del sitio

| Sección | Qué es |
|---|---|
| `/bootcamp/` | Las 20 clases en orden. Cada día tiene su página con los conceptos que introduce, las reglas que salen de él, sus fotogramas y la navegación anterior/siguiente. |
| `/conceptos/` | Índice por categoría (CORE / CONTEXTUAL / …) con tarjetas. |
| `/reglas/` | Índice de reglas, separando vigentes y obsoletas. |
| `/operaciones/` | Índice con el aviso de P&L autodeclarado. |
| `/cambios/` | Índice cronológico de cambios de criterio. |
| `/preguntas/` | Índice agrupado por estado real de cada pregunta. |
| `/comprobador/` | Página de auditoría: qué no tiene respaldo, dicho en voz alta. |

Cada nota lleva además:

- **Ficha de fuente** (arriba): tipo, confianza, estado, **clase del bootcamp**
  donde aparece y botón que abre el vídeo en el minuto exacto. Botón «Copiar
  cita» para citarla fuera del sitio.
- **Anotaciones** (abajo): comentarios anclados a una sección concreta.

### Los componentes propios viven en plugins locales

`quartz-plugins/{ficha-fuente,panel-avance,anotaciones}` son plugins de Quartz
normales: un `package.json` con bloque `quartz` y un `dist/components/index.js`.

Quartz los enlaza en `.quartz/plugins/` con un **symlink**, que en Windows falla
con `EPERM` sin privilegios. Por eso hay que preparar los enlaces antes de
compilar:

```bash
09_AUTOMATION\preparar_plugin_sitio.cmd          # Windows: junctions (mklink /J)
```

En GitHub Actions (Linux) el propio workflow los crea con `ln -s`; no hace falta
tocar nada. Un plugin de carpeta con **varios** componentes no se coloca con
`layout:` (Quartz lo trata como un solo componente), así que cada componente es
su propia carpeta.

### Comentarios: qué funciona de verdad

Las anotaciones se guardan en el **navegador** de cada lector
(`localStorage`), con sección, autor opcional, enlace directo y exportación a
JSON. Son privadas por defecto y se comparten por enlace o por archivo.

Publicar en el navegador no es publicar en un servidor. Para que un comentario lo
vea todo el mundo hace falta un servicio de guardado, y **el sitio no lleva uno
de serie a propósito**: los servicios anónimos sin cuenta no garantizan
permanencia, y usar uno daría la falsa impresión de que los comentarios quedan
guardados para siempre.

El punto de enganche está preparado: si una nota declara
`endpoint_anotaciones: "https://…"` en el frontmatter, el componente envía ahí
un `POST` con `{nota, anotaciones}` y hace un `GET ?nota=…` al abrir. Si el
endpoint falla, la anotación se queda en local y la interfaz lo dice, en vez de
perderla en silencio. Opciones, en orden creciente de esfuerzo:

| Opción | Cuenta | Coste | Comentarios compartidos |
|---|---|---|---|
| Navegador + enlace + exportar (actual) | no | 0 | no (uno a uno) |
| Supabase / Firebase (free tier) | sí | 0 | sí |
| Cloudflare Worker + KV | sí | 0 | sí |
| Giscus (GitHub) | sí (GitHub) | 0 | sí |

Giscus está soportado por Quartz de fábrica (`@quartz-community/comments`), pero
exige cuenta de GitHub a quien comenta, que es justo lo que se quería evitar.


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
5. **Se descarta lo que no tiene contenido.** Una diapositiva de texto sobre un
   gráfico en blanco no ilustra nada aunque su texto nombre el concepto.
6. **Un fotograma pertenece a un solo concepto.** Si su anotación nombra dos
   («NQ 5m. SMT en el low y FVG de 5m»), la imagen es prueba de uno y deja de
   publicarse en el otro. Es el fallo del IFVG con Judas Swing multiplicado:
   había 9 fotogramas repartidos entre 2–3 notas distintas.
7. **El contexto se etiqueta y se limita.** Si la anotación no nombra el
   concepto pero tampoco lo niega, la imagen se publica como **una sola** imagen
   de contexto, marcada «no muestra el concepto». Si ya hay alguna imagen que sí
   lo muestra, las de contexto no se usan.

Motivo: antes bastaba con que hubiera una fila de `evidence` con `frame_id`, y
la nota de IFVG llegó a mostrar una captura de Judas Swing cuyo propio
comentario decía que no identificaba el IFVG.

Auditoría: `python 09_AUTOMATION/auditar_fotogramas.py [--bootcamp] [--detalle]`.

### Revisión visual (lo que un programa no puede decidir)

Las reglas anteriores leen anotaciones. No pueden distinguir una diapositiva de
otro tema de la que dice ser; eso solo se ve mirando. Para esa parte:

```bash
python 09_AUTOMATION/revisar_capturas.py   # hoja HTML con todas las imágenes publicadas
# se abre, se marca lo que no cuadre y se descarga veredictos.json
python 09_AUTOMATION/vetar_fotogramas.py --veredictos veredictos.json
python 09_AUTOMATION/vetar_fotogramas.py --listar    # qué está vetado y por qué
```

El veto se guarda en la tabla `frame_vetos` **por concepto**: un mismo fotograma
puede servir a Judas Swing y no servir a PO3. Sobrevive a cualquier
regeneración del vault.

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
| `regenerar_vault.py` | 356 notas: 53 conceptos, 135 reglas, 54 operaciones, 55 cambios, 31 preguntas, 20 días de bootcamp, 7 índices y el comprobador |
| `verificar_vault.py` | 350 notas con frontmatter, 0 enlaces rotos, 0 imágenes rotas (las 6 restantes son portada e índices, que no llevan ficha) |
| `auditar_fotogramas.py` | 46 imágenes muestran su concepto, 6 son de contexto, 26 conceptos sin imagen |
| `fotogramas reutilizados` | **0**: 38 imágenes = 38 fotogramas distintos (antes 9 fotogramas se repetían en 2–3 notas) |
| `vetar_fotogramas.py --listar` | 21 vetos visuales, cada uno con su motivo y su concepto |
| **Revisión visual de las 38 publicadas** | 38 de 38 miradas una a una contra su definición; 0 sin revisar |
| `quartz build` | 817 archivos, grafo y búsqueda activos |
| **Anotaciones en navegador real** | Chrome headless: 14 secciones detectadas, anotación publicada y persistida en `localStorage` |
| **Sitio en producción** | 200 en `/`, en las notas y en los `.webp`; grafo y búsqueda presentes |
| Auditoría de contenido | ninguna cita > 246 caracteres; ningún dato personal; sin Reels |
| Imágenes | 38 WebP; la mayoría a 1200 px de ancho y sin la interfaz del gráfico |
| Repositorio local | sin vídeos, transcripciones, base ni modelos |

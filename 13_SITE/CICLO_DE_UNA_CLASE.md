# Qué pasa cuando Xavi publica una clase

Documento de referencia. Explica el camino completo desde que aparece un vídeo
en el canal hasta que su contenido está en el sitio publicado, **quién hace cada
paso** y **qué puede fallar sin que nadie se entere**.

Estado a 2026-11-15.

---

## 1. El camino, paso a paso

| # | Paso | Quién | Automático |
|---|---|---|---|
| 1 | Detecta el vídeo nuevo | Tarea programada de Claude Desktop → `sync_bootcamp.py` | sí |
| 2 | Descarga subtítulos `es-orig` + `info.json` | el mismo script, con `yt-dlp` | sí |
| 3 | Limpia el VTT a `.txt` + `.segments.json` | `build_transcripts.py` | sí |
| 4 | Indexa vídeo y segmentos en SQLite | `init_db.py` | sí |
| 5 | **Lee la transcripción y extrae conceptos, reglas, evidencia y cambios** | el agente de Claude Desktop, leyendo el texto | **no** |
| 6 | Añade lo extraído a `populate_kb.py` y hace `--merge` | el agente | **no** |
| 7 | Regenera el vault | `regenerar_vault.py` | **no** |
| 8 | Compila y publica | GitHub Actions, al hacer push a `main` | sí (pero lo dispara el push) |

Los pasos 1–4 los ejecuta la tarea programada sola. **Los pasos 5–7 no los hace
ningún proceso automático**: son el trabajo de análisis que hace el agente al
leer la transcripción, y sin ellos el sitio no cambia.

### La consecuencia práctica

Un vídeo nuevo puede estar **transcrito y a la vez invisible**, y ese es el
estado normal durante las horas (o días) que pasan entre el paso 4 y el 5. La
página del día lo dice explícitamente: *«Transcrita, pero aún sin trabajar»*.

Antes del 2026-11-15 ese estado se mostraba mal: el Día 21 salió publicado con
`confianza: explícito` y enlace al segundo 0 sin tener ni una fila de evidencia.
La regla ahora es de tres estados, no dos:

| Estado | `confianza` | Enlace al minuto | Qué dice la página |
|---|---|---|---|
| Sin transcripción | `no confirmado` | no | «Publicada y anunciada, pero todavía sin transcribir» |
| Transcrita, sin evidencia | `no confirmado` | no | «Transcrita, pero aún sin trabajar» |
| Con evidencia | `explícito` | sí | El contenido normal |

---

## 2. Dónde se rompía (y ya no)

Los tres fallos del 2026-11-15, con su causa. Se dejan escritos porque los tres
eran silenciosos: el reporte decía «OK» o el proceso salía con código 0.

### 2.1 `sync_bootcamp.py` no encontraba `yt-dlp`

Buscaba en `PATH`, en `~/.local/bin` y como módulo de Python. El único `yt-dlp`
del equipo está en `~/Documents/AutoDownloader/.venv/Scripts/yt-dlp.exe`, ruta
que **sí** conocía `frames_selectivos.py` pero no este script.

Resultado: cada ejecución diaria reportaba *«yt-dlp no está instalado»* y la
clase nueva se quedaba sin subtítulos — aunque el binario estuviera ahí y los
subtítulos existieran en YouTube. Pasó los días 2, 4, 6, 7, 12 y 15 de
noviembre. En los días 12 y 13 se descargaron a mano, que es como se disimuló.

Corregido: las dos listas de rutas son ahora la misma, y hay dos salidas más:
`09_AUTOMATION/.bin/` (relativa al proyecto) y la variable `YTDLP_BIN`.

### 2.1-bis. Y el entorno donde corre la tarea no es tu consola

El log del 15 de noviembre está escrito en rutas de `/sessions/quirky-exciting-
hypatia/mnt/TRADINGXAVIRUYRA`. La tarea programada **no** corre en tu consola de
Windows: Claude Desktop monta el proyecto en un sandbox Linux. Ahí `~` no es
`C:\Users\Asus` y el venv de AutoDownloader no existe, así que una ruta
absoluta de Windows no cruza la frontera.

Por eso la búsqueda empieza por `09_AUTOMATION/.bin/`, que es una ruta relativa
al proyecto — la misma idea que ya usaba `frames_selectivos.py` con `ffmpeg`.
En ese sandbox un `.exe` de Windows no sirve: lo que funciona es
`python -m pip install yt-dlp`, que es lo que se hizo a mano el día 12. El
mensaje de error ahora dice exactamente eso en vez de «no está instalado».

### 2.2 `build_transcripts.py` moría con el título del canal

Los títulos usan `：` (U+FF1A, dos puntos de ancho completo): *«Bootcamp Día 21：
Daily bias + DOL»*. Al imprimir ese nombre en una consola Windows con cp1252,
`UnicodeEncodeError` y el script abortaba. Los subtítulos estaban descargados y
la transcripción no se generaba.

Corregido: la impresión se sanea; el archivo en disco conserva el nombre real.

### 2.3 `init_db.py` perdía la clase entera por un índice

El único `con.commit()` estaba **después** de reconstruir `segments_fts`. Si ese
último paso fallaba —pasó al ejecutarse sobre un montaje 9p—, se revertía
también el catálogo y los segmentos recién insertados. Una clase completa
perdida por un índice que se puede reconstruir en un segundo.

Además, `main()` se llamaba sin `sys.exit`, así que el fallo terminaba en
**código 0** y `sync_bootcamp` lo reportaba como `init_db.py: OK`.

Corregido: el commit va antes del FTS, el índice es opcional y su fallo devuelve
código 2 con un aviso legible.

---

## 3. Qué se comprueba, y qué no

| Herramienta | Comprueba | Necesita |
|---|---|---|
| `verificar_vault.py` | frontmatter completo, enlaces `[[…]]`, imágenes en disco | nada |
| `auditar_fotogramas.py` | qué concepto ilustra cada imagen publicada | nada |
| `verificar_sitio.mjs` | 22 casos de uso sobre el sitio renderizado | Chrome + sitio servido |
| `revisar_capturas.py` | hoja HTML con todas las imágenes para revisar a ojo | nada |
| `sync_bootcamp.py` | que la comprobación diaria quedó registrada | red |

**Ninguno de ellos detecta lo único que de verdad puede quedarse atrás:** que
haya una clase transcrita a la que nadie le haya extraído conceptos. El único
que puede verlo es quien lee el reporte diario, o una consulta a la base:

```sql
SELECT cu.order_num, cu.lesson, COUNT(e.id) AS evidencias
FROM curriculum cu
LEFT JOIN videos v ON v.id = cu.video_id
LEFT JOIN evidence e ON e.video_id = v.id
GROUP BY cu.order_num
HAVING evidencias = 0;
```

Hoy devuelve los días **1, 3 y 21**.

---

## 4. El corte de cifras de la portada

La portada lleva una fecha de corte. Se calcula en cada generación y es
`MAX(upload_date)` de los vídeos **con evidencia**, no la del último vídeo
catalogado.

Con el criterio anterior (que aceptaba tener transcripción) el corte saltaba al
15 por el Día 21, que no aporta ninguna cifra. La portada habría dicho «corte 15»
con la última clase trabajada del 14, y las cifras de al lado no habrían
cuadrado con esa fecha.

---

## 5. Comandos

```bash
# ciclo diario (lo que ejecuta la tarea programada)
py -3.13 09_AUTOMATION/sync_bootcamp.py --download --process

# regenerar el sitio a mano
py -3.13 09_AUTOMATION/pipeline.py --solo-vault
py -3.13 09_AUTOMATION/verificar_vault.py

# compilar y probar en local
cd 13_SITE/quartz
npx quartz build -d ../../12_VAULT -o public
py -3.13 -m http.server 8899 --directory public
node 09_AUTOMATION/verificar_sitio.mjs http://127.0.0.1:8899 build
```

El tercer argumento `build` de `verificar_sitio.mjs` es necesario para servir
con `python -m http.server`: ese servidor no resuelve `/bootcamp/dia-13` sin
extensión y devuelve 404 aunque el archivo exista. GitHub Pages sí lo resuelve.

---

## 6. Lo que sigue sin automatizar

- **Extraer conceptos y reglas de una transcripción nueva.** Es lectura y
  criterio; hacerlo con una heurística sería inventar, que es justo lo que el
  proyecto prohíbe. La tarea de Claude Desktop lo hace al leer el texto.
  Decidido así el 2026-11-15: se queda como está.
- **Anotar fotogramas.** 695 marcos siguen sin anotación y no se publican como
  prueba visual. Para los conceptos sin imagen hay una tanda preparada (abajo).
- **Decidir si un fotograma ilustra un concepto.** La hoja presenta el material;
  la persona escribe qué ve. No hay veredicto automático.

## 6-bis. Publicación automática

`09_AUTOMATION/publicar_sitio.py` hace la cadena entera: regenerar, verificar,
comprobar que cambió algo, compilar y publicar. Se puede encadenar al ciclo
diario con `--publicar`:

```bash
py -3.13 09_AUTOMATION/sync_bootcamp.py --download --process --publicar
```

Para y avisa en dos casos, que es su razón de ser:

| Situación | Qué hace | Por qué |
|---|---|---|
| Hay cambios locales fuera de `12_VAULT/` | no publica, lista los archivos | mezclar trabajo en curso con una publicación automática es la forma más fácil de subir algo que no querías |
| El build local no compila | no publica, muestra el error | el deploy de GitHub Actions fallaría igual, pero el error quedaría en un log remoto con el commit ya hecho |

Si el vault no cambió, termina sin commit: no crea un commit vacío cada día.

## 6-ter. La tanda de los conceptos sin imagen

De los 26 conceptos sin ilustración, solo 9 se pueden fotografiar:

- 11 son `NOT USED`: RSI, MACD, Elliott… Xavi declara que no los usa, así que
  no hay nada suyo que ilustrar.
- 6 son de psicología: no se ven en un gráfico.
- Los 9 restantes: PD Array, Key Levels, PDH/PDL, Protected High/Low, Rejection
  Block, Cuentas de fondeo, Sesión de Nueva York, No News Monday, Bank Holiday.

```bash
python 09_AUTOMATION/revisar_capturas.py --tanda
# abre 09_AUTOMATION/.tmp/revision/tanda.html
python 09_AUTOMATION/vetar_fotogramas.py --anotar anotaciones.json
```

La hoja trae **49 fotogramas** de las clases que hablan de esos conceptos y que
nadie ha mirado. No es una lista de candidatos aprobados: hay que escribir qué
se ve.

De los 9, tres (Protected High/Low, Rejection Block, Cuentas de fondeo) no
tienen ningún fotograma sin revisar: sus clases ya están anotadas de arriba
abajo y ninguna anotación los menciona. Para esos tres no hay material sin
mirar; haría falta extraer fotogramas nuevos de los minutos donde se mencionan
en la transcripción.

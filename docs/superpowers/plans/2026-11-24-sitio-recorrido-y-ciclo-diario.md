# Sitio como recorrido y ciclo diario confiable — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar una versión congelada segura, convertir el sitio de archivo en recorrido de aprendizaje y, solo después, integrar bootcamp + reels en un único ciclo diario confiable.

**Architecture:** Tres fases secuenciales. Fase 0 corrige el timeout silencioso del publicador y congela el estado actual. Fase 1 reescribe los generadores para producir `00-empieza-aqui`, minuto real, ruta de conceptos, fotogramas honestos, comprobador con barras separadas y QA ampliado. Fase 2 añade estado/lock del ciclo e importación de reels citados sin tocar `videos`/`evidence` de YouTube. Todo se regenera desde SQLite; nadie edita notas a mano.

**Tech Stack:** Python 3.13 (`pytest`, `Pillow`), SQLite, Quartz 5 + plugins locales, Chrome headless vía CDP, `git commit -- 12_VAULT`, GitHub Actions.

**Spec:**
- `docs/superpowers/specs/2026-11-24-rediseno-sitio-recorrido-design.md`
- `docs/superpowers/specs/2026-11-24-tareas-automatizadas-bootcamp-reels-design.md`

## Global Constraints

- Cero inventiva: toda afirmación lleva `video_id`/`reel_code` + timestamp + cita + nivel `EXPLICITO|OBSERVADO|INFERIDO|NO CONFIRMADO`.
- Jerarquía de fuentes: bootcamp > vídeos educativos > reels.
- No borrar historial: `--merge`, nunca rebuild; reels antiguos quedan `in_window=0`, nunca `DELETE`.
- Publicar siempre al final del ciclo, nunca antes del análisis.
- Solo `git commit -- <rutas>`; **prohibido `git add -A`**. Para publicación automática: solo `12_VAULT`.
- Un timeout en cualquier fase del publicador ⇒ `rc != 0` y sin publicación.
- Sin `t=0s`, sin duración inventada: si no hay evidencia, botón «Ver clase completa»; si `duration_sec IS NULL`, «duración desconocida».
- Reels: solo nuevos desde `DfrZdVCMVWC` (2026-11-13); dudosos se descartan, no se publican; prohibido insertar `ig_<code>` en `videos` ni escribir en `evidence`.
- El resumen diario incluye hora exacta y modo de ejecución (programada vs al abrir la app).
- No ejecutar logins de Google ni guardar credenciales; no subir secretos a servicios externos.
- Responder en español; ante duda con Excel/CSV, examinar columnas/filtros y preguntar.
- Todo cambio se verifica con build + QA antes de seguir; `verificar_sitio.mjs` falla a propósito si aparece `t=0s`.

## Review Focus

Estas cinco entradas/situaciones no están cubiertas por un test en el código actual y son las más probables de romper la experiencia. Cada una tiene su test pinado en la tarea que la implementa:

1. **Timeout de `regenerar_vault.py`** → hoy el publicador dice «Build correcto» y `rc=0` aunque la fase murió; se pinza en Task 1 con `test_correr_timeout_es_fallo` y `test_timeout_en_fase_bloquea_publicacion`.
2. **`duration_sec=NULL` en días 28/29** → hoy imprime `0:00` y el QA lo acepta; se pinza en Task 4 con `test_duracion_desconocida_no_inventa_cero`.
3. **Captura con pie «no se ve» publicada como ilustración** → 5 notas lo hacen; se pinza en Task 5 con `test_veto_por_negacion` y `test_sin_pie_no_se_ve`.
4. **Reel dudoso o sin cita** → hoy podría filtrarse a la web; se pinza en Task 10 con `test_dudoso_se_descarta` y en Task 11 con `test_reel_sin_cita_no_se_importa`.
5. **Ejecución duplicada del ciclo sin novedades** → today duplica `sync_log` y publica de nuevo; se pinza en Task 9 con `test_idempotencia_sin_novedades`.

---

## File Structure (decisiones de límites)

| Archivo | Responsabilidad | Cambio |
|---|---|---|
| `09_AUTOMATION/publicar_sitio.py` | Único publicador: regenera, verifica, compila, commitea `12_VAULT`, push | **Modificar**: timeout → excepción, `rc!=0`, sin publicar; quitar `except` silencioso |
| `09_AUTOMATION/verificar_sitio.mjs` | QA en Chrome real sobre el sitio | **Modificar**: días desde el índice, `t=0s`, cobertura CORE, pies «no se ve» |
| `09_AUTOMATION/init_db.py` | Esquema SQLite | **Modificar**: añadir `concepto_relaciones`, `reel_items`, `reel_evidence` |
| `09_AUTOMATION/regenerar_vault.py` | Notas unitarias + portada + comprobador | **Modificar**: minutos reales, duración honesta, reparto de frames, barras, notas recortadas, `00-empieza-aqui.md`, contradicciones |
| `09_AUTOMATION/paginas_sitio.py` | Páginas de navegación | **Modificar**: `ruta.md`, tarjeta «Empieza aquí», `generar_reels()`, `ig_<code>` en enlaces |
| `13_SITE/quartz/quartz.config.yaml` | Plugins de Quartz | **Modificar**: desactivar `folder-page`, `graph`, `backlinks` |
| `13_SITE/quartz/quartz-plugins/{ficha-fuente,panel-avance,anotaciones}/dist/components/index.js` | Ficha de fuente y botones | **Modificar**: `IG:` → URL de Instagram con `?t=<seg>` |
| `09_AUTOMATION/ciclo_estado.py` | Estado atómico, lock, `run <FASE> -- <cmd>` | **Crear** |
| `09_AUTOMATION/importar_reels.py` | Importa reels citados a tablas propias | **Crear** |
| `09_AUTOMATION/validate_kb.py` | Validación de base | **Modificar**: checks de reels y relaciones |
| `13_SITE/README.md`, `13_SITE/CICLO_DE_UNA_CLASE.md` | Documentación operativa | **Modificar**: nuevo ciclo, `/reels/`, prefijo `IG:` |
| `tests/test_*.py` | Pruebas unitarias de los generadores | **Crear** |

---

## Fase 0 — Congelación segura

### Task 1: Eliminar el timeout silencioso del publicador

**Files:**
- Modify: `09_AUTOMATION/publicar_sitio.py:51-55,149-194`
- Test: `tests/test_publicar_sitio.py`

**Interfaces:**
- Consumes: `correr(cmd, cwd=BASE, timeout=1800)` existente en `publicar_sitio.py`.
- Produces: `correr()` lanza `TimeoutExpirado` (excepción propia) en vez de devolver un `CompletedProcess`; `main()` captura esa excepción en cada fase, imprime `FALLO por timeout al <fase>` y devuelve `1`.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_publicar_sitio.py`:
```python
import importlib.util
import os
import pytest

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "publicar_sitio.py")
spec = importlib.util.spec_from_file_location("publicar_sitio", RUTA)
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def test_correr_timeout_es_fallo(monkeypatch):
    class R:
        def __init__(self, *a, **kw):
            raise ps.subprocess.TimeoutExpired(["x"], 1)
    monkeypatch.setattr(ps.subprocess, "run", R)
    with pytest.raises(ps.TimeoutExpirado):
        ps.correr(["x"], timeout=1)


def test_timeout_en_fase_bloquea_publicacion(monkeypatch, capsys):
    # Simula que regenerar_vault agota el timeout y que nadie hace commit/push.
    monkeypatch.setattr(ps, "correr", lambda *a, **kw: (_ for _ in ()).throw(ps.TimeoutExpirado("regenerar", 1800)))
    commits = []
    monkeypatch.setattr(ps, "git", lambda *a, **kw: commits.append(a))
    rc = ps.main()
    assert rc == 1
    assert commits == []
    assert "FALLO por timeout" in capsys.readouterr().out
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_publicar_sitio.py -v`
Expected: FAIL — `AttributeError: module 'publicar_sitio' has no attribute 'TimeoutExpirado'`.

- [ ] **Step 3: Implementación mínima**

En `09_AUTOMATION/publicar_sitio.py`:
```python
class TimeoutExpirado(RuntimeError):
    """Una fase del pipeline agotó su límite de tiempo."""


def correr(cmd, cwd=BASE, timeout=1800):
    try:
        return subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired as e:
        raise TimeoutExpirado(f"{' '.join(cmd)} agotó {timeout}s") from e
```

En `main()`, reemplazar cada `r = correr(...)` por un bloque con manejo explícito. Para la fase de regeneración:
```python
    print("=== Regenerando el vault ===")
    try:
        r = correr(python + [os.path.join(BASE, "09_AUTOMATION", "regenerar_vault.py")])
    except TimeoutExpirado as e:
        print(f"FALLO por timeout al regenerar: {e}")
        return 1
```
Igual para verificación (`FALLO por timeout al verificar`) y build (`FALLO por timeout al compilar`). Los `git()` de commit/push también pasan dentro de `try/except TimeoutExpirado` con mensaje `FALLO por timeout al publicar`. `hay_cambios_fuera_del_vault()` y `hay_conflicto()` ya usan `git()` sin timeout explícito: envolver sus llamadas en el mismo `try` y devolver `3` con `FALLO por timeout al inspeccionar git`.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_publicar_sitio.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Verificación de integración**

Run: `python 09_AUTOMATION/publicar_sitio.py --simular`
Expected: termina sin el traceback `subprocess.TimeoutExpired` del 2026-11-24; si regeneración tarda >1800 s, imprime `FALLO por timeout al regenerar` y `rc=1`.

- [ ] **Step 6: Commit**

```bash
git add tests/test_publicar_sitio.py 09_AUTOMATION/publicar_sitio.py
git commit -m "Bloquear la publicación si una fase agota el timeout"
```

### Task 2: Congelar y publicar la versión conocida

**Files:**
- Sin código nuevo. Solo verificación y publicación selectiva.

**Interfaces:**
- Consumes: Task 1 (`publicar_sitio.py` con timeout corregido).
- Produces: `main` en GitHub Pages sirviendo el vault congelado; referencia de commit anotada en `10_REPORTS/congelamiento_2026-11-24.md`.

- [ ] **Step 1: Verificar el estado real de los 472 cambios**

Run:
```bash
git status --porcelain | wc -l
git status --porcelain -- 12_VAULT | wc -l
git diff --stat -- 12_VAULT/media | tail -3
```
Expected: `472` cambios totales; `458` en `12_VAULT`; los 52 `.webp` borrados del vault son los que faltan en disco (solo queda 1). **No restaurar media borrada a mano**: el pipeline la regenera desde SQLite en Task 5.

- [ ] **Step 2: Publicar con el publicador corregido**

Run: `python 09_AUTOMATION/publicar_sitio.py`
Expected: `Regenerando...`, `Verificando...`, `Build correcto.` o `Build local omitido`, `Publicado. GitHub Actions compilará y desplegará.` Si aparece `Sin credenciales de git`, `rc=5`: anotar PENDIENTE_DE_PUBLICAR y no afirmar deploy.

- [ ] **Step 3: Confirmar el deploy**

Run: `curl -sS -o /dev/null -w "%{http_code}\n" https://irvingramirez0.github.io/TRADINGXAVIRUYRA/`
Expected: `200`. Si el commit local no se pudo pushear, esperar a que el usuario lo haga desde su consola; no ejecutar login ni guardar credenciales.

- [ ] **Step 4: Documentar el congelamiento**

Crear `10_REPORTS/congelamiento_2026-11-24.md` con: hora exacta, `git rev-parse --short HEAD` antes y después, `rc` del publicador, código HTTP de producción y la frase literal de salida. Sin inventar datos.

- [ ] **Step 5: Commit**

```bash
git add 10_REPORTS/congelamiento_2026-11-24.md
git commit -m "Registrar la versión congelada antes del rediseño"
```

---

## Fase 1 — Rediseño del sitio como recorrido

### Task 3: Esquema para relaciones de conceptos y reels

**Files:**
- Modify: `09_AUTOMATION/init_db.py:23-170` (bloque `SCHEMA`)
- Test: `tests/test_init_db.py`

**Interfaces:**
- Consumes: `SCHEMA` existente y `main()` de `init_db.py`.
- Produces: tablas `concepto_relaciones(concepto_id, requiere_id, tipo)` con `tipo ∈ {'requiere','se_combina_con'}`; `reel_items` y `reel_evidence` con `PRIMARY KEY`/índices; script de migración idempotente para la BD ya existente.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_init_db.py`:
```python
import importlib.util
import os
import sqlite3

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "init_db.py")
spec = importlib.util.spec_from_file_location("init_db", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_esquema_incluye_tablas_nuevas():
    con = sqlite3.connect(":memory:")
    con.executescript(mod.SCHEMA)
    tablas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"concepto_relaciones", "reel_items", "reel_evidence"} <= tablas
    cols = {r[1] for r in con.execute("PRAGMA table_info(concepto_relaciones)")}
    assert cols == {"concepto_id", "requiere_id", "tipo"}
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_init_db.py -v`
Expected: FAIL — tablas no existen.

- [ ] **Step 3: Implementación mínima**

Añadir al final de `SCHEMA` en `09_AUTOMATION/init_db.py`:
```sql
CREATE TABLE IF NOT EXISTS concepto_relaciones (
    concepto_id INTEGER NOT NULL,
    requiere_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('requiere','se_combina_con')),
    PRIMARY KEY (concepto_id, requiere_id, tipo)
);

CREATE TABLE IF NOT EXISTS reel_items (
    code TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    date_utc TEXT,
    duration_sec INTEGER,
    tono TEXT,
    clasificacion TEXT NOT NULL CHECK(clasificacion IN ('RELEVANTE','IRRELEVANTE','DESCARTADO')),
    certainty TEXT NOT NULL,
    motivo TEXT,
    estado_sitio TEXT NOT NULL DEFAULT 'pendiente',
    in_window INTEGER NOT NULL DEFAULT 1,
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reel_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reel_code TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    quote TEXT NOT NULL,
    entity_tipo TEXT NOT NULL CHECK(entity_tipo IN ('concept','rule')),
    entity_id INTEGER NOT NULL,
    certainty TEXT NOT NULL,
    FOREIGN KEY(reel_code) REFERENCES reel_items(code),
    UNIQUE (reel_code, timestamp_sec, quote)
);
```
`init_db.py` ya ejecuta `con.executescript(SCHEMA)` sobre la BD existente; `CREATE TABLE IF NOT EXISTS` migrará sin borrar nada.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_init_db.py -v`
Expected: 1 PASS.

- [ ] **Step 5: Aplicar a la BD real y verificar integridad**

Run:
```bash
python 09_AUTOMATION/init_db.py
python 09_AUTOMATION/validate_kb.py | tail -3
```
Expected: `Sin fallos críticos.` y conteos iguales a los actuales (194 vídeos, 29 curriculum, 469 evidence).

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/init_db.py tests/test_init_db.py
git commit -m "Añadir tablas de relaciones y reels sin tocar datos existentes"
```

### Task 4: Minuto real y duración honesta en el bootcamp

**Files:**
- Modify: `09_AUTOMATION/paginas_sitio.py:126-204,265-490`
- Test: `tests/test_paginas_sitio.py`

**Interfaces:**
- Consumes: `con` de SQLite con `curriculum`, `videos`, `evidence`; `frontmatter()`, `escribir()`, `reloj()` de `paginas_sitio.py`.
- Produces: `minuto_clase(con, video_id) -> str` ('' si no hay evidencia citada); `duracion_clase(fila) -> str` ('duración desconocida' si `duration_sec IS NULL`); `datos_bootcamp()` incluye `timestamp` y `duracion_texto` por fila.

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_paginas_sitio.py`:
```python
import importlib.util
import os
import sqlite3

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "paginas_sitio.py")
spec = importlib.util.spec_from_file_location("paginas_sitio", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def bd(tiempo, duracion):
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE videos(id TEXT PRIMARY KEY, duration_sec INTEGER, upload_date TEXT, title TEXT, transcript_path TEXT);
    CREATE TABLE curriculum(order_num INTEGER, lesson TEXT, video_id TEXT, concepts TEXT, status TEXT, notes TEXT);
    CREATE TABLE evidence(id INTEGER, entity_type TEXT, entity_id INTEGER, video_id TEXT, timestamp_sec REAL, source_type TEXT);
    CREATE TABLE frames(id INTEGER, video_id TEXT);
    CREATE TABLE concepts(id INTEGER, name TEXT);
    CREATE TABLE rules(id INTEGER, name TEXT, first_seen_video TEXT);
    CREATE TABLE frame_vetos(frame_id INTEGER, concept_id INTEGER);
    """)
    con.execute("INSERT INTO videos VALUES('ABC',?, '20260101','Clase','t.txt')", (duracion,))
    con.execute("INSERT INTO curriculum VALUES(1,'Día 1 — X','ABC','','catalogado','')")
    if tiempo is not None:
        con.execute("INSERT INTO evidence VALUES(1,'concept',1,'ABC',?,'EXPLICITO')", (tiempo,))
    return con


def test_minuto_real_desde_evidencia():
    assert mod.minuto_clase(bd(754.0, 3600), "ABC") == "12:34"


def test_sin_evidencia_no_da_cero():
    assert mod.minuto_clase(bd(None, 3600), "ABC") == ""


def test_duracion_desconocida_no_inventa_cero():
    fila = mod.datos_bootcamp(bd(754.0, None))[0]
    assert mod.duracion_clase(fila) == "duración desconocida"
    assert fila["duracion"] == 0 or fila["duracion"] is None
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_paginas_sitio.py -v`
Expected: FAIL — `AttributeError: module 'paginas_sitio' has no attribute 'minuto_clase'`.

- [ ] **Step 3: Implementación mínima**

Añadir en `paginas_sitio.py`, después de `reloj()`:
```python
def minuto_clase(con, video_id):
    """Primer minuto citado con fuente explícita u observada; '' si no hay."""
    r = con.execute(
        "SELECT MIN(timestamp_sec) t FROM evidence "
        "WHERE video_id=? AND source_type IN ('EXPLICITO','OBSERVADO')",
        (video_id,),
    ).fetchone()
    if not r or r["t"] is None:
        return ""
    return reloj(r["t"])


def duracion_clase(fila):
    """Nunca convierte NULL en 0: eso produjo los '0:00' de los días 28/29."""
    d = fila.get("duracion")
    if d is None or d == 0:
        return "duración desconocida"
    return reloj(d)
```

En `datos_bootcamp()`, cada fila añade:
```python
"timestamp": minuto_clase(con, vid),
"duracion_texto": duracion_clase({"duracion": (v["duration_sec"] if v else None)}),
```

En `generar_bootcamp()`:
- El frontmatter de cada día lleva `"timestamp": f["timestamp"]` (no `"00:00"`).
- El bloque `> **Clase ... · Duración ...**` usa `f["duracion_texto"]` en vez de `meta_duracion`.
- El botón del índice deja de ser fijo:
```python
ts = f["timestamp"]
href = f'https://www.youtube.com/watch?v={f["video_id"]}'
if ts:
    seg = sum(int(x) * m for x, m in zip(reversed(ts.split(":")), [1, 60, 3600][-len(ts.split(":")):]))
    href += f"&t={seg}s"
    etiqueta = f"Ver en YouTube · {ts} ↗"
else:
    etiqueta = "Ver clase completa ↗"
```
Extraer `a_segundos(ts)` como función local para no repetir la conversión; reutilizarla en el frontmatter.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_paginas_sitio.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Regenerar y comprobar en el vault**

Run:
```bash
python 09_AUTOMATION/regenerar_vault.py >/dev/null
grep -R 'timestamp: "00:00"' 12_VAULT/bootcamp/ | wc -l
grep -R '0:00' 12_VAULT/bootcamp/dia-28.md 12_VAULT/bootcamp/dia-29.md
```
Expected: `0` minutos en cero; días 28/29 dicen «duración desconocida», nunca `0:00`.

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/paginas_sitio.py tests/test_paginas_sitio.py 12_VAULT/bootcamp/
git commit -m "Enlazar cada clase a su minuto real y no inventar duración"
```

### Task 5: Reparto de fotogramas y veto por negación

**Files:**
- Modify: `09_AUTOMATION/regenerar_vault.py:319-430,526-620`; `09_AUTOMATION/vetar_fotogramas.py:40-60`
- Test: `tests/test_fotogramas.py`

**Interfaces:**
- Consumes: `asignar_fotogramas(con, conceptos)`, `DUENO_FOTOGRAMAS`, `NEGACIONES`, `candidate_frames()`, `frame_is_annotated()` existentes.
- Produces: `asignar_fotogramas()` con prioridad `CORE > SUPPORTING > CONTEXTUAL` y multi-propiedad solo para CORE nombrado literalmente; `frame_vetos` con columna `entity_type`; `rellenar_vetos_heredados()` para migrar filas antiguas a `entity_type='concept'`.

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_fotogramas.py`:
```python
import importlib.util
import os
import sqlite3

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "regenerar_vault.py")
spec = importlib.util.spec_from_file_location("regenerar_vault", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_veto_por_negacion():
    assert mod.niega_concepto(
        "No hay etiquetas de FVG en pantalla",
        ["fair value gap", "fvg"],
        1,
        [("fair value gap", 1), ("fvg", 1)],
    ) is True


def test_core_gana_a_contextual():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE frames(id INTEGER, video_id TEXT, timestamp_sec REAL, path TEXT, description TEXT, analysis TEXT);
    CREATE TABLE evidence(id INTEGER, entity_type TEXT, entity_id INTEGER, frame_id INTEGER, video_id TEXT, timestamp_sec REAL, quote TEXT, source_type TEXT);
    CREATE TABLE concepts(id INTEGER, name TEXT, aliases TEXT, category TEXT, status TEXT, certainty TEXT);
    CREATE TABLE frame_vetos(frame_id INTEGER, concept_id INTEGER);
    INSERT INTO concepts VALUES(1,'FVG','fvg,fair value gap','CORE','vigente','EXPLICITO');
    INSERT INTO concepts VALUES(2,'Sesión de Londres','sesion de londres,london','CONTEXTUAL','vigente','EXPLICITO');
    INSERT INTO frames VALUES(734,'v',100,'x.jpg','NQ 5m. FVG de 5m marcado en el low','');
    INSERT INTO evidence VALUES(1,'concept',2,734,'v',100,'sesión','OBSERVADO');
    INSERT INTO evidence VALUES(2,'concept',1,734,'v',100,'FVG','EXPLICITO');
    """)
    conceptos = [{
        "id": 1, "name": "FVG", "alts": ["fvg", "fair value gap"],
        "alts_propias": ["fvg", "fair value gap"], "category": "CORE",
    }, {
        "id": 2, "name": "Sesión de Londres", "alts": ["sesión de londres", "london"],
        "alts_propias": ["sesión de londres", "london"], "category": "CONTEXTUAL",
    }]
    assert mod.asignar_fotogramas(con, conceptos)[734] == 1


def test_sin_pie_no_se_ve():
    # Una anotación que niega el concepto no debe dejar caption publicado.
    desc = "No se distingue el IFVG, muy alejado"
    assert mod.niega_concepto(
        desc, ["ifvg"], 3, [("ifvg", 3)]
    ) is True
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_fotogramas.py -v`
Expected: FAIL — `niega_concepto` no reconoce «No hay etiquetas de» ni «muy alejado»; `asignar_fotogramas` elige el CONTEXTUAL por tener `evidence` directa.

- [ ] **Step 3: Implementación mínima**

En `regenerar_vault.py`:
```python
NEGACIONES = (
    "no hay", "no se ve", "no verifica", "no muestra", "no identifica",
    "no aparece", "no aporta", "no se distingue", "no consta", "sin rótulo",
    "no hay rótulo", "no hay etiquetas de", "no se aprecia", "no permite ver",
    "no se observa", "muy alejado", "no muestra el concepto",
)
```

En `asignar_fotogramas()`, cambiar la tupla de peso para incluir prioridad de categoría:
```python
prioridad = {"CORE": 0, "SUPPORTING": 1, "CONTEXTUAL": 2}.get(c.get("category"), 3)
peso[fid][c["id"]] = (prioridad, ev, menciones, largo, rank)
...
def clave(cid):
    prio, ev, menciones, largo, rank = opciones[cid]
    return (-prio, -ev, -menciones, -largo, rank, cid)
```
Para multi-propiedad CORE: después de elegir `dueno[fid]`, si el `description` nombra literalmente más de un concepto CORE, devolver también esos IDs. Cambiar el tipo de retorno a `dict[int, set[int]]` y adaptar `build_media()`:
```python
duenos = DUENO_FOTOGRAMAS.get(fr["id"], {concepto["id"]})
if concepto["id"] not in duenos:
    continue
```
Mantener `set` para que el test existente `DUENO_FOTOGRAMAS.get(fr["id"], concepto["id"]) != concepto["id"]` se actualice al nuevo tipo en todas las call sites (buscar con `grep -n DUENO_FOTOGRAMAS`).

En `vetar_fotogramas.py`, ampliar la tabla con `ALTER TABLE`:
```python
columnas = {r[1] for r in con.execute("PRAGMA table_info(frame_vetos)")}
if "entity_type" not in columnas:
    con.execute("ALTER TABLE frame_vetos ADD COLUMN entity_type TEXT NOT NULL DEFAULT 'concept'")
```
y en `regenerar_vault.py:410` filtrar `AND entity_type='concept'` para no mezclar vetos de reglas.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_fotogramas.py -v`
Expected: 4 PASS.

- [ ] **Step 5: Regenerar y auditar**

Run:
```bash
python 09_AUTOMATION/regenerar_vault.py >/dev/null
python 09_AUTOMATION/auditar_fotogramas.py --detalle | tail -12
grep -Rl 'no se ve\|no se distingue\|muy alejado' 12_VAULT/conceptos/ 12_VAULT/reglas/ | wc -l
```
Expected: 0 pies confesivos publicados como ilustración; `auditar_fotogramas` muestra cobertura CORE con FVG/PO3/AMD.

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/regenerar_vault.py 09_AUTOMATION/vetar_fotogramas.py tests/test_fotogramas.py 12_VAULT/
git commit -m "Repartir fotogramas por prioridad CORE y vetar anotaciones negativas"
```

### Task 6: Ruta de conceptos por dependencia

**Files:**
- Modify: `09_AUTOMATION/paginas_sitio.py:498-545`
- Modify: `09_AUTOMATION/regenerar_vault.py:692-778` (niveles derivados en notas)
- Test: `tests/test_ruta_conceptos.py`

**Interfaces:**
- Consumes: tabla `concepto_relaciones` (Task 3); `conceptos_data(con)`; `escribir()`, `tarjeta()`, `lista_tarjetas()`.
- Produces: `generar_ruta_conceptos(con, slugs_concepto) -> int` que escribe `12_VAULT/conceptos/ruta.md` con 4 niveles; `nivel_concepto(con, id) -> int` calculado por dependencias (1–4).

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_ruta_conceptos.py`:
```python
import importlib.util
import os
import sqlite3

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "paginas_sitio.py")
spec = importlib.util.spec_from_file_location("paginas_sitio", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_niveles_por_dependencia():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE concepts(id INTEGER, name TEXT, aliases TEXT, category TEXT, definition TEXT, certainty TEXT, status TEXT, first_seen_video TEXT, first_seen_ts REAL);
    CREATE TABLE concepto_relaciones(concepto_id INTEGER, requiere_id INTEGER, tipo TEXT);
    INSERT INTO concepts VALUES(1,'Liquidez','','CORE','','EXPLICITO','vigente','',0);
    INSERT INTO concepts VALUES(2,'FVG','','CORE','','EXPLICITO','vigente','',0);
    INSERT INTO concepts VALUES(3,'IFVG','','CORE','','EXPLICITO','vigente','',0);
    INSERT INTO concepto_relaciones VALUES(2,1,'requiere');
    INSERT INTO concepto_relaciones VALUES(3,2,'requiere');
    """)
    assert mod.nivel_concepto(con, 1) == 1
    assert mod.nivel_concepto(con, 2) == 2
    assert mod.nivel_concepto(con, 3) == 3
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_ruta_conceptos.py -v`
Expected: FAIL — `AttributeError: 'paginas_sitio' has no attribute 'nivel_concepto'`.

- [ ] **Step 3: Implementación mínima**

En `paginas_sitio.py`:
```python
def nivel_concepto(con, concepto_id, _vistos=None):
    """1 + el máximo nivel de sus requisitos; 1 si no tiene."""
    _vistos = _vistos or set()
    if concepto_id in _vistos:
        return 1
    _vistos = _vistos | {concepto_id}
    reqs = [r[0] for r in con.execute(
        "SELECT requiere_id FROM concepto_relaciones "
        "WHERE concepto_id=? AND tipo='requiere'", (concepto_id,))]
    if not reqs:
        return 1
    return 1 + max(nivel_concepto(con, r, _vistos) for r in reqs)


def generar_ruta_conceptos(con, slugs_concepto):
    grupos = {1: [], 2: [], 3: [], 4: []}
    for c in con.execute("SELECT id, name, definition FROM concepts ORDER BY name"):
        s = slugs_concepto.get(c["id"])
        if not s:
            continue
        nivel = min(4, nivel_concepto(con, c["id"]))
        grupos[nivel].append((s, c))
    lineas = [frontmatter({
        "tipo": "indice", "title": "Ruta de conceptos", "titulo": "Ruta de conceptos",
        "confianza": "explícito", "estado": "vigente", "video": "", "timestamp": "",
    }), "", "# Ruta de conceptos", "",
        "Cuatro niveles. No saltes al siguiente sin el anterior: cada nota cita el vídeo y el minuto donde Xavi la usa.", ""]
    titulos = {1: "Nivel 1 — liquidez, swings y estructura de velas",
               2: "Nivel 2 — FVG, PO3, equilibrium",
               3: "Nivel 3 — IFVG, CISD, DOL",
               4: "Nivel 4 — sesiones, noticias, psicología"}
    for nivel in (1, 2, 3, 4):
        lineas += [f"## {titulos[nivel]}", ""]
        lineas.append(lista_tarjetas([
            tarjeta(f"../conceptos/{s}", c["name"], "", (c["definition"] or "")[:140])
            for s, c in grupos[nivel]
        ]) or "_Sin conceptos en este nivel todavía._")
        lineas.append("")
    escribir("conceptos", "ruta.md", "\n".join(lineas))
    return sum(len(g) for g in grupos.values())
```

Llamar desde `regenerar_vault.py:1190` dentro del `try` existente, justo después de `paginas_sitio.generar_indices(...)`:
```python
paginas_sitio.generar_ruta_conceptos(con, slugs_concepto)
```
En `generar_indices()`, insertar al principio de la sección de conceptos un enlace a `./ruta` con la etiqueta «Ruta por dependencia (empieza aquí)» y dejar CORE/CONTEXTUAL como «Filtro por categoría».

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_ruta_conceptos.py -v`
Expected: 1 PASS.

- [ ] **Step 5: Regenerar y verificar**

Run:
```bash
python 09_AUTOMATION/regenerar_vault.py >/dev/null
grep -c '^## Nivel' 12_VAULT/conceptos/ruta.md
```
Expected: `4`.

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/paginas_sitio.py 09_AUTOMATION/regenerar_vault.py tests/test_ruta_conceptos.py 12_VAULT/conceptos/
git commit -m "Añadir ruta de conceptos por dependencia nivel 1 a 4"
```

### Task 7: Página «Empieza aquí» derivada del mapa

**Files:**
- Modify: `09_AUTOMATION/regenerar_vault.py:1006-1145` (`generate_index`) y `main()`
- Test: `tests/test_empieza_aqui.py`

**Interfaces:**
- Consumes: `05_METHODOLOGY/00_MAPA_METODOLOGIA.md:104-170` (bloque `## 3. La metodología en una página`), `slugs_concepto`, `PREGUNTAS_MD`.
- Produces: `generar_empieza_aqui(slugs_concepto, fecha_corte) -> str` que escribe `12_VAULT/00-empieza-aqui.md`; `index.md` con esa página como **primera** tarjeta.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_empieza_aqui.py`:
```python
import importlib.util
import os

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "regenerar_vault.py")
spec = importlib.util.spec_from_file_location("regenerar_vault", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_bloque_extraido_no_copiado():
    bloque = mod.leer_bloque_metodologia()
    assert "### 3.1 Contexto y dirección" in bloque
    assert "### 3.7 Psicología" in bloque
    assert "## 4. Lo que NO forma parte" not in bloque


def test_empieza_aqui_primera_tarjeta(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "VAULT", str(tmp_path))
    os.makedirs(tmp_path, exist_ok=True)
    mod.generar_empieza_aqui({}, "2026-11-23")
    index = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert index.index("./00-empieza-aqui") < index.index("./bootcamp")
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_empieza_aqui.py -v`
Expected: FAIL — funciones no definidas.

- [ ] **Step 3: Implementación mínima**

En `regenerar_vault.py`:
```python
def leer_bloque_metodologia():
    """Lee solo §3 del mapa; nunca copia el texto a mano."""
    mapa = os.path.join(BASE, "05_METHODOLOGY", "00_MAPA_METODOLOGIA.md")
    txt = open(mapa, encoding="utf-8").read()
    ini = txt.index("## 3. La metodología en una página")
    fin = txt.index("\n## 4. ", ini)
    return txt[ini:fin].strip()


def generar_empieza_aqui(slugs_concepto, fecha_corte):
    bloque = leer_bloque_metodologia()
    lineas = ["---", 'tipo: indice', 'title: "Empieza aquí"',
              'titulo: "Empieza aquí"', 'confianza: "explícito"',
              'estado: "vigente"', 'video: ""', 'timestamp: ""',
              f'corte: "{fecha_corte}"', '---', "", "",
              "# Empieza aquí", "",
              f"**Corte de la metodología: {fecha_corte}.** Sigue este orden; cada etapa enlaza a la clase y al minuto donde se explica.", "",
              "> [!warning] La ruta, no el archivo",
              "> Esto es lo que Xavi hace, en el orden en que lo hace. El resto del sitio es la evidencia.", ""]
    for sec in ["4H/1H", "DOL", "liquidez", "PO3", "entradas", "gestión", "riesgo", "psicología"]:
        lineas += [f"- [[{slugs_concepto.get(sec, sec)}|{sec}]]" if sec in slugs_concepto else f"- {sec}"]
    lineas += ["", "## El mapa, paso a paso", "", bloque, "",
               "## Cómo leer los enlaces", "",
               "Cada botón «Ver en YouTube» abre el vídeo en el minuto citado. Si una etapa no tiene minuto, el botón dice «Ver clase completa»: no se inventa el segundo cero.", ""]
    with open(os.path.join(VAULT, "00-empieza-aqui.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas))
    # La portada existente se reescribe con esta tarjeta delante.
    generate_index_actual = os.path.join(VAULT, "index.md")
    if os.path.exists(generate_index_actual):
        txt = open(generate_index_actual, encoding="utf-8").read()
        tarjeta = '<a class="xr-tarjeta" href="./00-empieza-aqui"><span class="xr-tarjeta-titulo">Empieza aquí</span><span class="xr-tarjeta-desc">La metodología, en orden y con minuto.</span></a>'
        if tarjeta not in txt:
            txt = txt.replace('<div class="xr-tarjetas">', '<div class="xr-tarjetas">\n' + tarjeta, 1)
            open(generate_index_actual, "w", encoding="utf-8").write(txt)
```

Llamar en `main()` después de `generate_index(...)` con la fecha real:
```python
generar_empieza_aqui(slugs_concepto, estado.get("fecha_corte", ""))
```
Mejor: integrar la tarjeta directamente en la lista `secciones` de `generate_index()` para que se regenere limpio, y que el test de `tmp_path` pase sin depender de un `index.md` previo: añadir `("00-empieza-aqui", "Empieza aquí", "...")` como primer elemento.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_empieza_aqui.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Regenerar y verificar contenido**

Run:
```bash
python 09_AUTOMATION/regenerar_vault.py >/dev/null
head -20 12_VAULT/00-empieza-aqui.md
grep -n '00-empieza-aqui' 12_VAULT/index.md | head -2
```
Expected: bloque §3 completo, 8 etapas, tarjeta antes que `./bootcamp`.

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/regenerar_vault.py tests/test_empieza_aqui.py 12_VAULT/00-empieza-aqui.md 12_VAULT/index.md
git commit -m "Publicar el método como ruta principal desde el mapa real"
```

### Task 8: Comprobador honesto, notas recortadas y una sola fuente de cifras

**Files:**
- Modify: `09_AUTOMATION/regenerar_vault.py:692-778,1006-1145,1292-1410`
- Modify: `13_SITE/quartz/quartz.config.yaml:151-174`
- Test: `tests/test_comprobador.py`

**Interfaces:**
- Consumes: `comprobador_fuentes(con, slugs_concepto, slugs_regla, slugs_trade, slugs_cambio)` existente; `generate_conceptos()`.
- Produces: `comprobador_fuentes()` con `slugs_trade` y `slugs_cambio` reales (no `{}`); barras de conceptos/reglas/operaciones; sin bloque «Todo tiene fuente».

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_comprobador.py`:
```python
import importlib.util
import os
import sqlite3

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "regenerar_vault.py")
spec = importlib.util.spec_from_file_location("regenerar_vault", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_comprobador_muestra_operaciones_sin_cita():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE concepts(id INTEGER, name TEXT, certainty TEXT);
    CREATE TABLE rules(id INTEGER, name TEXT, certainty TEXT);
    CREATE TABLE evidence(id INTEGER, entity_type TEXT, entity_id INTEGER, video_id TEXT);
    CREATE TABLE videos(id TEXT);
    CREATE TABLE trades(id INTEGER, slug TEXT);
    CREATE TABLE changes(id INTEGER);
    INSERT INTO concepts VALUES(1,'FVG','EXPLICITO');
    INSERT INTO rules VALUES(1,'Regla','EXPLICITO');
    INSERT INTO evidence VALUES(1,'concept',1,'v1');
    INSERT INTO evidence VALUES(2,'rule',1,'v1');
    INSERT INTO videos VALUES('v1');
    INSERT INTO trades VALUES(1,'op-1');
    """)
    mod.VAULT = os.path.join(os.path.dirname(__file__), "_vault_tmp")
    os.makedirs(mod.VAULT, exist_ok=True)
    sin = mod.comprobador_fuentes(con, {1: 'fvg'}, {1: 'regla'}, {1: 'op-1'}, {})
    assert sin == 0
    texto = open(os.path.join(mod.VAULT, "comprobador.md"), encoding="utf-8").read()
    assert "0/1 operaciones con cita formal" in texto
    assert "Todo tiene fuente" not in texto
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_comprobador.py -v`
Expected: FAIL — el texto no contiene la barra de operaciones.

- [ ] **Step 3: Implementación mínima**

En `comprobador_fuentes()`, ampliar el panel:
```python
total_trades = con.execute("SELECT COUNT(*) n FROM trades").fetchone()["n"]
panel["barras"].append({
    "etiqueta": "Operaciones con cita formal (P&L autodeclarado)",
    "hecho": 0, "total": total_trades,
    "nota": "El P&L es autodeclarado: no hay extracto de cuenta que lo audite.",
})
```
Borrar el bloque `[!success] Todo tiene fuente` y sustituirlo por:
```python
if not filas:
    lineas += ["> [!note] Sin huecos en conceptos ni reglas",
               "> Las operaciones siguen siendo autodeclaradas: ver la barra de arriba.", ""]
```

En `main()` (Task 5 ya tocó esta zona), pasar los slugs reales:
```python
slugs_trade = {t["id"]: slug(t.get("slug") or str(t["id"]))
               for t in con.execute("SELECT id, slug FROM trades")}
slugs_cambio = {c["id"]: slug(f"cambio-{c['id']}")
                for c in con.execute("SELECT id FROM changes")}
sin_fuente = comprobador_fuentes(con, slugs_concepto, slugs_regla, slugs_trade, slugs_cambio)
```

En `generate_conceptos()`, reducir los apartados a `Definición`, `Cómo identificarlo`, `Errores comunes`, `Evidencia` (eliminar el blockquote duplicado). Los campos eliminados se conservan en la base; solo dejan de imprimirse.

En `13_SITE/quartz/quartz.config.yaml`: cambiar `enabled: true` → `false` para `folder-page` (línea ~151), `graph` (~160) y `backlinks` (~173). `explorer` y `search` siguen activos.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_comprobador.py -v`
Expected: 1 PASS.

- [ ] **Step 5: Regenerar y verificar**

Run:
```bash
python 09_AUTOMATION/regenerar_vault.py >/dev/null
grep -c '^## ' 12_VAULT/conceptos/liquidez.md
grep -n 'operaciones con cita formal' 12_VAULT/comprobador.md
grep -n 'Todo tiene fuente' 12_VAULT/comprobador.md | wc -l
```
Expected: ≤5 apartados, barra `0/54`, 0 ocurrencias de «Todo tiene fuente».

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/regenerar_vault.py 13_SITE/quartz/quartz.config.yaml tests/test_comprobador.py 12_VAULT/
git commit -m "Mostrar cobertura real y quitar ruido de las notas"
```

### Task 9: QA ampliado y contradicciones publicadas

**Files:**
- Modify: `09_AUTOMATION/verificar_sitio.mjs:60-176`
- Modify: `09_AUTOMATION/regenerar_vault.py` (nueva `generar_contradciones`)
- Test: `tests/test_verificar_sitio.py` (wrapper Python que comprueba el propio JS) y `tests/test_contradiciones.py`

**Interfaces:**
- Consumes: `check(nombre, cond)` y `abrir(url, perfil, puerto)` del propio `verificar_sitio.mjs`; tabla §5 de `05_METHODOLOGY/11_PREGUNTAS_ABIERTAS.md:396-405`.
- Produces: `verificar_sitio.mjs` con `DIAS` leído de `document.querySelectorAll('.xr-dia').length` y aserciones `t=0s`, CORE, pies «no se ve»; `12_VAULT/contradicciones.md` con 7 filas.

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_contradiciones.py`:
```python
import importlib.util
import os

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "regenerar_vault.py")
spec = importlib.util.spec_from_file_location("regenerar_vault", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_siete_contradicciones():
    mod.VAULT = os.path.join(os.path.dirname(__file__), "_vault_tmp")
    os.makedirs(mod.VAULT, exist_ok=True)
    n = mod.generar_contradciones()
    assert n == 7
    txt = open(os.path.join(mod.VAULT, "contradicciones.md"), encoding="utf-8").read()
    assert "9:30–10:30" in txt and "9:30–11:00" in txt
    assert "Vigente" in txt and "Histórica" in txt
```

`tests/test_verificar_sitio.py`:
```python
import os

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "verificar_sitio.mjs")
txt = open(RUTA, encoding="utf-8").read()


def test_qa_no_hardcodea_21():
    assert "===21" not in txt
    assert "xr-dia').length===21" not in txt
    assert "xr-dia').length" in txt


def test_qa_detecta_segundo_cero():
    assert "t=0s" in txt
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_verificar_sitio.py tests/test_contradiciones.py -v`
Expected: FAIL — `===21` presente; `generar_contradciones` no existe.

- [ ] **Step 3: Implementación mínima**

En `verificar_sitio.mjs`:
- Sustituir `check("bootcamp: 21 días listados", ...===21)` por:
```js
const nDias = await A.ev("document.querySelectorAll('.xr-dia').length")
check(`bootcamp: ${nDias} días listados`, nDias >= 29)
check("bootcamp: cada día enlaza a su página", await A.ev(`[...document.querySelectorAll('.xr-dia-titulo')].length===${nDias} && [...document.querySelectorAll('.xr-dia-titulo')].every(a=>/dia-[0-9][0-9]/.test(a.getAttribute('href')||''))`))
```
- Sustituir el `21` de la comprobación de títulos por `nDias`.
- Añadir después de la comprobación del Día 21:
```js
A=await abrir(u("/bootcamp/"),"qa-t0",9410)
check("bootcamp: ningún botón abre el segundo 0", await A.ev("![...document.querySelectorAll('.xr-boton-fuente')].some(a=>/[?&]t=0s/.test(a.href||''))"))
A.cerrar()
A=await abrir(u("/conceptos/"),"qa-core",9411)
check("conceptos: ruta por dependencia publicada", await A.ev("!!document.querySelector('a[href*=\"ruta\"]')"))
A.cerrar()
A=await abrir(u("/comprobador/"),"qa-comp",9412)
check("comprobador: dice 0/54 operaciones con cita formal", await A.ev("/0\\/\\d+ operaciones con cita formal/.test(document.body.textContent)"))
check("comprobador: no dice 'Todo tiene fuente'", await A.ev("!/Todo tiene fuente/.test(document.body.textContent)"))
A.cerrar()
```
Añadir comprobación de pies «no se ve» recorriendo las notas CORE publicadas con `fetch` sobre el build local.

En `regenerar_vault.py`, nueva función que parsea la tabla de contradicciones:
```python
def generar_contradciones():
    txt = open(PREGUNTAS_MD, encoding="utf-8").read()
    ini = txt.index("## 5. Contradicciones documentadas")
    fin = txt.index("\n**Regla:**", ini)
    filas = [l for l in txt[ini:fin].splitlines()
             if l.startswith("| ") and not l.startswith("|---") and "Tema" not in l]
    lineas = ["---", 'tipo: indice', 'title: "Contradicciones"',
              'titulo: "Contradicciones"', 'confianza: "no confirmado"',
              'estado: "vigente"', 'video: ""', 'timestamp: ""', '---', "",
              "# Contradicciones documentadas", "",
              "Dos versiones conviven. Ninguna se borra: se marca cuál manda hoy.", "",
              "| Tema | Vigente | Histórica | Estado |", "|---|---|---|---|"]
    for f in filas:
        celdas = [c.strip() for c in f.strip("|").split("|")]
        if len(celdas) >= 4:
            lineas.append(f"| {celdas[0]} | {celdas[2]} | {celdas[1]} | {celdas[3]} |")
    lineas += ["", "Ver la clase que resuelve cada tensión desde la ficha de la regla correspondiente.", ""]
    with open(os.path.join(VAULT, "contradicciones.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas))
    return len(filas)
```
Llamarla en `main()` dentro del `try` de páginas de navegación. Añadir `("contradicciones","Contradicciones","...")` al listado `secciones` de `generate_index()` para que tenga tarjeta, manteniendo 8 tarjetas (la nueva «Empieza aquí» desplaza al panel de cifras a segundo plano).

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_verificar_sitio.py tests/test_contradiciones.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Verificar QA en local con Chrome**

Run:
```bash
cd 13_SITE/quartz && npx quartz build --serve -d ../../12_VAULT >/tmp/quartz.log 2>&1 &
node 09_AUTOMATION/verificar_sitio.mjs http://127.0.0.1:8080
```
Expected: `NN/NN comprobaciones OK` con 29 días y sin `t=0s`. Si no hay Chrome, registrar `AUDITORIA_DIFERIDA` y no afirmar verificación.

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/verificar_sitio.mjs 09_AUTOMATION/regenerar_vault.py tests/test_verificar_sitio.py tests/test_contradiciones.py 12_VAULT/
git commit -m "Ampliar QA a 29 días, minuto real y contradicciones"
```

### Task 10: Publicar la fase 1 y verificar en producción

**Files:**
- Sin código nuevo.

**Interfaces:**
- Consumes: Tasks 3–9 completos, publicador corregido (Task 1).
- Produces: versión de rediseño en `https://irvingramirez0.github.io/TRADINGXAVIRUYRA`.

- [ ] **Step 1: Build y QA local**

Run:
```bash
python 09_AUTOMATION/regenerar_vault.py >/dev/null
python 09_AUTOMATION/verificar_vault.py | tail -5
cd 13_SITE/quartz && npx quartz build -d ../../12_VAULT -o public
cd ../.. && node 09_AUTOMATION/verificar_sitio.mjs http://localhost:8080
```
Expected: 0 enlaces rotos, 0 imágenes rotas, build correcto, QA OK.

- [ ] **Step 2: Publicar**

Run: `python 09_AUTOMATION/publicar_sitio.py`
Expected: `Publicado.` o `Sin credenciales` documentado como pendiente.

- [ ] **Step 3: Verificar en producción**

Run:
```bash
for u in / /00-empieza-aqui /bootcamp/ /conceptos/ruta /comprobador /contradicciones; do
  printf "%s " "$u"; curl -sS -o /dev/null -w "%{http_code}\n" "https://irvingramirez0.github.io/TRADINGXAVIRUYRA$u"
done
```
Expected: `200` en las seis rutas (el `/00-empieza-aqui` antes daba 404).

- [ ] **Step 4: Commit de cierre si queda documentación**

```bash
git add 13_SITE/README.md 13_SITE/CICLO_DE_UNA_CLASE.md
git commit -m "Actualizar documentación del sitio tras el rediseño"
```

---

## Fase 2 — Ciclo automático

### Task 11: Estado atómico y lock del ciclo

**Files:**
- Create: `09_AUTOMATION/ciclo_estado.py`
- Test: `tests/test_ciclo_estado.py`

**Interfaces:**
- Consumes: `.work/ciclo/` (nuevo), `10_REPORTS/ciclo_<fecha>.md`.
- Produces: CLI `python 09_AUTOMATION/ciclo_estado.py run <FASE> -- <cmd>` con `rc`, últimas 40 líneas útiles, lock con PID/timestamp, `claim()` y `finish()`; `estado.json` atómico vía `os.replace`.

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_ciclo_estado.py`:
```python
import importlib.util
import json
import os

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "ciclo_estado.py")
spec = importlib.util.spec_from_file_location("ciclo_estado", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_estado_atomico(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "ESTADO", str(tmp_path / "estado.json"))
    mod.guardar_estado({"lote_id": "2026-11-24", "fase": "PREFLIGHT"})
    assert json.loads((tmp_path / "estado.json").read_text())["lote_id"] == "2026-11-24"
    assert not list(tmp_path.glob("*.tmp"))


def test_lock_activo_no_mata_proceso(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "LOCK", str(tmp_path / "ciclo.lock"))
    (tmp_path / "ciclo.lock").write_text(json.dumps({"pid": 999999, "ts": "2026-11-24T00:00:00"}))
    assert mod.lock_activo() is True
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_ciclo_estado.py -v`
Expected: FAIL — módulo no existe.

- [ ] **Step 3: Implementación mínima**

`09_AUTOMATION/ciclo_estado.py`:
```python
#!/usr/bin/env python3
"""Estado atómico y lock para el ciclo diario. Sin heurísticas de extracción."""
import argparse
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(BASE, ".work", "ciclo")
ESTADO = os.path.join(DIR, "estado.json")
LOCK = os.path.join(DIR, "ciclo.lock")
REPORTES = os.path.join(BASE, "10_REPORTS")
FASES = ("PREFLIGHT", "BOOTCAMP", "REELS", "AUDITORIA", "PUBLICACION", "CIERRE")


def guardar_estado(datos):
    os.makedirs(DIR, exist_ok=True)
    tmp = ESTADO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, ESTADO)


def lock_activo():
    if not os.path.exists(LOCK):
        return False
    try:
        info = json.load(open(LOCK, encoding="utf-8"))
        pid = int(info["pid"])
    except Exception:
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if h:
            ctypes.windll.kernel32.CloseHandle(h)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def claim(lote_id):
    if lock_activo():
        return False
    os.makedirs(DIR, exist_ok=True)
    with open(LOCK + ".tmp", "w", encoding="utf-8") as fh:
        json.dump({"pid": os.getpid(), "ts": lote_id, "lote_id": lote_id}, fh)
    os.replace(LOCK + ".tmp", LOCK)
    guardar_estado({"lote_id": lote_id, "fases": {f: {"rc": None} for f in FASES}})
    return True


def lineas_utiles(texto, n=40):
    return [l for l in texto.splitlines() if l.strip()][-n:]


def run(fase, cmd):
    os.makedirs(REPORTES, exist_ok=True)
    try:
        p = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        rc, salida = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired as e:
        rc, salida = 1, f"FALLO por timeout en {fase}: {e}"
    estado = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}
    estado.setdefault("fases", {})[fase] = {
        "rc": rc, "ultimas_lineas": lineas_utiles(salida),
        "hora": subprocess.check_output(["powershell", "-NoProfile", "-Command",
                                         "Get-Date -Format o"], text=True).strip(),
    }
    guardar_estado(estado)
    for l in estado["fases"][fase]["ultimas_lineas"]:
        print(l)
    return rc
```

Añadir `finish(lote_id, resumen)` que escribe el markdown en `10_REPORTS/ciclo_<lote_id>.md` con hora exacta y modo (`al abrir la app` si `CLAUDE_DESKTOP_OPEN=1`, si no `programada`), y borra el lock solo si el PID coincide. CLI con `argparse`: `run`, `claim`, `finish`.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_ciclo_estado.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Probar el wrapper con un comando real**

Run: `python 09_AUTOMATION/ciclo_estado.py run PREFLIGHT -- python -c "print('ok')"`
Expected: imprime `ok`, crea `.work/ciclo/estado.json` con `rc=0`. **No borrar** el JSONL histórico ni el lock ajeno.

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/ciclo_estado.py tests/test_ciclo_estado.py
git commit -m "Añadir estado atómico y lock para el ciclo diario"
```

### Task 12: Importación de reels citados sin contaminar YouTube

**Files:**
- Create: `09_AUTOMATION/importar_reels.py`
- Modify: `09_AUTOMATION/validate_kb.py`
- Modify: `09_AUTOMATION/paginas_sitio.py` (`generar_reels`), `09_AUTOMATION/regenerar_vault.py` (llamada)
- Modify: 3 × `13_SITE/quartz/quartz-plugins/*/dist/components/index.js`
- Test: `tests/test_reels.py`

**Interfaces:**
- Consumes: `reel_items`, `reel_evidence` (Task 3); JSONL de `01_CATALOG/`; `conceptos_data()`, `slug()`, `frontmatter()`, `escribir()`.
- Produces: `importar_reels(con, datos) -> dict` con altas `{relevantes, descartados, irrelevantes}`; `generar_reels(con)` en `paginas_sitio.py`; `urlYoutube()` extendido con `IG:`.

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_reels.py`:
```python
import importlib.util
import os
import sqlite3

BASE = os.path.join(os.path.dirname(__file__), "..")
spec = importlib.util.spec_from_file_location("importar_reels", os.path.join(BASE, "09_AUTOMATION", "importar_reels.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def bd():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE reel_items(code TEXT PRIMARY KEY, url TEXT, date_utc TEXT, duration_sec INTEGER, tono TEXT, clasificacion TEXT, certainty TEXT, motivo TEXT, estado_sitio TEXT DEFAULT 'pendiente', in_window INTEGER DEFAULT 1);
    CREATE TABLE reel_evidence(id INTEGER PRIMARY KEY AUTOINCREMENT, reel_code TEXT, timestamp_sec REAL, quote TEXT, entity_tipo TEXT, entity_id INTEGER, certainty TEXT, UNIQUE(reel_code,timestamp_sec,quote));
    CREATE TABLE concepts(id INTEGER, name TEXT);
    CREATE TABLE rules(id INTEGER, name TEXT);
    CREATE TABLE segments(video_id TEXT, start_sec REAL, end_sec REAL, text TEXT);
    CREATE TABLE videos(id TEXT);
    INSERT INTO concepts VALUES(1,'FVG');
    INSERT INTO rules VALUES(1,'Regla');
    """)
    return con


def test_relevantes_y_dudosos():
    datos = [{
        "code": "ABC123", "url": "https://instagram.com/reel/ABC123/",
        "date_utc": "2026-11-14", "tono": "dudoso", "clasificacion": "DUDOSO",
        "certainty": "NO CONFIRMADO", "motivo": "promesa de payout",
        "evidencia": [{"timestamp_sec": 12, "quote": "gana 10k", "entity_name": "FVG"}],
    }, {
        "code": "XYZ789", "url": "https://instagram.com/reel/XYZ789/",
        "date_utc": "2026-11-15", "tono": "serio", "clasificacion": "RELEVANTE",
        "certainty": "EXPLICITO", "motivo": "",
        "evidencia": [{"timestamp_sec": 34, "quote": "el FVG se valida en 5m", "entity_name": "FVG"}],
    }]
    r = mod.importar_reels(bd(), datos)
    assert r["descartados"] == 1
    assert r["relevantes"] == 1


def test_reel_sin_cita_no_se_importa():
    datos = [{"code": "NOSI", "clasificacion": "RELEVANTE", "certainty": "EXPLICITO", "evidencia": []}]
    con = bd()
    r = mod.importar_reels(con, datos)
    assert r["relevantes"] == 0
    assert con.execute("SELECT COUNT(*) FROM reel_evidence").fetchone()[0] == 0
    assert con.execute("SELECT clasificacion FROM reel_items WHERE code='NOSI'").fetchone()[0] == "DESCARTADO"
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_reels.py -v`
Expected: FAIL — módulo no existe.

- [ ] **Step 3: Implementación mínima**

`09_AUTOMATION/importar_reels.py`:
```python
#!/usr/bin/env python3
"""Importa reels citados a tablas propias. Nunca escribe en videos/evidence."""
import argparse
import json
import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "07_KNOWLEDGE_BASE", "xavi_ruyra.db")
CORTE = "DfrZdVCMVWC"  # 2026-11-13, decisión del usuario 2026-11-24
ENTIDADES = {"concept": "concepts", "rule": "rules"}


def normaliza(s):
    return " ".join((s or "").lower().split())


def importar_reels(con, datos):
    out = {"relevantes": 0, "descartados": 0, "irrelevantes": 0}
    orden = {c: i for i, c in enumerate(
        [r[0] for r in con.execute(
            "SELECT code FROM reel_items ORDER BY date_utc DESC")])}
    if CORTE not in orden:
        orden[CORTE] = -1
    for d in datos:
        code = d.get("code", "")
        clas = d.get("clasificacion", "DESCARTADO")
        razon = str(d.get("motivo", ""))
        ev = [e for e in d.get("evidencia", [])
              if normaliza(e.get("quote")) and e.get("timestamp_sec") is not None]
        if clas == "DUDOSO" or (clas == "RELEVANTE" and not ev):
            clas = "DESCARTADO"
        if d.get("tono") == "dudoso" or "payout" in razon.lower():
            clas = "DESCARTADO"
        if clas == "RELEVANTE" and orden.get(code, 10**6) < orden[CORTE]:
            clas = "DESCARTADO"
            razon = "anterior al corte " + CORTE
        con.execute(
            "INSERT OR REPLACE INTO reel_items(code,url,date_utc,duration_sec,tono,clasificacion,certainty,motivo,in_window) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (code, d.get("url", ""), d.get("date_utc", ""), d.get("duration_sec"),
             d.get("tono", ""), clas, d.get("certainty", "NO CONFIRMADO"), razon,
             1 if orden.get(code, 10**6) <= orden[CORTE] else 0))
        if clas == "RELEVANTE":
            for e in ev:
                nombre = e.get("entity_name", "")
                fila = con.execute("SELECT id FROM concepts WHERE name=?", (nombre,)).fetchone()
                tipo = "concept"
                if not fila:
                    fila = con.execute("SELECT id FROM rules WHERE name=?", (nombre,)).fetchone()
                    tipo = "rule"
                if not fila:
                    continue
                con.execute(
                    "INSERT OR IGNORE INTO reel_evidence(reel_code,timestamp_sec,quote,entity_tipo,entity_id,certainty) "
                    "VALUES(?,?,?,?,?,?)",
                    (code, e["timestamp_sec"], e["quote"], tipo, fila[0],
                     e.get("certainty", "OBSERVADO")))
            out["relevantes"] += 1
        else:
            out["descartados" if clas == "DESCARTADO" else "irrelevantes"] += 1
    con.commit()
    return out
```
CLI: `--import <ruta.json>` lee el JSON, valida que sea lista, llama a `importar_reels`, imprime el resumen; nunca ejecuta `DELETE`.

En `paginas_sitio.py`, `generar_reels(con)` escribe `12_VAULT/reels/index.md` y una nota por reel relevante con `tipo: reel`, `video: IG:<code>`, `timestamp` en `MM:SS`, `fuente_url`, cita enlazada al concepto/regla existente. Sin conceptos ni reglas nuevas. Se llama desde `regenerar_vault.py:main()` dentro del `try` de navegación.

En los 3 plugins, sustituir `urlYoutube`:
```javascript
function urlYoutube(video, ts) {
  if (!video) return null
  const seg = aSegundos(ts)
  if (String(video).startsWith("IG:")) {
    const code = String(video).slice(3)
    const base = `https://www.instagram.com/reel/${encodeURIComponent(code)}/`
    return seg === null ? base : `${base}?t=${seg}s`
  }
  const base = `https://www.youtube.com/watch?v=${encodeURIComponent(video)}`
  return seg === null ? base : `${base}&t=${seg}s`
}
```
Y la etiqueta del botón: si `IG:`, «Ver en Instagram»; si no, la actual. Actualizar los mismos 3 bloques `TIPOS` con `reel: "Reel"`.

En `validate_kb.py`, añadir antes del `RESULTADO`:
```python
print("\n== REELS ==")
for row in cur.execute("SELECT r.code, r.clasificacion, COUNT(e.id) n FROM reel_items r LEFT JOIN reel_evidence e ON e.reel_code=r.code GROUP BY r.code"):
    if row[1] == "RELEVANTE" and row[2] == 0:
        failures.append(f"Reel {row[0]} relevante sin cita")
print(f"Reels citados: {scalar(cur, 'SELECT COUNT(DISTINCT reel_code) FROM reel_evidence')}")
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_reels.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Verificar que no se contaminó YouTube**

Run:
```bash
python -c "import sqlite3; c=sqlite3.connect('07_KNOWLEDGE_BASE/xavi_ruyra.db'); print(c.execute(\"SELECT COUNT(*) FROM videos WHERE id LIKE 'ig_%'\").fetchone()[0])"
```
Expected: `0`.

- [ ] **Step 6: Commit**

```bash
git add 09_AUTOMATION/importar_reels.py 09_AUTOMATION/validate_kb.py 09_AUTOMATION/paginas_sitio.py 09_AUTOMATION/regenerar_vault.py 13_SITE/quartz/quartz-plugins tests/test_reels.py 12_VAULT/reels/
git commit -m "Importar reels citados en tablas propias y publicarlos en /reels/"
```

### Task 13: Prompt maestro y cierre del ciclo

**Files:**
- Modify: `13_SITE/README.md`, `13_SITE/CICLO_DE_UNA_CLASE.md`
- Create: `10_REPORTS/prompt-ciclo-diario.md`

**Interfaces:**
- Consumes: Tasks 11–12, spec `e6eca19`.
- Produces: texto literal del prompt de Claude Desktop con `PREFLIGHT → BOOTCAMP → REELS → AUDITORÍA CONDICIONAL → PUBLICACIÓN → CIERRE`, y documentación actualizada.

- [ ] **Step 1: Escribir el prompt maestro**

`10_REPORTS/prompt-ciclo-diario.md` debe contener, en español y sin inventar datos:

```markdown
# Ciclo diario — bootcamp + reels + sitio

Ejecuta en este orden, con `python 09_AUTOMATION/ciclo_estado.py run <FASE> -- <cmd>` y registrando rc y líneas significativas:

1. PREFLIGHT: `claim` con lote_id = fecha local exacta; si hay lock activo, avisa y termina sin matar procesos; detecta conflictos `UU|AA|DD|AU|UA|DU|UD`; ante `disk I/O error` conserva el journal, nunca borres la BD.
2. BOOTCAMP: `python 09_AUTOMATION/sync_bootcamp.py --download --process` (un reintento para red/429/5xx/disk I/O). Como máximo una clase nueva por ejecución. Sin clase nueva, escribe «SIN CLASE NUEVA — metodología intacta» y no ejecutes populate_kb. Con clase, analiza con cita (`video_id` + timestamp + cita + certeza), escribe los 8 documentos de 05_METHODOLOGY y ejecuta `populate_kb.py --merge` NUNCA sin --merge; usa VIDEO_DATES con fecha real porque TODAY está fijo. Luego validate_kb, PRAGMA integrity_check y build_search_index solo si cambiaron anotaciones. Nada de esto se publica todavía.
3. REELS: solo reels posteriores a DfrZdVCMVWC (2026-11-13). Descarta dudosos, sin cita o con promesas de payout; no los listes para revisión. Hasta 4 por ejecución, con `instagram_reels_tono.py --queue` como prioridad, no veredicto. Importa con `python 09_AUTOMATION/importar_reels.py --import .work/ciclo/reels_<fecha>.json`. Nunca escribas en videos ni evidence de YouTube.
4. AUDITORÍA CONDICIONAL: solo si hubo clase nueva o reels aceptados: `verificar_vault.py`, `auditar_fotogramas.py --detalle`, `revisar_capturas.py --tanda` (publica solo lo anotado) y, con node + Chrome, `node 09_AUTOMATION/verificar_sitio.mjs <url> build`. Sin node/Chrome escribe AUDITORIA_DIFERIDA, no afirmes verificación.
5. PUBLICACIÓN: `python 09_AUTOMATION/publicar_sitio.py` al final de cada ciclo. Interpreta rc y línea: 0 + «Publicado» = PUBLICADO; 0 + «El vault no cambió» = SIN CAMBIOS; 5 + «Sin credenciales» = commit local sin deploy; 3 = bloqueado; timeout = FALLO por timeout, sin publicar. Nunca copies solo la última línea.
6. CIERRE: `finish` con clase, reels[], auditoria, publicacion y ruta del reporte. Incluye siempre la hora exacta y si fue al abrir la app o programada. Si no hay clase, reels aceptados ni cambios en el vault, di «nada que publicar».

Reglas: no git add -A, no borrar historial, no inventar minutos ni duraciones, no publicar contenido sin analizar, no preguntar salvo ante decisiones nuevas, no ejecutar logins de Google ni guardar credenciales.
```

- [ ] **Step 2: Actualizar documentación**

En `13_SITE/README.md`, sustituir la sección 「Qué incluye el vault」 para incluir `/reels/`, `00-empieza-aqui`, `conceptos/ruta`, `contradicciones`, y corregir el número de clases de 21 a 29 en la tabla de secciones (línea 24). En `13_SITE/CICLO_DE_UNA_CLASE.md`, reemplazar los «pasos 5–9 manuales» por el ciclo real de 6 fases y eliminar la afirmación obsoleta de que faltan evidencias en días 1, 3 y 21.

- [ ] **Step 3: Verificar el prompt con el spec**

Run: comparar el prompt con las secciones §2–§4 del spec `e6eca19`: seis fases, corte `DfrZdVCMVWC`, dudosos descartados, rc 5 no exit, hora y modo en el reporte. Sin comandos nuevos de login.

- [ ] **Step 4: Commit**

```bash
git add 13_SITE/README.md 13_SITE/CICLO_DE_UNA_CLASE.md 10_REPORTS/prompt-ciclo-diario.md
git commit -m "Documentar el ciclo diario único y el prompt de Desktop"
```

### Task 14: Verificación final y cierre

**Files:**
- Sin código nuevo.

**Interfaces:**
- Consumes: Tasks 1–13 completos.
- Produces: confirmed deployment and honest report.

- [ ] **Step 1: Ejecutar todos los tests**

Run: `python -m pytest tests/ -v`
Expected: todos PASS (≥16 casos).

- [ ] **Step 2: Regenerar, verificar, compilar, publicar**

Run:
```bash
python 09_AUTOMATION/regenerar_vault.py
python 09_AUTOMATION/verificar_vault.py
python 09_AUTOMATION/validate_kb.py
cd 13_SITE/quartz && npx quartz build -d ../../12_VAULT -o public
cd ../.. && python 09_AUTOMATION/publicar_sitio.py
```
Expected: 0 enlaces rotos, 0 imágenes rotas, sin fallos críticos, build correcto, `Publicado.` (o `rc=5` documentado).

- [ ] **Step 3: Confirmar QA en producción**

Run: `node 09_AUTOMATION/verificar_sitio.mjs`
Expected: `NN/NN comprobaciones OK` con 29 días, sin `t=0s`, `/00-empieza-aqui` 200.

- [ ] **Step 4: Reporte final**

Crear `10_REPORTS/cierre-2026-11-24.md` con: hora exacta, commit final, resultados de los 16+ tests, QA en producción, lo que queda pendiente de anotación manual y la frase exacta de la salida del publicador. Nada de afirmaciones sin evidencia.

- [ ] **Step 5: Commit**

```bash
git add 10_REPORTS/cierre-2026-11-24.md
git commit -m "Cerrar el rediseño y el ciclo con verificación en producción"
```

---

## Self-Review

- **Spec coverage:** Fase 0 (timeout + congelación) → Tasks 1–2. N1 → Task 7. N2 → Task 4 + Task 9. N3 → Task 6. N4 → Task 5. N5/N6/N7 → Task 8. N8 → Task 8 + Task 9. N9 → Task 9. N10/N11 → orden de fases. D1–D6 → Tasks 11–13. Sin huecos.
- **Placeholders:** sin TBD/TODO; cada paso incluye comando o código concreto.
- **Type consistency:** `minuto_clase`, `duracion_clase`, `nivel_concepto`, `generar_ruta_conceptos`, `generar_empieza_aqui`, `generar_contradciones`, `importar_reels`, `guardar_estado`, `lock_activo` se definen una sola vez y se usan con la misma firma en las tareas posteriores. `DUENO_FOTOGRAMAS` cambia de `dict[int,int]` a `dict[int,set[int]]` en Task 5 y todas sus call sites se actualizan en esa misma tarea.
- **Review Focus:** los cinco riesgos están pinados en Tasks 1, 4, 5, 12 y 11 respectivamente, con tests ejecutables.
- **Orden:** Fase 1 se publica (Task 10) antes de empezar la Fase 2, cumpliendo N10.

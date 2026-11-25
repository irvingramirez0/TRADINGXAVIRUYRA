import importlib.util
import os
import sqlite3
import sys

AUTOMATION = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION")
sys.path.insert(0, AUTOMATION)
RUTA = os.path.join(AUTOMATION, "paginas_sitio.py")
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
    CREATE TABLE frames(id INTEGER, video_id TEXT, timestamp_sec REAL, path TEXT, description TEXT);
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

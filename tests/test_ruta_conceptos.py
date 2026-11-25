import importlib.util
import os
import sys

AUTOMATION = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION")
sys.path.insert(0, AUTOMATION)
RUTA = os.path.join(AUTOMATION, "paginas_sitio.py")
spec = importlib.util.spec_from_file_location("paginas_sitio", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_niveles_por_dependencia():
    import sqlite3
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

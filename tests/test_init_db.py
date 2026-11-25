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

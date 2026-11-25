import importlib.util
import os
import sqlite3

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "regenerar_vault.py")
spec = importlib.util.spec_from_file_location("regenerar_vault", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_comprobador_muestra_operaciones_sin_cita(tmp_path, monkeypatch):
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
    monkeypatch.setattr(mod, "VAULT", str(tmp_path))
    sin = mod.comprobador_fuentes(con, {1: 'fvg'}, {1: 'regla'}, {1: 'op-1'}, {})
    assert sin == 0
    texto = (tmp_path / "comprobador.md").read_text(encoding="utf-8")
    assert 'etiqueta: "Operaciones con cita formal (P&L autodeclarado)", hecho: 0, total: 1' in texto
    assert "Todo tiene fuente" not in texto

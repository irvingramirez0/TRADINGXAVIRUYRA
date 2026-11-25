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
    CREATE TABLE frame_vetos(frame_id INTEGER, concept_id INTEGER, entity_type TEXT);
    INSERT INTO concepts VALUES(1,'FVG','fvg,fair value gap','CORE','vigente','EXPLICITO');
    INSERT INTO concepts VALUES(2,'Sesión de Londres','sesion de londres,london','CONTEXTUAL','vigente','EXPLICITO');
    INSERT INTO frames VALUES(734,'v',100,'x.jpg','NQ 5m. FVG de 5m marcado en el low','');
    -- El CONTEXTUAL tiene evidencia directa; el CORE solo se nombra en la
    -- descripción. Así se comprueba que la prioridad CORE gana al empate.
    INSERT INTO evidence VALUES(1,'concept',2,734,'v',100,'sesión','OBSERVADO');
    """)
    conceptos = [{
        "id": 1, "name": "FVG", "alts": ["fvg", "fair value gap"],
        "alts_propias": ["fvg", "fair value gap"], "category": "CORE",
    }, {
        "id": 2, "name": "Sesión de Londres", "alts": ["sesión de londres", "london"],
        "alts_propias": ["sesión de londres", "london"], "category": "CONTEXTUAL",
    }]
    assert mod.asignar_fotogramas(con, conceptos)[734] == {1}


def test_sin_pie_no_se_ve():
    # Una anotación que niega el concepto no debe dejar caption publicado.
    desc = "No se distingue el IFVG, muy alejado"
    assert mod.niega_concepto(
        desc, ["ifvg"], 3, [("ifvg", 3)]
    ) is True


def test_negacion_en_oracion_anterior_al_concepto():
    # Caso real del fotograma 681: el IFVG se nombra en una frase anterior y
    # después se dice que el gráfico está demasiado lejos para ver la leg.
    desc = ("Recuadro: 'No siempre me voy a esperar al higher time frame ifvg'. "
            "El gráfico está muy alejado; no se distingue la estructura de la leg.")
    assert mod.niega_concepto(desc, ["inverse fair value gap (ifvg)", "ifvg"], 43,
                              [("ifvg", 43)]) is True

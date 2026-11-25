import importlib.util
import os

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "regenerar_vault.py")
spec = importlib.util.spec_from_file_location("regenerar_vault", RUTA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_siete_contradicciones(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "VAULT", str(tmp_path))
    n = mod.generar_contradciones()
    assert n == 7
    txt = (tmp_path / "contradicciones.md").read_text(encoding="utf-8")
    assert "9:30–10:30" in txt and "9:30–11:00" in txt
    assert "Vigente" in txt and "Histórica" in txt


def test_portada_incluye_contradiciones(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "VAULT", str(tmp_path))
    (tmp_path / "bootcamp").mkdir(exist_ok=True)
    notas, slugs = {}, {}
    mod.generate_index(notas, slugs, 0, 0, 0, 0, {})
    html = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "./contradicciones" in html
    

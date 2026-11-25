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

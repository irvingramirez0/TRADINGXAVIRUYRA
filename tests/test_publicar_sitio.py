import importlib.util
import os
import sys
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
    # Aislar argparse: pytest pasa sus propios argumentos a sys.argv.
    monkeypatch.setattr(sys, "argv", ["publicar_sitio.py"])
    # Simula que regenerar_vault agota el timeout y que nadie hace commit/push.
    monkeypatch.setattr(ps, "correr", lambda *a, **kw: (_ for _ in ()).throw(ps.TimeoutExpirado("regenerar", 1800)))
    commits = []

    class GitVacio:
        returncode = 0
        stdout = ""
        stderr = ""

    def git_falso(*a, **kw):
        commits.append(a)
        return GitVacio()

    monkeypatch.setattr(ps, "git", git_falso)
    rc = ps.main()
    assert rc == 1
    assert not [c for c in commits if c[0] in ("commit", "push")]
    assert "FALLO por timeout" in capsys.readouterr().out

import os

RUTA = os.path.join(os.path.dirname(__file__), "..", "09_AUTOMATION", "verificar_sitio.mjs")
txt = open(RUTA, encoding="utf-8").read()


def test_qa_no_hardcodea_21():
    assert 'bootcamp: 21 días listados' not in txt
    assert ').length")===21' not in txt
    assert "xr-dia').length" in txt


def test_qa_detecta_segundo_cero():
    assert "t=0s" in txt
    assert "const nDias" in txt
    assert "nDias >= 29" in txt


def test_qa_comprueba_citas_core():
    assert " ningún botón abre el segundo 0" in txt
    assert "ruta por dependencia publicada" in txt
    assert "xr-boton-fuente" in txt

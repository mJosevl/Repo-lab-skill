from unittest.mock import MagicMock

from langchain_core.messages import AIMessage

from clasificador import construir_clasificador


def test_clasificador_normaliza():
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Soporte.\n")
    resultado = construir_clasificador(modelo_falso).invoke({"ticket": "x"})
    assert resultado == "soporte"

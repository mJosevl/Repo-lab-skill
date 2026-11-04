from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

from cadena_tres_pasos import construir_cadena


def test_cadena_conecta_los_tres_pasos():
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="concepto\nconflicto\ntono"),
        AIMessage(content="un cuento breve"),
        AIMessage(content="# Título\n\nun cuento breve"),
    ]
    cadena = construir_cadena(modelo_falso)
    resultado = cadena.invoke({"libro": "libro de prueba"})
    assert modelo_falso.call_count == 3
    assert "# Título" in resultado
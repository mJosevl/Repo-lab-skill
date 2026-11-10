"""Pruebas del enrutamiento (Bloque 19). Modelo falso: no usa la API.

FakeListChatModel responde en orden: la 1.ª respuesta es la clasificación
y la 2.ª es la de la cadena elegida.
"""
import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from enrutamiento import construir_enrutador


@pytest.mark.parametrize(
    "clasificacion, esperado",
    [
        ("factoria", "ruta factoria"),
        ("administracion", "ruta administracion"),
        ("soporte", "ruta soporte"),
        (" Soporte.\n", "ruta soporte"),      # normaliza mayúscula y punto
        ("no sé", "ruta otro"),               # categoría inesperada -> default
    ],
)
def test_enrutador_elige_la_ruta_correcta(clasificacion, esperado):
    modelo = FakeListChatModel(responses=[clasificacion, esperado])
    resultado = construir_enrutador(modelo).invoke({"ticket": "x"})
    assert resultado == esperado

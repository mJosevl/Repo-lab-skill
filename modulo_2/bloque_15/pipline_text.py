"""Pruebas del pipeline de texto (Bloque 15). No necesitan mocks:
el pipeline no usa la red."""
import pytest

from pipeline_texto import (
    limpiar_texto,
    procesar_texto,
    proporcion_coincidencia,
    tokenizar,
)


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto("¡¡¡...!!!")
    assert resultado == []


def test_limpiar_texto_conserva_tildes_y_enie():
    assert limpiar_texto("¿Año de CANCIÓN?") == "año de canción"


def test_limpiar_texto_colapsa_espacios():
    assert limpiar_texto("  hola    mundo  ") == "hola mundo"


def test_limpiar_texto_rechaza_lo_que_no_es_texto():
    with pytest.raises(TypeError):
        limpiar_texto(None)


def test_tokenizar_separa_por_espacios():
    assert tokenizar("el gato y el perro") == ["el", "gato", "y", "el", "perro"]


def test_proporcion_coincidencia_total():
    ref = procesar_texto("Es San Juan de Pasto")
    resp = procesar_texto("Es SAN Juan Pasto de Juan")
    assert proporcion_coincidencia(ref, resp) == 1.0


def test_proporcion_coincidencia_referencia_vacia():
    assert proporcion_coincidencia([], ["hola"]) == 0.0
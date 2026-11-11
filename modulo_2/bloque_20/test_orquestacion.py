"""Bloque 20 · verificación de extremo a extremo (checklist completo).

1. La clasificación normaliza.
2. Cada ruta, incluido el default, recibe lo que le corresponde.
3. Una ruta con with_fallbacks: el fallback SÍ se ejecuta.
4. Un fallo fuera de las rutas (en la clasificación) no deja al flujo sin respuesta.
"""
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from clasificador import construir_clasificador
from enrutamiento import (
    RESPUESTA_RUTA,
    construir_cadena_con_enrutamiento,
    construir_cadena_segura,
)
from manejo_errores import RESPUESTA_GENERICA, procesar_ticket_seguro


def fallar(_):
    raise ConnectionError("simulado")


# 1. Normalización
def test_clasificacion_normaliza_antes_de_comparar():
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Soporte.\n")
    assert construir_clasificador(modelo_falso).invoke({"ticket": "x"}) == "soporte"


# 2. Camino normal: cada ruta, incluido el default
@pytest.mark.parametrize("categoria, ruta", [
    ("factoria", "cadena_factoria"),
    ("administracion", "cadena_administracion"),
    ("soporte", "cadena_soporte"),
    ("desconocido", "cadena_otro"),          # default
])
def test_enrutamiento_va_a_la_ruta_correcta(categoria, ruta):
    clasificacion_falsa = MagicMock(return_value=categoria)
    cadena_falsa = MagicMock(return_value=f"respuesta de {ruta}")
    cadena = construir_cadena_con_enrutamiento(clasificacion_falsa, **{ruta: cadena_falsa})

    resultado = cadena.invoke({"ticket": "x"})

    assert cadena_falsa.called
    assert resultado == f"respuesta de {ruta}"


# 3. Fallback de una ruta
def test_ruta_soporte_usa_fallback_ante_fallo_del_modelo():
    cadena_soporte_segura = construir_cadena_segura(RunnableLambda(fallar))
    resultado = cadena_soporte_segura.invoke({"ticket": "se cayó el agente"})
    assert resultado == RESPUESTA_RUTA
    assert "equipo" in resultado.lower()


def test_flujo_completo_con_ruta_rota_igual_responde():
    clasificacion_falsa = MagicMock(return_value="soporte")
    cadena = construir_cadena_con_enrutamiento(
        clasificacion_falsa,
        cadena_soporte=construir_cadena_segura(RunnableLambda(fallar)),
    )
    assert cadena.invoke({"ticket": "x"}) == RESPUESTA_RUTA


# 4. Fallo antes de elegir ruta: solo lo atrapa el try/except general
def test_procesar_ticket_seguro_no_propaga_excepciones():
    clasificacion_falsa = MagicMock(side_effect=ConnectionError("simulado"))
    cadena = construir_cadena_con_enrutamiento(paso_clasificacion=clasificacion_falsa)

    resultado = procesar_ticket_seguro(cadena, "mensaje de prueba")

    assert resultado == RESPUESTA_GENERICA
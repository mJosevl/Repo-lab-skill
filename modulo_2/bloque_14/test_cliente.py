from unittest.mock import Mock, patch

import httpx
import pytest
from google.genai import errors

import cliente_gemini
from cliente_gemini import (
    con_reintento,
    consultar_modelo,
    enviar_peticion,
    registrar_costo,
)

MODELO = "gemini-3.5-flash-lite"


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente_gemini.costo_total_sesion = 0
    yield


def cliente_falso(efecto=None, devuelve=None):
    """Cliente de Gemini simulado: nunca llama a la API real."""
    cliente = Mock()
    if efecto is not None:
        cliente.models.generate_content.side_effect = efecto
    else:
        cliente.models.generate_content.return_value = devuelve
    return cliente


def respuesta_falsa(texto="respuesta simulada", entrada=10, salida=5):
    respuesta = Mock()
    respuesta.text = texto
    respuesta.usage_metadata.prompt_token_count = entrada
    respuesta.usage_metadata.candidates_token_count = salida
    respuesta.usage_metadata.thoughts_token_count = 0
    return respuesta


# --- enviar_peticion ---
def test_enviar_peticion_credencial_invalida():
    cliente = cliente_falso(efecto=errors.ClientError(401, {"error": {"message": "x"}}))
    with pytest.raises(ValueError):
        enviar_peticion(cliente, "test", MODELO)


def test_enviar_peticion_sin_permiso():
    cliente = cliente_falso(efecto=errors.ClientError(403, {"error": {"message": "x"}}))
    with pytest.raises(ValueError):
        enviar_peticion(cliente, "test", MODELO)


def test_enviar_peticion_limite_de_uso():
    cliente = cliente_falso(efecto=errors.ClientError(429, {"error": {"message": "x"}}))
    with pytest.raises(TimeoutError):
        enviar_peticion(cliente, "test", MODELO)


def test_enviar_peticion_error_del_servidor():
    cliente = cliente_falso(efecto=errors.ServerError(503, {"error": {"message": "x"}}))
    with pytest.raises(TimeoutError):
        enviar_peticion(cliente, "test", MODELO)


def test_enviar_peticion_sin_conexion():
    cliente = cliente_falso(efecto=httpx.ConnectError("sin red"))
    with pytest.raises(TimeoutError):
        enviar_peticion(cliente, "test", MODELO)


def test_enviar_peticion_exito():
    esperada = respuesta_falsa()
    cliente = cliente_falso(devuelve=esperada)
    assert enviar_peticion(cliente, "test", MODELO) is esperada


# --- con_reintento ---
def test_con_reintento_agota_intentos():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente_gemini.time.sleep") as espera:
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)
    assert espera.call_count == 2


def test_con_reintento_exito_tras_fallar():
    funcion = Mock(side_effect=[TimeoutError("1"), TimeoutError("2"), "ok"])
    with patch("cliente_gemini.time.sleep"):
        assert con_reintento(funcion, intentos=3) == "ok"
    assert funcion.call_count == 3


def test_con_reintento_no_reintenta_value_error():
    funcion = Mock(side_effect=ValueError("credencial"))
    with patch("cliente_gemini.time.sleep") as espera:
        with pytest.raises(ValueError):
            con_reintento(funcion, intentos=3)
    assert funcion.call_count == 1
    espera.assert_not_called()


def test_con_reintento_respeta_espera_maxima():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente_gemini.time.sleep") as espera:
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=6, espera_base=2, espera_maxima=5)
    # el jitter suma como máximo un 10%
    assert all(llamada.args[0] <= 5 * 1.1 for llamada in espera.call_args_list)


# --- registrar_costo ---
def test_registrar_costo_acumula():
    # gemini-3.5-flash-lite: 300 entrada / 2500 salida (nanodólares por token)
    costo = registrar_costo(respuesta_falsa(entrada=10, salida=5), MODELO)
    assert costo == 10 * 300 + 5 * 2500
    registrar_costo(respuesta_falsa(entrada=10, salida=5), MODELO)
    assert cliente_gemini.costo_total_sesion == 2 * costo


# --- consultar_modelo ---
def test_consultar_modelo_exito():
    cliente = cliente_falso(devuelve=respuesta_falsa("Santiago"))
    assert consultar_modelo("Capital de Chile?", modelo=MODELO, cliente=cliente) == "Santiago"
    assert cliente_gemini.costo_total_sesion > 0


def test_consultar_modelo_convierte_error():
    with patch("cliente_gemini.con_reintento", side_effect=TimeoutError("simulado")):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba", modelo=MODELO, cliente=Mock())


def test_consultar_modelo_propaga_credencial_invalida():
    cliente = cliente_falso(efecto=errors.ClientError(401, {"error": {"message": "x"}}))
    with patch("cliente_gemini.time.sleep"):
        with pytest.raises(ValueError):
            consultar_modelo("pregunta de prueba", modelo=MODELO, cliente=cliente)
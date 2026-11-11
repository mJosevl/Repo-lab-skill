"""Pruebas del manejo de errores. Modelos falsos: no usan la API."""
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.runnables import RunnableLambda

from manejo_errores import (
    RESPUESTA_GENERICA,
    RESPUESTA_TICKET_VACIO,
    construir_enrutador_seguro,
    procesar_ticket_seguro,
)


def fallar(_):
    raise ConnectionError("error de red simulado")


modelo_roto = RunnableLambda(fallar)


def test_si_falla_el_principal_usa_el_respaldo():
    respaldo = FakeListChatModel(responses=["soporte", "respuesta del respaldo"])
    enrutador = construir_enrutador_seguro(modelo_roto, respaldo)
    assert enrutador.invoke({"ticket": "x"}) == "respuesta del respaldo"


def test_si_fallan_los_dos_responde_el_mensaje_fijo():
    enrutador = construir_enrutador_seguro(modelo_roto, modelo_roto)
    assert enrutador.invoke({"ticket": "x"}) == RESPUESTA_GENERICA


def test_procesar_ticket_vacio_no_llama_al_modelo():
    enrutador = RunnableLambda(fallar)  # si se llamara, fallaría
    assert procesar_ticket_seguro(enrutador, "   ") == RESPUESTA_TICKET_VACIO


def test_procesar_ticket_atrapa_cualquier_error():
    enrutador = RunnableLambda(fallar)
    assert procesar_ticket_seguro(enrutador, "hola") == RESPUESTA_GENERICA


def test_procesar_ticket_normal_devuelve_la_respuesta():
    principal = FakeListChatModel(responses=["factoria", "pasos del job"])
    enrutador = construir_enrutador_seguro(principal, modelo_roto)
    assert procesar_ticket_seguro(enrutador, "buscar order id") == "pasos del job"

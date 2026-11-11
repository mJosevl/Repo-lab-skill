"""Pruebas del Bloque 22. Sin modelo real ni API."""
from langchain_core.runnables import RunnableLambda

import agente_memoria
from agente_memoria import con_memoria, normalizar_respuesta, obtener_historial
from herramientas import consultar_job, contar_jobs_por_estado


# --- Herramientas con args_schema ---
def test_consultar_job_sin_historial():
    r = consultar_job.invoke({"nombre_job": "carga_inventario"})
    assert "Ended Not OK" in r and "Historial" not in r


def test_consultar_job_con_historial():
    r = consultar_job.invoke({"nombre_job": "CARGA_INVENTARIO", "incluir_historial": True})
    assert "código de salida 1" in r


def test_el_esquema_expone_los_argumentos():
    assert set(consultar_job.args) == {"nombre_job", "incluir_historial"}


def test_contar_jobs_por_estado():
    assert "1 job(s)" in contar_jobs_por_estado.invoke({"estado": "Ended Not OK"})


# --- Memoria ---
def test_normalizar_respuesta_une_bloques_de_texto():
    r = normalizar_respuesta({"output": [{"type": "text", "text": "Hola "},
                                         {"type": "text", "text": "Natacha"}]})
    assert r["output"].content == "Hola Natacha"


def test_misma_sesion_mismo_historial():
    assert obtener_historial("a") is obtener_historial("a")
    assert obtener_historial("a") is not obtener_historial("b")


def test_la_memoria_crece_dentro_de_una_sesion():
    agente_memoria.historiales.clear()
    # Ejecutor falso: responde cuántos mensajes previos ve
    falso = RunnableLambda(lambda x: {"output": f"veo {len(x['chat_history'])}"})
    agente = con_memoria(falso)
    s1 = {"configurable": {"session_id": "s1"}}
    s2 = {"configurable": {"session_id": "s2"}}

    assert agente.invoke({"entrada": "hola"}, s1)["output"].content == "veo 0"
    assert agente.invoke({"entrada": "otra"}, s1)["output"].content == "veo 2"
    assert agente.invoke({"entrada": "hola"}, s2)["output"].content == "veo 0"

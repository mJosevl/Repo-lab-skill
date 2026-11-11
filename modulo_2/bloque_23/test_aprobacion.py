"""Pruebas del Bloque 23. Sin modelo real ni teclado: la respuesta
humana se simula reemplazando pedir_confirmacion."""
import json
from types import SimpleNamespace

from langchain_core.messages import AIMessage

import aprobacion
from agente import registrar_traza
from aprobacion import registro_aprobaciones, relanzar_job


def test_relanzar_aprobado(monkeypatch):
    monkeypatch.setattr(aprobacion, "pedir_confirmacion", lambda _: "s")
    r = relanzar_job.invoke({"nombre_job": "CARGA_INVENTARIO"})
    assert "Rerun" in r
    assert registro_aprobaciones[-1]["aprobado"] is True


def test_relanzar_rechazado_no_ejecuta(monkeypatch):
    monkeypatch.setattr(aprobacion, "pedir_confirmacion", lambda _: "n")
    r = relanzar_job.invoke({"nombre_job": "CARGA_INVENTARIO"})
    assert "NO aprobado" in r
    assert registro_aprobaciones[-1]["aprobado"] is False


def test_cualquier_respuesta_distinta_de_s_es_rechazo(monkeypatch):
    monkeypatch.setattr(aprobacion, "pedir_confirmacion", lambda _: "sí, dale")
    assert "NO aprobado" in relanzar_job.invoke({"nombre_job": "CARGA_INVENTARIO"})


def test_job_inexistente_ni_siquiera_pide_aprobacion(monkeypatch):
    def no_deberia_llamarse(_):
        raise AssertionError("pidió aprobación para un job que no existe")
    monkeypatch.setattr(aprobacion, "pedir_confirmacion", no_deberia_llamarse)
    assert relanzar_job.invoke({"nombre_job": "NO_EXISTE"}).startswith("No encontré")


def test_registrar_traza_escribe_una_linea_json(tmp_path):
    archivo = tmp_path / "trazas.jsonl"
    accion = SimpleNamespace(tool="consultar_job", tool_input={"nombre_job": "X"})
    resultado = {"intermediate_steps": [(accion, "Ended OK")],
                 "output": AIMessage(content="Todo bien")}
    registrar_traza("s1", "¿cómo está X?", resultado, archivo=str(archivo))
    linea = json.loads(archivo.read_text(encoding="utf-8").strip())
    assert linea["acciones"][0]["herramienta"] == "consultar_job"
    assert linea["respuesta_final"] == "Todo bien"

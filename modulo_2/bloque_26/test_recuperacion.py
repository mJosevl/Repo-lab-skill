"""Pruebas del Bloque 26: embeddings y modelo falsos, sin API."""
import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from indexacion import cargar_corpus, indexar_corpus
from recuperacion import construir_prompt, extraer_citas, formatear_contexto, responder

EMB = DeterministicFakeEmbedding(size=64)


@pytest.fixture
def store(tmp_path):
    return indexar_corpus(cargar_corpus(), EMB, directorio=str(tmp_path))


def test_formatear_contexto_numera_desde_1():
    docs = [Document(page_content="a", metadata={"fuente": "PROC-01.md"}),
            Document(page_content="b", metadata={"fuente": "PROC-03.md"})]
    contexto, citas = formatear_contexto(docs)
    assert contexto == "[1] a\n\n[2] b"
    assert citas == {1: "PROC-01.md", 2: "PROC-03.md"}


def test_citas_tiene_k_entradas_y_ninguna_desconocida(store):
    _, citas = construir_prompt("¿qué es el Order ID?", store, k=3)
    assert list(citas) == [1, 2, 3]
    assert all(f.startswith("PROC-") for f in citas.values())


def test_el_prompt_contiene_la_pregunta_exacta(store):
    pregunta = "¿Cómo reviso un agente Unavailable?"
    prompt, _ = construir_prompt(pregunta, store)
    assert f"Pregunta: {pregunta}" in prompt
    assert "dilo explícitamente en vez de inventar" in prompt


def test_contexto_sin_saltos_de_numeracion(store):
    prompt, citas = construir_prompt("Set to OK", store, k=4)
    for n in citas:
        assert f"[{n}] " in prompt


def test_extraer_citas_marca_las_inventadas():
    citas = {1: "PROC-01.md", 2: "PROC-02.md"}
    r = extraer_citas("Usa Set to OK [1] y revisa el log [1]. Ver también [99].", citas)
    assert r == {1: "PROC-01.md", 99: "CITA INVÁLIDA (no estaba en el contexto)"}


def test_responder_devuelve_respuesta_y_fuentes(store):
    modelo = FakeListChatModel(responses=["Se marca como Set to OK [1]."])
    r = responder("¿cómo marco un job?", store, modelo)
    assert r["respuesta"] == "Se marca como Set to OK [1]."
    assert r["fuentes_citadas"] == {1: r["citas"][1]}
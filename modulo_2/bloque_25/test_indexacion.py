"""Pruebas del Bloque 25 con embeddings falsos: sin API ni cuota."""
from unittest.mock import Mock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding

from indexacion import (
    abrir,
    agregar_documento,
    borrar_documento,
    cargar_corpus,
    con_reintentos,
    ids_de,
    indexar_corpus,
    partir,
    validar_chunks,
)

EMB = DeterministicFakeEmbedding(size=64)


@pytest.fixture
def store(tmp_path):
    return indexar_corpus(cargar_corpus(), EMB, directorio=str(tmp_path))


# --- Validación ---
def test_chunks_validos_no_tienen_problemas():
    docs = cargar_corpus()
    assert validar_chunks(partir(docs), docs) == []


def test_detecta_chunk_vacio_y_duplicado():
    docs = cargar_corpus()
    chunks = partir(docs)
    malos = chunks + [chunks[0], Document(page_content="  ", metadata={"fuente": "x"})]
    problemas = validar_chunks(malos, docs)
    assert "hay chunks vacíos" in problemas
    assert "hay chunks duplicados" in problemas


def test_ids_son_estables_y_unicos():
    chunks = partir(cargar_corpus())
    ids = ids_de(chunks)
    assert ids == ids_de(chunks)
    assert len(ids) == len(set(ids))
    assert ids[0].endswith("#0")


# --- Persistencia ---
def test_reindexar_no_duplica(store, tmp_path):
    antes = store._collection.count()
    indexar_corpus(cargar_corpus(), EMB, directorio=str(tmp_path))
    assert abrir(EMB, directorio=str(tmp_path))._collection.count() == antes


def test_agregar_y_borrar_un_procedimiento(store):
    antes = store._collection.count()
    nuevo = Document(page_content="# PROC-04\n\nUn job en Wait Condition espera otra condición.",
                     metadata={"fuente": "PROC-04.md"})
    agregados = agregar_documento(store, nuevo)
    assert store._collection.count() == antes + agregados
    assert borrar_documento(store, "PROC-04.md") == agregados
    assert store._collection.count() == antes


def test_borrar_algo_que_no_existe_no_falla(store):
    assert borrar_documento(store, "NO_EXISTE.md") == 0


# --- Reintentos ---
def test_reintenta_ante_429():
    operacion = Mock(side_effect=[Exception("429 RESOURCE_EXHAUSTED"), "ok"])
    with patch("indexacion.time.sleep") as espera:
        assert con_reintentos(operacion) == "ok"
    espera.assert_called_once()


def test_no_reintenta_otros_errores():
    operacion = Mock(side_effect=Exception("401 API key inválida"))
    with patch("indexacion.time.sleep") as espera:
        with pytest.raises(Exception):
            con_reintentos(operacion)
    espera.assert_not_called()

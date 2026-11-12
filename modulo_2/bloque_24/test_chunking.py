"""Pruebas del chunking: sin API."""
from chunking import cargar_corpus, dividir_fijo, dividir_recursivo, termina_a_mitad


def test_carga_los_tres_procedimientos_con_su_fuente():
    docs = cargar_corpus()
    assert len(docs) == 3
    assert all(d.metadata["fuente"].startswith("PROC-") for d in docs)


def test_ningun_chunk_supera_el_tamano():
    docs = cargar_corpus()
    assert all(len(c.page_content) <= 200 for c in dividir_fijo(docs, 200))
    assert all(len(c.page_content) <= 300 for c in dividir_recursivo(docs, 300))


def test_cada_chunk_conserva_su_fuente():
    chunks = dividir_recursivo(cargar_corpus())
    assert all("fuente" in c.metadata for c in chunks)


def test_recursivo_corta_menos_oraciones_que_fijo():
    docs = cargar_corpus()
    cortes_fijo = sum(termina_a_mitad(c) for c in dividir_fijo(docs))
    cortes_recursivo = sum(termina_a_mitad(c) for c in dividir_recursivo(docs))
    assert cortes_recursivo < cortes_fijo

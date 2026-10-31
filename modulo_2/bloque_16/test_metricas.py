"""Pruebas de las métricas (Bloque 16). Sin mocks: no usan la red."""
import pytest

from metricas import (
    calcular_metricas,
    calcular_precision_cobertura_f1,
    contar_coincidencias,
    peores_casos,
    resumir_metricas,
)


# --- Funcionamiento básico ---
def test_contar_coincidencias_no_suma_repeticiones_de_mas():
    assert contar_coincidencias(["robot", "obedece"],
                                ["robot", "robot", "robot", "obedece"]) == 2


def test_ejemplo_calculado_a_mano():
    m = calcular_metricas("El gato duerme en el sofá.",
                          "El gato duerme en el sillón todo el día.")
    assert m["precision"] == pytest.approx(5 / 9)
    assert m["cobertura"] == pytest.approx(5 / 6)
    assert m["f1"] == pytest.approx(2 / 3)


def test_respuesta_identica_da_uno():
    m = calcular_metricas("Las Tres Leyes de la Robótica",
                          "¡las tres LEYES de la robótica!")
    assert m == {"precision": 1.0, "cobertura": 1.0, "f1": 1.0}


def test_respuesta_vacia_devuelve_ceros():
    assert calcular_precision_cobertura_f1(["robot"], []) == {
        "precision": 0.0, "cobertura": 0.0, "f1": 0.0}


def test_habla_de_mas_baja_la_precision():
    m = calcular_metricas("Susan Calvin es robopsicóloga",
                          "Susan Calvin es robopsicóloga en US Robots y es muy seria")
    assert m["cobertura"] == 1.0
    assert m["precision"] < 0.5


def test_se_queda_corto_baja_la_cobertura():
    m = calcular_metricas("Hari Seldon creó la psicohistoria para salvar la galaxia",
                          "Hari Seldon creó la psicohistoria")
    assert m["precision"] == 1.0
    assert m["cobertura"] < 0.6


# --- Límites documentados: la métrica se equivoca ---
def test_limite_sinonimos_castiga_respuesta_correcta():
    m = calcular_metricas("El robot es obediente", "El autómata es dócil")
    assert m["f1"] == pytest.approx(0.5)


def test_limite_dato_equivocado_igual_puntua_alto():
    m = calcular_metricas("Yo, Robot se publicó en 1950", "Yo, Robot se publicó en 1977")
    assert m["f1"] > 0.8


def test_limite_negacion_faltante_casi_perfecto():
    m = calcular_metricas("Un robot no debe dañar a un humano",
                          "Un robot debe dañar a un humano")
    assert m["precision"] == 1.0
    assert m["f1"] > 0.9


# --- Resumen y peores casos ---
def test_resumir_metricas_promedia():
    r = [{"precision": 1, "cobertura": 0, "f1": 0.5},
         {"precision": 0, "cobertura": 1, "f1": 0.5}]
    assert resumir_metricas(r) == {
        "precision_promedio": 0.5, "cobertura_promedio": 0.5, "f1_promedio": 0.5}


def test_resumir_metricas_lista_vacia():
    assert resumir_metricas([])["f1_promedio"] == 0.0


def test_peores_casos_ordena_de_menor_a_mayor():
    r = [{"consulta": "a", "f1": 0.9}, {"consulta": "b", "f1": 0.2},
         {"consulta": "c", "f1": 0.5}]
    assert [c["consulta"] for c in peores_casos(r, 2)] == ["b", "c"]
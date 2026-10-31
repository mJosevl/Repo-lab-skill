"""Métricas de evaluación de texto (Bloque 16), con ejemplos de Asimov.

Usa el pipeline del Bloque 15 (procesar_texto) y agrega una métrica real:
precisión, cobertura y F1, contando palabras SIN perder las repeticiones.

    precision  ->  de lo que dijo el modelo, ¿cuánto es correcto?
    cobertura  ->  de lo que debía decir, ¿cuánto dijo?
    f1         ->  las dos juntas en un solo número
"""
from collections import Counter

from pipeline_texto import procesar_texto


# ---------------------------------------------------------------
# 1. contar_coincidencias: el robot que repite no suma de más
# ---------------------------------------------------------------
def contar_coincidencias(tokens_referencia: list[str], tokens_respuesta: list[str]) -> int:
    """Cuenta cuántas palabras coinciden, respetando las repeticiones.

    Ejemplo:
        ref  = ["robot", "obedece"]
        resp = ["robot", "robot", "robot", "obedece"]
        contar_coincidencias(ref, resp) -> 2
        (la referencia tiene 1 "robot": los otros 2 no suman)
    """
    # Counter: cuántas veces aparece cada palabra
    # resp -> Counter({"robot": 3, "obedece": 1})
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)

    # & entre Counter: toma el MÍNIMO de cada palabra en común
    # robot: mín(1, 3) = 1  |  obedece: mín(1, 1) = 1
    interseccion = conteo_referencia & conteo_respuesta

    return sum(interseccion.values())  # 1 + 1 = 2


# ---------------------------------------------------------------
# 2. calcular_precision_cobertura_f1: Speedy entre dos órdenes
# ---------------------------------------------------------------
def calcular_precision_cobertura_f1(
    tokens_referencia: list[str], tokens_respuesta: list[str]
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens.

    Ejemplo (respuesta que habla de más):
        ref  = procesar_texto("Susan Calvin es robopsicóloga")
        resp = procesar_texto("Susan Calvin es robopsicóloga en US Robots y es muy seria")
        -> precision 0.36 | cobertura 1.0 | f1 0.53
        Dijo todo lo esperado (cobertura 1), pero lo mezcló con relleno.
    """
    # Lista vacía: no se puede dividir por cero
    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)

    # precision: coincidencias sobre lo que DIJO el modelo
    precision = coincidencias / len(tokens_respuesta)

    # cobertura: coincidencias sobre lo que DEBÍA decir
    cobertura = coincidencias / len(tokens_referencia)

    # f1: equilibrio entre las dos (si una es 0, f1 también)
    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {"precision": precision, "cobertura": cobertura, "f1": f1}


# ---------------------------------------------------------------
# 3. calcular_metricas: de dos textos a un resultado
# ---------------------------------------------------------------
def calcular_metricas(texto_referencia: str, texto_respuesta: str) -> dict[str, float]:
    """Procesa los DOS textos con el pipeline y los compara.

    Ejemplo (la Primera Ley sin su "no"):
        calcular_metricas("Un robot no debe dañar a un humano",
                          "Un robot debe dañar a un humano")
        -> precision 1.0 | cobertura 0.88 | f1 0.93
        Casi perfecto... para la frase que ordena dañar.
    """
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)
    return calcular_precision_cobertura_f1(tokens_referencia, tokens_respuesta)


# ---------------------------------------------------------------
# 4. resumir_metricas: la psicohistoria de Hari Seldon
# ---------------------------------------------------------------
def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    """Promedia precisión, cobertura y F1 de muchos resultados.

    Como la psicohistoria: predice a la masa, no al individuo.
    Un promedio alto puede esconder un caso desastroso.
    """
    if not resultados:
        return {"precision_promedio": 0.0, "cobertura_promedio": 0.0, "f1_promedio": 0.0}

    n = len(resultados)
    return {
        "precision_promedio": sum(r["precision"] for r in resultados) / n,
        "cobertura_promedio": sum(r["cobertura"] for r in resultados) / n,
        "f1_promedio": sum(r["f1"] for r in resultados) / n,
    }


# ---------------------------------------------------------------
# 5. peores_casos: lo que Susan Calvin revisaría primero
# ---------------------------------------------------------------
def peores_casos(resultados: list[dict], cantidad: int = 3) -> list[dict]:
    """Ordena de menor a mayor F1 y devuelve los primeros.
    Son los que vale la pena leer con criterio propio (Bloque 17)."""
    return sorted(resultados, key=lambda r: r["f1"])[:cantidad]


# ---------------------------------------------------------------
# Demostración:  python metricas.py   (no usa la API)
# ---------------------------------------------------------------
CASOS_ASIMOV = [
    ("Sinónimos: castiga lo correcto",
     "El robot es obediente", "El autómata es dócil"),
    ("Habla de más: precisión baja",
     "Susan Calvin es robopsicóloga",
     "Susan Calvin es robopsicóloga en US Robots y es muy seria"),
    ("Se queda corto: cobertura baja",
     "Hari Seldon creó la psicohistoria para salvar la galaxia",
     "Hari Seldon creó la psicohistoria"),
    ("Dato equivocado: premia lo incorrecto",
     "Yo, Robot se publicó en 1950", "Yo, Robot se publicó en 1977"),
    ("Negación: casi perfecto para lo prohibido",
     "Un robot no debe dañar a un humano", "Un robot debe dañar a un humano"),
]

if __name__ == "__main__":
    print(f"{'Caso':<44} {'Prec':>5} {'Cob':>5} {'F1':>5}")
    for titulo, referencia, respuesta in CASOS_ASIMOV:
        m = calcular_metricas(referencia, respuesta)
        print(f"{titulo:<44} {m['precision']:>5.2f} {m['cobertura']:>5.2f} {m['f1']:>5.2f}")
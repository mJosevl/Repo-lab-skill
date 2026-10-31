"""Compara respuestas reales del modelo contra referencias propias,
antes y después del pipeline (Bloque 15).

OJO: llama a la API de verdad (3 consultas). Necesita cliente_gemini.py
en esta misma carpeta y el .env con GEMINI_API_KEY.
"""
from cliente_gemini import consultar_modelo
from pipeline_texto import procesar_texto, proporcion_coincidencia

CASOS = [
    {
        "consulta": "¿Qué es Python? Responde en una sola oración.",
        "referencia": "Python es un lenguaje de programación interpretado.",
    },
    {
        "consulta": "¿Cuál es la capital de Chile? Responde en una sola oración.",
        "referencia": "La capital de Chile es Santiago.",
    },
    {
        "consulta": "¿Qué es Git? Responde en una sola oración.",
        "referencia": "Git es un sistema de control de versiones distribuido.",
    },
]


def comparar(numero, consulta, referencia):
    respuesta = consultar_modelo(consulta)

    # Antes: texto crudo, solo separado por espacios
    pct_crudo = proporcion_coincidencia(referencia.split(), respuesta.split())
    # Después: los dos lados pasan por el pipeline
    pct_proc = proporcion_coincidencia(
        procesar_texto(referencia), procesar_texto(respuesta)
    )

    print(f"\n[Caso {numero}] {consulta}")
    print(f"  Referencia: {referencia}")
    print(f"  Respuesta:  {respuesta.strip()}")
    print(f"  Coincidencia texto crudo:     {pct_crudo:.1%}")
    print(f"  Coincidencia texto procesado: {pct_proc:.1%}")


if __name__ == "__main__":
    for i, caso in enumerate(CASOS, start=1):
        comparar(i, caso["consulta"], caso["referencia"])
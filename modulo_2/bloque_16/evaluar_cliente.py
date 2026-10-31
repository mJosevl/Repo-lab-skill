"""Aplica las métricas a respuestas REALES del cliente (Bloque 16).

OJO: llama a la API de verdad (5 consultas). Necesita en esta carpeta:
    cliente_gemini.py, pipeline_texto.py, metricas.py
y el .env con GEMINI_API_KEY (puede estar en la raíz del repo).
Guarda todo en resultados_metricas.json.
"""
import json
from datetime import date

from cliente_gemini import consultar_modelo
from metricas import calcular_metricas, peores_casos, resumir_metricas

ARCHIVO = "resultados_metricas.json"

# Respuestas cortas: si el modelo responde un párrafo, la precisión se desploma.
INSTRUCCION = "Responde en una sola oración breve, en español, sin formato markdown."

# (consulta, referencia escrita por mí)
CASOS = [
    ("¿Quién escribió Yo, Robot?",
     "Isaac Asimov escribió Yo, Robot."),
    ("¿En qué año se publicó Yo, Robot?",
     "Yo, Robot se publicó en 1950."),
    ("¿Cuál es la Primera Ley de la Robótica de Asimov?",
     "Un robot no debe dañar a un ser humano ni permitir que sufra daño."),
    ("¿Qué es la psicohistoria en la saga Fundación?",
     "La psicohistoria es una ciencia que predice el comportamiento de grandes masas."),
    ("¿Cómo se llama la robopsicóloga de los cuentos de robots de Asimov?",
     "La robopsicóloga se llama Susan Calvin."),
]


def guardar(resultados: list[dict]) -> None:
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)


def main() -> None:
    resultados = []
    for consulta, referencia in CASOS:
        try:
            respuesta = consultar_modelo(consulta, system_instruction=INSTRUCCION)
        except (ValueError, RuntimeError) as error:
            print(f"Se omite '{consulta}': {error}")
            continue

        metricas = calcular_metricas(referencia, respuesta)
        resultados.append({
            "fecha": date.today().isoformat(),
            "consulta": consulta,
            "referencia": referencia,
            "respuesta": respuesta.strip(),
            **{k: round(v, 2) for k, v in metricas.items()},
        })
        guardar(resultados)  # en cada vuelta: si la API falla, no se pierde lo hecho

    if not resultados:
        print("No hubo respuestas para evaluar.")
        return

    print(f"\n{'Consulta':<62} {'Prec':>5} {'Cob':>5} {'F1':>5}")
    for r in resultados:
        print(f"{r['consulta'][:60]:<62} {r['precision']:>5.2f} "
              f"{r['cobertura']:>5.2f} {r['f1']:>5.2f}")

    resumen = resumir_metricas(resultados)
    print(f"\nPromedio -> precisión {resumen['precision_promedio']:.2f} | "
          f"cobertura {resumen['cobertura_promedio']:.2f} | "
          f"F1 {resumen['f1_promedio']:.2f}")

    print("\nPeores casos primero (para leer con criterio propio en el Bloque 17):")
    for r in peores_casos(resultados):
        print(f"  F1 {r['f1']:.2f} | {r['consulta']}")
        print(f"     referencia: {r['referencia']}")
        print(f"     respuesta:  {r['respuesta']}")

    print(f"\nGuardado en {ARCHIVO}")


if __name__ == "__main__":
    main()
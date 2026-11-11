"""Bloque 23 · nexo_desk: agente con memoria, aprobación humana y trazas.

- Herramientas de consulta (sin riesgo) + relanzar_job (requiere aprobación).
- Cada interacción queda en trazas_agente.jsonl: qué se preguntó, qué
  herramientas usó y con qué argumentos, y la respuesta final.
"""
import json
from datetime import datetime, timezone

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

from agente_memoria import con_memoria, prompt_agente
from aprobacion import relanzar_job
from herramientas import HERRAMIENTAS

HERRAMIENTAS_23 = HERRAMIENTAS + [relanzar_job]
ARCHIVO_TRAZAS = "trazas_agente.jsonl"


def construir_agente(modelo):
    agente = create_tool_calling_agent(modelo, HERRAMIENTAS_23, prompt_agente)
    ejecutor = AgentExecutor(
        agent=agente,
        tools=HERRAMIENTAS_23,
        return_intermediate_steps=True,
        max_iterations=5,  # límite de autonomía: no da vueltas sin fin
    )
    return con_memoria(ejecutor)


def registrar_traza(session_id: str, entrada: str, resultado: dict,
                    archivo: str = ARCHIVO_TRAZAS) -> dict:
    """Agrega una línea JSON por interacción."""
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {"herramienta": a.tool, "argumentos": a.tool_input, "observacion": o}
            for a, o in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado["output"].content,
    }
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro


if __name__ == "__main__":
    from modelo import crear_modelo

    agente = construir_agente(crear_modelo())
    session_id = "operador_turno_noche"
    config = {"configurable": {"session_id": session_id}}

    for entrada in [
        "¿Cómo está CARGA_INVENTARIO?",
        "Relánzalo, por favor",          # pedirá aprobación (s/n)
    ]:
        resultado = agente.invoke({"entrada": entrada}, config)
        print(resultado["output"].content)
        registrar_traza(session_id, entrada, resultado)

    print(f"\nTrazas guardadas en {ARCHIVO_TRAZAS}")

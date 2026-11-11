"""Bloque 21 · nexo_desk: primer agente con dos herramientas y traza."""
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from herramientas import HERRAMIENTAS

prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres nexo_desk, asistente de operadores de Control-M. Usa las "
        "herramientas para consultar jobs. Si una pregunta no se puede "
        "responder con ellas, dilo; no inventes estados ni Order IDs.",
    ),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])


def construir_agente(modelo, verbose: bool = True) -> AgentExecutor:
    agente = create_tool_calling_agent(modelo, HERRAMIENTAS, prompt_agente)
    return AgentExecutor(
        agent=agente,
        tools=HERRAMIENTAS,
        verbose=verbose,
        return_intermediate_steps=True,  # para ver la traza de decisión
    )


def mostrar_traza(resultado: dict) -> None:
    """Imprime qué herramientas usó el agente y qué obtuvo."""
    pasos = resultado.get("intermediate_steps", [])
    if not pasos:
        print("  (no usó herramientas)")
    for accion, observacion in pasos:
        print(f"  {accion.tool}({accion.tool_input}) -> {observacion}")


if __name__ == "__main__":
    from modelo import crear_modelo

    agente = construir_agente(crear_modelo(), verbose=False)
    for pregunta in [
        "¿Cómo está el job CARGA_INVENTARIO?",
        "Dame el Order ID de REPORTE_VENTAS",
        "¿Qué color combina con el rojo?",   # fuera de alcance: no debería usar herramientas
    ]:
        resultado = agente.invoke({"entrada": pregunta})
        print(f"\n{pregunta}\n{resultado['output']}")
        mostrar_traza(resultado)

"""Bloque 22 · nexo_desk: agente con herramientas propias y memoria por sesión.

Cada operador (session_id) tiene su propio historial: en el segundo mensaje
el agente recuerda lo que se habló en el primero.
"""
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

from herramientas import HERRAMIENTAS

prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres nexo_desk, asistente de operadores de Control-M. Usa las "
        "herramientas para consultar jobs y recuerda lo que el operador "
        "dijo antes. No inventes estados ni Order IDs.",
    ),
    MessagesPlaceholder("chat_history"),   # <- aquí entra la memoria
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

historiales: dict[str, InMemoryChatMessageHistory] = {}


def obtener_historial(session_id: str) -> InMemoryChatMessageHistory:
    """Un historial por sesión: mismo session_id = misma memoria."""
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]


def cerrar_sesion(session_id: str) -> None:
    """Borra el historial al terminar la conversación (no falla si no existe)."""
    historiales.pop(session_id, None)


def normalizar_respuesta(resultado: dict) -> dict:
    """Gemini a veces devuelve el texto como lista de bloques
    [{'type': 'text', 'text': ...}]. El historial necesita un mensaje simple:
    esto evita el error de formato que apareció en clase."""
    contenido = resultado["output"]
    if isinstance(contenido, list):
        contenido = "".join(
            bloque["text"]
            for bloque in contenido
            if isinstance(bloque, dict) and bloque.get("type") == "text"
        )
    return {**resultado, "output": AIMessage(content=contenido)}


def con_memoria(ejecutor):
    """Envuelve cualquier ejecutor con memoria por sesión."""
    return RunnableWithMessageHistory(
        ejecutor | RunnableLambda(normalizar_respuesta),
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )


def construir_agente_con_memoria(modelo):
    agente = create_tool_calling_agent(modelo, HERRAMIENTAS, prompt_agente)
    ejecutor = AgentExecutor(
        agent=agente, tools=HERRAMIENTAS, return_intermediate_steps=True
    )
    return con_memoria(ejecutor)


if __name__ == "__main__":
    from modelo import crear_modelo

    agente = construir_agente_con_memoria(crear_modelo())
    sesion = {"configurable": {"session_id": "operador_turno_noche"}}

    r1 = agente.invoke({"entrada": "¿Cómo está CARGA_INVENTARIO, con historial?"}, sesion)
    print(r1["output"].content)

    # Segunda pregunta: "ese job" solo se entiende gracias a la memoria
    print("Mensajes en el historial:", len(obtener_historial("operador_turno_noche").messages))

    r2 = agente.invoke({"entrada": "¿Y cuál era el Order ID de ese job?"}, sesion)
    print(r2["output"].content)
    print("Mensajes en el historial:", len(obtener_historial("operador_turno_noche").messages))

    # Otra sesión: no recuerda nada
    otra = {"configurable": {"session_id": "operador_turno_dia"}}
    r3 = agente.invoke({"entrada": "¿Cuál era el Order ID de ese job?"}, otra)
    print(r3["output"].content)
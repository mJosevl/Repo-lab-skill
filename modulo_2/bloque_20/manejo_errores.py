"""Bloque 20 · nexo_desk: que un paso que falla no tumbe todo el flujo.

Tres capas de protección:
  1. with_fallbacks: si el modelo principal falla, prueba el de respaldo.
  2. Si los dos fallan, responde un mensaje fijo (sin modelo).
  3. procesar_ticket_seguro: try/except final + log, nunca se cae.
"""
import logging

from langchain_core.runnables import RunnableLambda

from enrutamiento import construir_enrutador

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexo_desk")

RESPUESTA_GENERICA = (
    "No pude procesar el ticket automáticamente. Regístralo y "
    "escálalo al analista de turno."
)
RESPUESTA_TICKET_VACIO = "El ticket está vacío. Describe qué necesitas."


def construir_enrutador_seguro(modelo, modelo_respaldo):
    """Enrutador con dos modelos y una respuesta fija de último recurso."""
    respuesta_fija = RunnableLambda(lambda _: RESPUESTA_GENERICA)
    return construir_enrutador(modelo).with_fallbacks(
        [construir_enrutador(modelo_respaldo), respuesta_fija]
    )


def procesar_ticket_seguro(enrutador, ticket: str) -> str:
    """Procesa un ticket sin lanzar nunca una excepción al operador."""
    if not isinstance(ticket, str) or not ticket.strip():
        return RESPUESTA_TICKET_VACIO
    try:
        # OJO: la clave debe ser "ticket", igual que en las plantillas.
        return enrutador.invoke({"ticket": ticket.strip()})
    except Exception as error:
        logger.error("Error procesando ticket: %s", error)
        return RESPUESTA_GENERICA


if __name__ == "__main__":
    from modelo import crear_modelo

    enrutador = construir_enrutador_seguro(
        crear_modelo("gemini-3.6-flash", timeout=10),      # principal
        crear_modelo("gemini-3.5-flash-lite", timeout=15),  # respaldo
    )
    print(procesar_ticket_seguro(enrutador, "Necesito cambiar el host de un job"))
    print(procesar_ticket_seguro(enrutador, "   "))

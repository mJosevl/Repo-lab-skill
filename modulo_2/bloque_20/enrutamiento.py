"""Bloque 19: enrutamiento condicional.

Flujo: ticket -> clasificador -> RunnableBranch -> cadena de su categoría.
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough

from clasificador import construir_clasificador


def construir_cadena(modelo, instruccion):
    """Una cadena por categoría: plantilla | modelo | parser."""
    plantilla = PromptTemplate.from_template(
        instruccion + " No inventes nombres de jobs ni comandos.\n\nTicket: {ticket}"
    )
    return plantilla | modelo | StrOutputParser()


def construir_enrutador(modelo):
    clasificador = construir_clasificador(modelo)

    cadena_factoria = construir_cadena(
        modelo,
        "Eres analista de factoría Control-M. Indica los pasos para "
        "trabajar el job o XML que pide el ticket.",
    )
    cadena_administracion = construir_cadena(
        modelo,
        "Eres administrador de Control-M. Indica qué revisar en el "
        "ambiente o host que menciona el ticket.",
    )
    cadena_soporte = construir_cadena(
        modelo,
        "Eres soporte de turno de Control-M. Indica los primeros pasos "
        "para atender este incidente y a quién escalar.",
    )
    cadena_otro = construir_cadena(
        modelo,
        "El ticket no es claro. Pide al operador los datos que faltan, "
        "sin inventar pasos.",
    )

    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "factoria", cadena_factoria),
        (lambda x: x["categoria"] == "administracion", cadena_administracion),
        (lambda x: x["categoria"] == "soporte", cadena_soporte),
        cadena_otro,  # default: cualquier categoría inesperada
    )

    # 1) agrega "categoria" al diccionario  2) elige la ruta
    return RunnablePassthrough.assign(categoria=clasificador) | bifurcacion


if __name__ == "__main__":
    from modelo import crear_modelo

    enrutador = construir_enrutador(crear_modelo())
    for ticket in [
        "¿Cómo busco el Order ID de un job?",
        "Necesito cambiar el host de un job",
        "Se cayó el microservicio, me llamaron en turno",
        "No funciona",
    ]:
        print(f"\nTicket: {ticket}")
        print(enrutador.invoke({"ticket": ticket}))

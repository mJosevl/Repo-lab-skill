"""Bloque 19: enrutamiento condicional.

Flujo: ticket -> clasificador -> RunnableBranch -> cadena de su categoría.
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)

from clasificador import construir_clasificador


RESPUESTA_RUTA = (
    "Tu ticket quedó registrado. El equipo de turno lo revisará "
    "y te contactará con los pasos a seguir."
)


def construir_cadena_segura(cadena):
    """Bloque 20: si la ruta falla, responde algo razonable en vez de caerse."""
    return cadena.with_fallbacks([RunnableLambda(lambda _: RESPUESTA_RUTA)])


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

    return construir_cadena_con_enrutamiento(
        clasificador,
        construir_cadena_segura(cadena_factoria),
        construir_cadena_segura(cadena_administracion),
        construir_cadena_segura(cadena_soporte),
        construir_cadena_segura(cadena_otro),
    )


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_factoria=None,
    cadena_administracion=None,
    cadena_soporte=None,
    cadena_otro=None,
):
    """Arma clasificación + bifurcación. Recibe cada pieza por parámetro
    para poder reemplazarla por una falsa en las pruebas."""
    vacia = RunnablePassthrough()
    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "factoria", cadena_factoria or vacia),
        (lambda x: x["categoria"] == "administracion", cadena_administracion or vacia),
        (lambda x: x["categoria"] == "soporte", cadena_soporte or vacia),
        cadena_otro or vacia,  # default: cualquier categoría inesperada
    )
    # 1) agrega "categoria" al diccionario  2) elige la ruta
    return RunnablePassthrough.assign(categoria=paso_clasificacion) | bifurcacion


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

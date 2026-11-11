from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def construir_clasificador(modelo):
    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente ticket de Control-M en una sola "
        "palabra: factoria, administracion o soporte. "
        "Reglas: factoria es trabajo con jobs o XML (modificar, "
        "crear, buscar un Order ID). administracion es cambiar "
        "hosts, revisar ambientes, monitorear o tickets "
        "recurrentes. soporte es un incidente atendido en turno. "
        "Responde solo con esa palabra.\n\n{ticket}"
    )
    return (
        plantilla
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip(" .\n").lower())
    )


if __name__ == "__main__":
    from modelo import crear_modelo

    clasificador = construir_clasificador(crear_modelo())
    for ticket in [
        "¿Cómo busco el Order ID de un job?",
        "Necesito cambiar el host de un job",
        "Se cayó el microservicio, me llamaron en turno",
    ]:
        print(ticket, "->", clasificador.invoke({"ticket": ticket}))

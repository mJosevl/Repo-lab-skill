from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def construir_cadena(modelo):
    # Paso 1: extraer el concepto central, el conflicto y el tono de un libro
    plantilla_concepto = PromptTemplate.from_template(
        "Del siguiente libro de ciencia ficción, devuelve su concepto "
        "central, su conflicto y su tono, uno por línea, sin "
        "desarrollarlos:\n\n{libro}"
    )
    paso_concepto = plantilla_concepto | modelo | StrOutputParser()

    # Paso 2: escribir un cuento nuevo a partir de ese concepto
    plantilla_cuento = PromptTemplate.from_template(
        "Usando este concepto, conflicto y tono, escribe un cuento "
        "breve y original de ciencia ficción, de unas 150 palabras, "
        "en español:\n\n{concepto}"
    )
    paso_cuento = plantilla_cuento | modelo | StrOutputParser()

    # Paso 3: ponerle título y dar formato markdown
    plantilla_formato = PromptTemplate.from_template(
        "Pon un título al siguiente cuento y entrégalo en markdown: "
        "el título como encabezado y el cuento debajo.\n\n{cuento}"
    )
    paso_formato = plantilla_formato | modelo | StrOutputParser()

    return (
        paso_concepto
        | (lambda concepto: {"concepto": concepto})
        | paso_cuento
        | (lambda cuento: {"cuento": cuento})
        | paso_formato
    )


if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    cadena = construir_cadena(modelo)

    resultado = cadena.invoke({"libro": "Los propios dioses, de Isaac Asimov"})
    print(resultado)
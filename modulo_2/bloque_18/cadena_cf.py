from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from cprint import cprint

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Paso 1: extraer el germen del libro
plantilla_concepto = PromptTemplate.from_template(
    "Del siguiente libro de ciencia ficción, devuelve su concepto "
    "central, su conflicto y su tono, uno por línea, sin "
    "desarrollarlos:\n\n{libro}"
)
paso_concepto = plantilla_concepto | modelo | StrOutputParser()

# Paso 2: escribir un cuento nuevo con ese germen
plantilla_cuento = PromptTemplate.from_template(
    "Usando este concepto, conflicto y tono, escribe un cuento "
    "breve y original de ciencia ficción, de unas 150 palabras, "
    "en español:\n\n{concepto}"
)
paso_cuento = plantilla_cuento | modelo | StrOutputParser()

# Paso 3: dar formato
plantilla_formato = PromptTemplate.from_template(
    "Pon un título al siguiente cuento y entrégalo en markdown: "
    "el título como encabezado y el cuento debajo. Al final agrega "
    "una línea 'Inspirado en: {libro}'.\n\nCuento:\n{cuento}"
)
paso_formato = plantilla_formato | modelo | StrOutputParser()

# Cadena completa
cadena_cf = (
    {"concepto": paso_concepto, "libro": lambda x: x["libro"]}
    | {"cuento": paso_cuento, "libro": lambda x: x["libro"]}
    | paso_formato
)

if __name__ == "__main__":
    libro = "Los propios dioses, de Isaac Asimov"
    cprint.info(cadena_cf.invoke({"libro": libro}))
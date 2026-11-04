from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from cprint import cprint

# Definición de la plantilla
# Plantilla para comparar probabilidades de victoria entre dos tenistas en una superficie específica
plantilla = PromptTemplate.from_template(
    "Probabilidades de que {tenista_1} le gane a {tenista_2}"
    " en una superficie de {superficie}"
    " dame respuesta corta solo quién gana y un porcentaje de probabilidad"
)

# Invocación de la plantilla con datos específicos
prompt = plantilla.invoke(
    {
        "tenista_1": "Rafael Nadal",
        "tenista_2": "Roger Federer",
        "superficie": "arcilla"
    }
)

cprint.ok(prompt.text)


modelo = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature = 0, # Que tan aleatorio es el resultado 0 poco, 2 muy aleatorio, default 0.7.
)
# Generación de la respuesta del modelo
respuesta = modelo.invoke(prompt)
cprint.info(respuesta.content)

cadena_simple = plantilla | modelo

respuesta = cadena_simple.invoke(
    {
        "tenista_1": "Rafael Nadal",
        "tenista_2": "Roger Federer",
        "superficie": "arcilla"
    }
)
cprint.info(respuesta.content)
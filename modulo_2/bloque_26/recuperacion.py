"""Bloque 26 · nexo_desk: recuperación semántica + prompt dinámico con citas.

pregunta -> k chunks más parecidos -> contexto numerado [1], [2]...
         -> prompt que obliga a citar -> respuesta -> fuentes verificables
"""
import re

from langchain_core.output_parsers import StrOutputParser

from indexacion import abrir, cargar_corpus, indexar_corpus

PROMPT_TEMPLATE = """Eres nexo_desk, asistente de operadores de Control-M.
Responde la pregunta usando SOLO el contexto de abajo. Cita la fuente de cada \
afirmación con su número entre corchetes, como [1]. Si el contexto no alcanza \
para responder, dilo explícitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    """Contexto numerado para el prompt + mapa número -> fuente."""
    lineas, citas = [], {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        citas[i] = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(lineas), citas


def construir_prompt(pregunta: str, vector_store, k: int = 3):
    """Recupera k chunks (sin reindexar) y arma el prompt con citas."""
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    chunks = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks)
    return PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta), citas


def extraer_citas(respuesta: str, citas: dict) -> dict:
    """{número citado: fuente}. Si el modelo inventa un número, lo marca."""
    numeros = sorted({int(n) for n in re.findall(r"\[(\d+)\]", respuesta)})
    return {n: citas.get(n, "CITA INVÁLIDA (no estaba en el contexto)") for n in numeros}


def responder(pregunta: str, vector_store, modelo, k: int = 3) -> dict:
    prompt, citas = construir_prompt(pregunta, vector_store, k)
    texto = (modelo | StrOutputParser()).invoke(prompt)
    return {"respuesta": texto, "citas": citas, "fuentes_citadas": extraer_citas(texto, citas)}


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

    load_dotenv()
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise SystemExit('Falta GEMINI_API_KEY en tu ".env".')
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=clave)
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", google_api_key=clave)

    store = abrir(embeddings)
    if store._collection.count() == 0:          # solo la primera vez
        store = indexar_corpus(cargar_corpus(), embeddings)
    print("Chunks en el índice:", store._collection.count())

    preguntas = [
        "¿Cómo marco un job como terminado sin matar el proceso?",   # PROC-01
        "Un agente aparece desconectado, ¿qué reviso?",              # PROC-02
        "¿Cuál es la contraseña del servidor de producción?",       # fuera del corpus
    ]
    for pregunta in preguntas:
        r = responder(pregunta, store, modelo)
        print("\n" + "=" * 70)
        print("Pregunta:", pregunta)
        print("Recuperados:", r["citas"])
        print("Respuesta:", r["respuesta"])
        print("Fuentes citadas:", r["fuentes_citadas"] or "ninguna")
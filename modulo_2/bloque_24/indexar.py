"""Bloque 24 · nexo_desk: indexar el corpus y persistir los embeddings en Chroma.

corpus (.md) -> chunks -> embeddings de Gemini -> Chroma en ./chroma_db
"""
from langchain_chroma import Chroma

from chunking import cargar_corpus, dividir_recursivo

DIRECTORIO_DB = "./chroma_db"
COLECCION = "procedimientos_controlm"


def crear_embeddings():
    import os

    from dotenv import load_dotenv
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit('Falta GEMINI_API_KEY en tu ".env".')
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )


def indexar(chunks, embeddings, directorio: str = DIRECTORIO_DB,
            coleccion: str = COLECCION) -> Chroma:
    """Guarda los chunks en Chroma. Reinicia la colección para no duplicar."""
    vector_store = Chroma(
        collection_name=coleccion,
        embedding_function=embeddings,
        persist_directory=directorio,
    )
    vector_store.reset_collection()  # volver a indexar no duplica los chunks
    vector_store.add_documents(chunks)
    return vector_store


def abrir(embeddings, directorio: str = DIRECTORIO_DB, coleccion: str = COLECCION) -> Chroma:
    """Abre la base ya guardada en disco, sin volver a indexar."""
    return Chroma(collection_name=coleccion, embedding_function=embeddings,
                  persist_directory=directorio)


if __name__ == "__main__":
    embeddings = crear_embeddings()
    chunks = dividir_recursivo(cargar_corpus())

    try:
        vector_store = indexar(chunks, embeddings)
    except Exception as error:
        mensaje = str(error)
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            raise SystemExit("Límite de peticiones. Espera un minuto y reintenta.")
        if "API key" in mensaje or "401" in mensaje or "403" in mensaje:
            raise SystemExit("La API rechazó la clave. Revisa GEMINI_API_KEY.")
        raise

    print(f"Chunks indexados: {vector_store._collection.count()}")

    # Comprobación: buscar por significado, no por palabra exacta
    pregunta = "¿cómo marco un job como terminado sin matar el proceso?"
    for doc in vector_store.similarity_search(pregunta, k=2):
        print(f"\n[{doc.metadata['fuente']}]\n{doc.page_content}")

"""Bloque 25 · nexo_desk: indexación persistente y mantenible del corpus.

- ids estables por chunk: volver a indexar REEMPLAZA, no duplica.
- agregar o borrar un procedimiento sin recalcular los demás.
- validación de chunks antes de gastar llamadas a la API.
- reintentos ante 429.
"""
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CARPETA = Path(__file__).parent
CARPETA_CORPUS = CARPETA / "corpus"
DIRECTORIO_DB = str(CARPETA / "vectorstore")   # ruta absoluta: no depende de dónde corras
COLECCION = "procedimientos_controlm"


# ---------- 1. Cargar y partir ----------
def cargar_corpus(carpeta: Path = CARPETA_CORPUS) -> list[Document]:
    return [
        Document(page_content=a.read_text(encoding="utf-8"), metadata={"fuente": a.name})
        for a in sorted(Path(carpeta).glob("*.md"))
    ]


def partir(documentos: list[Document], tamano: int = 300, solapamiento: int = 30) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=tamano, chunk_overlap=solapamiento)
    return splitter.split_documents(documentos)


def ids_de(chunks: list[Document]) -> list[str]:
    """Id estable = fuente + posición: 'PROC-01_estado_de_jobs.md#0', '#1'..."""
    contador: dict[str, int] = {}
    ids = []
    for chunk in chunks:
        fuente = chunk.metadata["fuente"]
        n = contador.get(fuente, 0)
        ids.append(f"{fuente}#{n}")
        contador[fuente] = n + 1
    return ids


# ---------- 2. Validar antes de gastar API ----------
def validar_chunks(chunks: list[Document], documentos: list[Document]) -> list[str]:
    """Devuelve la lista de problemas (vacía = todo bien).

    No compara la suma de caracteres: con solapamiento los chunks suman
    MÁS que el corpus, y esa comparación fallaría aunque todo esté bien.
    """
    problemas = []
    textos = [c.page_content for c in chunks]
    if any(not t.strip() for t in textos):
        problemas.append("hay chunks vacíos")
    if len(textos) != len(set(textos)):
        problemas.append("hay chunks duplicados")
    originales = {d.metadata["fuente"]: d.page_content for d in documentos}
    for c in chunks:
        if c.page_content not in originales.get(c.metadata.get("fuente"), ""):
            problemas.append(f"un chunk no aparece en su fuente {c.metadata.get('fuente')}")
            break
    fuentes_con_chunks = {c.metadata.get("fuente") for c in chunks}
    for fuente in originales:
        if fuente not in fuentes_con_chunks:
            problemas.append(f"el documento {fuente} quedó sin chunks")
    return problemas


# ---------- 3. Reintentos ante límite de uso ----------
def con_reintentos(operacion, max_intentos: int = 4, espera_inicial: float = 5):
    espera = espera_inicial
    for intento in range(1, max_intentos + 1):
        try:
            return operacion()
        except Exception as error:
            mensaje = str(error)
            es_limite = "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje
            if not es_limite or intento == max_intentos:
                raise
            print(f"Límite de peticiones. Reintento {intento} de {max_intentos - 1} en {espera} s...")
            time.sleep(espera)
            espera *= 2


# ---------- 4. Indexar, reconectar, agregar, borrar ----------
def abrir(embeddings, directorio: str = DIRECTORIO_DB, coleccion: str = COLECCION) -> Chroma:
    """Reconecta a la base en disco, sin recalcular nada."""
    return Chroma(collection_name=coleccion, embedding_function=embeddings,
                  persist_directory=directorio)


def indexar_corpus(documentos, embeddings, directorio: str = DIRECTORIO_DB,
                   coleccion: str = COLECCION) -> Chroma:
    chunks = partir(documentos)
    problemas = validar_chunks(chunks, documentos)
    if problemas:
        raise ValueError("Chunks inválidos: " + "; ".join(problemas))

    store = abrir(embeddings, directorio, coleccion)
    con_reintentos(lambda: store.add_documents(chunks, ids=ids_de(chunks)))
    return store


def borrar_documento(store: Chroma, fuente: str) -> int:
    """Borra todos los chunks de un procedimiento. Devuelve cuántos borró."""
    encontrados = store.get(where={"fuente": fuente})["ids"]
    if encontrados:
        store.delete(ids=encontrados)
    return len(encontrados)


def agregar_documento(store: Chroma, documento: Document) -> int:
    """Agrega (o actualiza) un procedimiento sin tocar los demás."""
    borrar_documento(store, documento.metadata["fuente"])  # por si cambió de largo
    chunks = partir([documento])
    con_reintentos(lambda: store.add_documents(chunks, ids=ids_de(chunks)))
    return len(chunks)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit('Falta GEMINI_API_KEY en tu ".env".')
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", google_api_key=os.getenv("GEMINI_API_KEY"))

    store = indexar_corpus(cargar_corpus(), embeddings)
    print("Ruta del índice:", DIRECTORIO_DB)
    print("Chunks tras indexar:", store._collection.count())

    store = indexar_corpus(cargar_corpus(), embeddings)
    print("Chunks tras indexar OTRA vez (no duplica):", store._collection.count())

    nuevo = Document(
        page_content=("# PROC-04 · Revisar un job en Wait Condition\n\n"
                      "Contenido de ejemplo. Un job en Wait Condition espera una "
                      "condición de otro job. Se revisa qué condición falta y qué "
                      "job debía generarla."),
        metadata={"fuente": "PROC-04_wait_condition.md"},
    )
    print("Chunks agregados de PROC-04:", agregar_documento(store, nuevo))
    print("Chunks totales:", abrir(embeddings)._collection.count())

    print("Chunks borrados de PROC-04:", borrar_documento(store, "PROC-04_wait_condition.md"))
    print("Chunks totales:", abrir(embeddings)._collection.count())

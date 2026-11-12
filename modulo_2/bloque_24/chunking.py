"""Bloque 24 · nexo_desk: cargar el corpus y dividirlo en chunks.

Compara dos estrategias:
  - fija: corta cada N caracteres, aunque parta una oración a la mitad.
  - recursiva: intenta cortar por párrafo, luego por línea, luego por
    espacio. Respeta mejor el sentido.
"""
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

CARPETA_CORPUS = Path(__file__).parent / "corpus"


def cargar_corpus(carpeta: Path = CARPETA_CORPUS) -> list[Document]:
    """Un Document por archivo .md, con el nombre del archivo como fuente."""
    documentos = []
    for archivo in sorted(Path(carpeta).glob("*.md")):
        documentos.append(Document(
            page_content=archivo.read_text(encoding="utf-8"),
            metadata={"fuente": archivo.name},
        ))
    return documentos


def dividir_fijo(documentos: list[Document], tamano: int = 200) -> list[Document]:
    splitter = CharacterTextSplitter(separator="", chunk_size=tamano, chunk_overlap=0)
    return splitter.split_documents(documentos)


def dividir_recursivo(documentos: list[Document], tamano: int = 300,
                      solapamiento: int = 30) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=tamano, chunk_overlap=solapamiento)
    return splitter.split_documents(documentos)


def termina_a_mitad(chunk: Document) -> bool:
    """True si el chunk corta una oración (no termina en punto ni salto)."""
    return not chunk.page_content.rstrip().endswith((".", ":", "\n"))


if __name__ == "__main__":
    documentos = cargar_corpus()
    print(f"Documentos cargados: {len(documentos)}")

    for nombre, chunks in [("FIJO", dividir_fijo(documentos)),
                           ("RECURSIVO", dividir_recursivo(documentos))]:
        cortados = sum(termina_a_mitad(c) for c in chunks)
        print(f"\n=== {nombre}: {len(chunks)} chunks, {cortados} cortan una oración ===")
        for c in chunks[:3]:
            print(f"[{c.metadata['fuente']}] {c.page_content!r}\n")

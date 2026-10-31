"""Pipeline de procesamiento de texto (Bloque 15).

Deja el texto en un formato comparable: minúsculas, sin puntuación
y separado en palabras (tokens).
"""
import re


def limpiar_texto(texto: str) -> str:
    """Normaliza el texto: minúsculas, sin puntuación y sin espacios repetidos."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)       # borra la puntuación
    texto = re.sub(r"\s+", " ", texto).strip()  # varios espacios -> uno
    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    """Convierte texto limpio en una lista de tokens (palabras)."""
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Une los dos pasos: limpia y tokeniza."""
    return tokenizar(limpiar_texto(texto))


def proporcion_coincidencia(tokens_ref: list[str], tokens_resp: list[str]) -> float:
    """Qué proporción de las palabras de la referencia aparece en la respuesta."""
    set_ref = set(tokens_ref)
    if not set_ref:  # referencia vacía: evita dividir por cero
        return 0.0
    comunes = set_ref & set(tokens_resp)
    return len(comunes) / len(set_ref)
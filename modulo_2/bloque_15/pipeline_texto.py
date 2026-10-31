"""Pipeline de procesamiento de texto (Bloque 15), con ejemplos de Asimov.

Objetivo: dejar dos textos en el mismo formato para compararlos de forma
justa, sin que una mayúscula o una coma cambien el resultado.

Los pasos:
    1. limpiar_texto           quita la forma (mayúsculas, signos, espacios)
    2. tokenizar               corta el texto en fichas (palabras)
    3. procesar_texto          hace 1 y 2 de una vez
    4. vectorizar              cuenta cuántas veces aparece cada ficha
    5. proporcion_coincidencia compara referencia y respuesta (0 a 1)
"""
import re
from collections import Counter


# ---------------------------------------------------------------
# 1. limpiar_texto: la Primera Ley, sin gritos
# ---------------------------------------------------------------
def limpiar_texto(texto: str) -> str:
    """Deja el texto en minúsculas, sin puntuación y con un solo espacio
    entre palabras.

    Ejemplo:
        limpiar_texto("¡Speedy,   trae el SELENIO!")
        -> "speedy trae el selenio"
    """
    # Si no llega texto, no hay orden que procesar:
    # limpiar_texto(None) -> TypeError: limpiar_texto espera un texto (str), no NoneType
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera un texto (str), no {tipo}")

    # .lower(): todo a minúsculas
    # "¡Speedy,   trae el SELENIO!" -> "¡speedy,   trae el selenio!"
    texto = texto.lower()

    # re.sub(r"[^\w\s]", "", ...): borra lo que no sea letra, número o espacio
    # "¡speedy,   trae el selenio!" -> "speedy   trae el selenio"
    texto = re.sub(r"[^\w\s]", "", texto)

    # re.sub(r"\s+", " ", ...).strip(): varios espacios -> uno solo
    # "speedy   trae el selenio" -> "speedy trae el selenio"
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


# ---------------------------------------------------------------
# 2. tokenizar: las fichas de Multivac
# ---------------------------------------------------------------
def tokenizar(texto_limpio: str) -> list[str]:
    """Corta el texto limpio en una lista de palabras (tokens).

    Ejemplo:
        tokenizar("speedy trae el selenio")
        -> ["speedy", "trae", "el", "selenio"]
    """
    # .split(): corta en cada espacio
    palabras = texto_limpio.split()
    return palabras


# ---------------------------------------------------------------
# 3. procesar_texto: limpiar + tokenizar en un solo paso
# ---------------------------------------------------------------
def procesar_texto(texto: str) -> list[str]:
    """Limpia el texto y lo corta en palabras.

    Ejemplo:
        procesar_texto("¡UN ROBOT no debe dañar a un HUMANO!")
        -> ["un", "robot", "no", "debe", "dañar", "a", "un", "humano"]
    """
    texto_limpio = limpiar_texto(texto)   # "un robot no debe dañar a un humano"
    palabras = tokenizar(texto_limpio)    # ["un", "robot", "no", ...]
    return palabras


# ---------------------------------------------------------------
# 4. vectorizar: la bolsa de fichas, contada
# ---------------------------------------------------------------
def vectorizar(tokens: list[str]) -> Counter:
    """Cuenta cuántas veces aparece cada palabra.

    Ejemplo:
        vectorizar(procesar_texto("Robot, robot, ROBOT: obedece al humano"))
        -> Counter({"robot": 3, "obedece": 1, "al": 1, "humano": 1})
    """
    return Counter(tokens)


# ---------------------------------------------------------------
# 5. proporcion_coincidencia: ¿cuánto de la referencia aparece?
# ---------------------------------------------------------------
def proporcion_coincidencia(tokens_ref: list[str], tokens_resp: list[str]) -> float:
    """Devuelve un número entre 0 y 1:
        0 = ninguna palabra de la referencia aparece en la respuesta
        1 = todas aparecen

    Ojo: usa set(), así que NO ve el orden ni las repeticiones.

    Ejemplo (la trampa de Robbie):
        ref  = procesar_texto("Robbie cuida a Gloria")
        resp = procesar_texto("Gloria cuida a Robbie")
        proporcion_coincidencia(ref, resp) -> 1.0   (¡pero la historia se invirtió!)
    """
    # set(): bolsa sin repetidos y sin orden
    # ["un", "robot", "no", "debe", "dañar", "a", "un", "humano"]
    #   -> {"un", "robot", "no", "debe", "dañar", "a", "humano"}   (7, un "un" se fue)
    palabras_ref = set(tokens_ref)
    palabras_resp = set(tokens_resp)

    # Referencia vacía: no se puede dividir por cero
    if len(palabras_ref) == 0:
        return 0.0

    # &: las palabras que están en los DOS lados
    # Primera Ley sin "no": comunes = 6 de 7 -> 6/7 = 0.86
    comunes = palabras_ref & palabras_resp

    return len(comunes) / len(palabras_ref)


# ---------------------------------------------------------------
# Demostración:  python pipeline_texto.py
# ---------------------------------------------------------------
CASOS_ASIMOV = [
    ("Limpieza: la Primera Ley a gritos",
     "Un robot no debe dañar a un humano",
     "¡UN ROBOT no debe dañar a un HUMANO!"),
    ("Orden: ¿quién cuida a quién?",
     "Robbie cuida a Gloria",
     "Gloria cuida a Robbie"),
    ("Negación: la Primera Ley sin su 'no'",
     "Un robot no debe dañar a un humano",
     "Un robot debe dañar a un humano"),
    ("Dato: Speedy y el mineral equivocado",
     "Speedy debe traer selenio de Mercurio",
     "Speedy debe traer hierro de Mercurio"),
    ("Cifra: el plan de Hari Seldon",
     "Hari Seldon predijo la caída del Imperio en 1.000 años",
     "Hari Seldon predijo la caída del Imperio en 30.000 años"),
]

if __name__ == "__main__":
    for titulo, referencia, respuesta in CASOS_ASIMOV:
        crudo = proporcion_coincidencia(referencia.split(), respuesta.split())
        limpio = proporcion_coincidencia(
            procesar_texto(referencia), procesar_texto(respuesta)
        )
        print(f"\n{titulo}")
        print(f"  Referencia: {referencia}")
        print(f"  Respuesta:  {respuesta}")
        print(f"  Sin limpiar: {crudo:.2f}  |  Limpiando: {limpio:.2f}")
import json
import os
import random
import re
import statistics
import time

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from typing import Any, Callable

# Carga las variables definidas en el archivo .env
load_dotenv()

MODELO_POR_DEFECTO = "gemini-3.5-flash-lite"

# Precios oficiales, nivel de pago, Standard.
# Unidad: nanodólares por token (USD por millón de tokens × 1.000).
# Fuente: https://ai.google.dev/gemini-api/docs/pricing (consultado el 2026-10-20).
# El precio de salida incluye los tokens de razonamiento.
# gemini-3.8-flash y gemini-3.6-flash: precio vigente hasta el 2026-12-31;
# desde el 2027-01-01 suben a (1500, 7500).
PRECIOS = {
    "gemini-3.8-flash": (750, 3750),
    "gemini-3.6-flash": (750, 3750),
    "gemini-3.5-flash-lite": (300, 2500),
    "gemini-3.1-flash-lite": (250, 1500),
}
MODELOS_A_COMPARAR = list(PRECIOS)
CICLOS_POR_MODELO = 5
NANODOLARES_POR_DOLAR = 1_000_000_000


def crear_cliente():
    """Crea el cliente de Gemini validando que exista la credencial."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta GEMINI_API_KEY. Revisa que tu archivo .env esté en la raíz "
            "del proyecto y que la variable se llame exactamente así."
        )
    return genai.Client(api_key=api_key)


def validar_pregunta(pregunta):
    """Detiene la ejecución si la pregunta no es texto o viene vacía."""
    if not isinstance(pregunta, str):
        raise ValueError("La pregunta debe ser una cadena de texto")
    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")
    return pregunta.strip()


def armar_peticion(system_instruction=None, response_schema=None):
    """Arma la configuración de la petición con lo que se haya pasado."""
    # Armamos las opciones solo con lo que nos pasaron
    opciones = {}
    if system_instruction:
        opciones["system_instruction"] = system_instruction
    if response_schema:
        opciones["response_mime_type"] = "application/json"
        opciones["response_schema"] = response_schema
    return types.GenerateContentConfig(**opciones)


def enviar_peticion(cliente, pregunta, modelo=None,
                    system_instruction=None, response_schema=None):
    """Envía la pregunta al modelo y devuelve la respuesta cruda del SDK.

    Bloque 12: clasifica los errores.
    ValueError   -> no tiene sentido reintentar (credencial, petición mala).
    TimeoutError -> es momentáneo, se puede reintentar (429, 5xx, red).
    """
    modelo = modelo or os.getenv("GEMINI_MODEL", MODELO_POR_DEFECTO)
    config = armar_peticion(system_instruction, response_schema)

    try:
        return cliente.models.generate_content(
            model=modelo, contents=pregunta, config=config
        )
    except errors.ClientError as e:
        # 429: límite de uso, es momentáneo -> se puede reintentar
        if e.code == 429:
            raise TimeoutError(
                "Límite de uso excedido (429). Hay que esperar y reintentar."
            ) from e
        # 401/403, o 400 con la API key mala: no tiene sentido reintentar
        if e.code in (401, 403) or (e.code == 400 and "API key" in str(e.message)):
            raise ValueError(
                f"Credencial inválida o sin permiso (código {e.code}). "
                "Revisa tu GEMINI_API_KEY."
            ) from e
        raise ValueError(
            f"El servicio rechazó la petición (código {e.code}): {e.message}. "
            "Revisa el nombre del modelo y la petición."
        ) from e
    except errors.ServerError as e:
        # 5xx: error del proveedor, puede ser momentáneo
        raise TimeoutError(
            f"El servicio tuvo un error interno (código {e.code}). "
            "Hay que esperar y reintentar."
        ) from e
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise TimeoutError(
            "No se pudo conectar con el servicio. Puede ser momentáneo."
        ) from e


def extraer_texto(respuesta):
    """Obtiene el texto generado; falla con un mensaje claro si no viene."""
    texto = getattr(respuesta, "text", None)
    if not texto:
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        )
    return texto


def parsear_respuesta_json(texto, claves_esperadas):
    """Convierte el texto del modelo en un diccionario y revisa sus claves."""
    # 1. Limpiar: quitar espacios y las marcas ```json ... ``` si el modelo las puso
    limpio = texto.strip()
    limpio = re.sub(r"^```(?:json)?\s*", "", limpio)  # borra ```json del inicio
    limpio = re.sub(r"\s*```$", "", limpio)           # borra ``` del final

    # 2. Convertir el texto en un diccionario de Python
    try:
        datos = json.loads(limpio)
    except json.JSONDecodeError as e:
        raise ValueError("La respuesta del modelo no es JSON válido.") from e

    # 3. Revisar que sea un diccionario y que traiga todas las claves
    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON no es un objeto.")
    for clave in claves_esperadas:
        if clave not in datos:
            raise ValueError(f"Falta la clave '{clave}' en la respuesta.")

    # 4. Todo bien
    return datos


def obtener_precios(modelo):
    """Devuelve (precio_entrada, precio_salida) del modelo, o falla con un mensaje claro."""
    precios = PRECIOS.get(modelo)
    if precios is None:
        raise RuntimeError(
            f"No hay precios cargados para el modelo '{modelo}'. "
            "Agrégalo al diccionario PRECIOS."
        )
    return precios


def calcular_costo(respuesta, precio_entrada, precio_salida):
    """Devuelve tokens y costo (en nanodólares enteros) a partir de usage_metadata."""
    uso = getattr(respuesta, "usage_metadata", None)
    if not uso:
        raise RuntimeError(
            "La respuesta no trae usage_metadata, no se puede calcular el costo."
        )

    # "or 0" cubre tanto el atributo ausente como el valor None
    tokens_entrada = getattr(uso, "prompt_token_count", None) or 0
    tokens_respuesta = getattr(uso, "candidates_token_count", None) or 0
    tokens_razonamiento = getattr(uso, "thoughts_token_count", None) or 0

    # Los tokens de razonamiento se cobran como salida
    tokens_salida = tokens_respuesta + tokens_razonamiento

    costo = tokens_entrada * precio_entrada + tokens_salida * precio_salida
    return {
        "tokens_entrada": tokens_entrada,
        "tokens_salida": tokens_salida,
        "costo_nanodolares": costo,
    }


# --- Bloque 12-13: reintento con backoff exponencial, techo y jitter ---
def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    """Reintenta la función solo ante TimeoutError, esperando cada vez más."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} falló. "
                  f"Reintentando en {espera_con_jitter:.1f}s...")
            time.sleep(espera_con_jitter)


# --- Bloque 13: costo por operación y acumulado de la sesión ---
costo_total_sesion = 0  # en nanodólares


def registrar_costo(respuesta, modelo):
    """Calcula el costo real de la operación (precios oficiales) y lo acumula."""
    global costo_total_sesion
    precio_entrada, precio_salida = obtener_precios(modelo)
    uso = calcular_costo(respuesta, precio_entrada, precio_salida)
    costo_total_sesion += uso["costo_nanodolares"]
    print(
        f"Operación: {uso['tokens_entrada']}/{uso['tokens_salida']} tokens, "
        f"costo US$ {uso['costo_nanodolares'] / NANODOLARES_POR_DOLAR:.6f} "
        f"(acumulado: US$ {costo_total_sesion / NANODOLARES_POR_DOLAR:.6f})"
    )
    return uso["costo_nanodolares"]


# --- Bloque 13: interfaz pública que une todo ---
def consultar_modelo(pregunta, system_instruction=None, modelo=None, cliente=None):
    """Valida, envía con reintento, registra el costo y devuelve el texto."""
    pregunta = validar_pregunta(pregunta)
    cliente = cliente or crear_cliente()
    modelo = modelo or os.getenv("GEMINI_MODEL", MODELO_POR_DEFECTO)
    try:
        respuesta = con_reintento(
            lambda: enviar_peticion(
                cliente, pregunta, modelo, system_instruction=system_instruction
            )
        )
    except TimeoutError as e:
        raise RuntimeError(
            "El servicio no respondió tras varios intentos. Intenta más tarde."
        ) from e
    registrar_costo(respuesta, modelo)
    return extraer_texto(respuesta)


def medir_latencia(cliente, pregunta, modelo, ciclos=CICLOS_POR_MODELO):
    """Mide cuánto tarda enviar_peticion, repetida varias veces, y resume los tiempos."""
    if ciclos < 1:
        raise ValueError("Los ciclos deben ser al menos 1")

    tiempos = []
    respuesta = None
    for _ in range(ciclos):
        inicio = time.perf_counter()
        respuesta = enviar_peticion(cliente, pregunta, modelo)
        fin = time.perf_counter()
        tiempos.append(fin - inicio)

    return {
        "modelo": modelo,
        "ciclos": ciclos,
        "tiempos": tiempos,
        "promedio": sum(tiempos) / len(tiempos),
        "mediana": statistics.median(tiempos),
        "minimo": min(tiempos),
        "maximo": max(tiempos),
        # Se conserva la última respuesta para calcular tokens y costo
        "ultima_respuesta": respuesta,
    }
#obtener_dato_de_prueba
def obtener_dato_de_prueba(pregunta, system_instruction=None, response_schema=None):
    """Valida, envía, extrae y, si hay esquema, convierte la respuesta en diccionario.
    Devuelve el resultado, o None si algo falla."""
    try:
        pregunta = validar_pregunta(pregunta)
        cliente = crear_cliente()
        respuesta = enviar_peticion(
            cliente, pregunta,
            system_instruction=system_instruction,
            response_schema=response_schema,
        )
        texto = extraer_texto(respuesta)
        if response_schema:
            # Las claves esperadas son las que el esquema marca como "required"
            return parsear_respuesta_json(texto, response_schema.get("required", []))
        return texto
    except (ValueError, RuntimeError, TimeoutError) as error:
        print("No se pudo completar la operación:", error)
        return None


if __name__ == "__main__":
    pregunta = (
        "Hola, confirma con un mensaje corto que mi entorno Python está "
        "bien configurado."
    )
    try:
        cliente = crear_cliente()
        pregunta_validada = validar_pregunta(pregunta)

        # Petición principal, con el modelo explícito para buscar su precio
        modelo_principal = os.getenv("GEMINI_MODEL", MODELO_POR_DEFECTO)
        respuesta = enviar_peticion(cliente, pregunta_validada, modelo_principal)

        print("Respuesta del modelo:")
        print(extraer_texto(respuesta))

        precio_entrada, precio_salida = obtener_precios(modelo_principal)
        uso = calcular_costo(respuesta, precio_entrada, precio_salida)
        costo_usd = uso["costo_nanodolares"] / NANODOLARES_POR_DOLAR

        print(f"\nModelo: {modelo_principal}")
        print(f"Tokens de entrada: {uso['tokens_entrada']}")
        print(f"Tokens de salida: {uso['tokens_salida']}")
        print(f"Costo estimado (precio oficial): US$ {costo_usd:.6f}")

        # Comparación: misma pregunta corta para todos los modelos
        pregunta_latencia = validar_pregunta(
            "Cuánto es 2 + 2? Dame solo el resultado"
        )
        print(f"\nComparación ({CICLOS_POR_MODELO} ciclos por modelo):")
        for modelo in MODELOS_A_COMPARAR:
            # Si un modelo falla, se omite y se sigue con el siguiente
            try:
                resultado = medir_latencia(cliente, pregunta_latencia, modelo)
                p_entrada, p_salida = obtener_precios(modelo)
                uso_modelo = calcular_costo(
                    resultado["ultima_respuesta"], p_entrada, p_salida
                )
            except (RuntimeError, ValueError, TimeoutError) as error:
                print(f"{modelo}: se omite ({error})")
                continue

            costo_modelo = uso_modelo["costo_nanodolares"] / NANODOLARES_POR_DOLAR
            print(
                f"{modelo}: "
                f"prom {resultado['promedio']:.2f} s | "
                f"mediana {resultado['mediana']:.2f} s | "
                f"mín {resultado['minimo']:.2f} s | "
                f"máx {resultado['maximo']:.2f} s | "
                f"tokens {uso_modelo['tokens_entrada']}/{uso_modelo['tokens_salida']} | "
                f"costo US$ {costo_modelo:.6f}"
            )

    except (ValueError, RuntimeError, TimeoutError) as error:
        print("No se pudo completar la operación:", error)
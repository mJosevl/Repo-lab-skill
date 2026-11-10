"""Crea el modelo de Gemini para LangChain, leyendo la clave del .env."""
import os

from dotenv import load_dotenv

load_dotenv()


def crear_modelo(nombre: str = "gemini-3.5-flash-lite", timeout: int = 15):
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=nombre,
        google_api_key=os.getenv("GEMINI_API_KEY"),
        timeout=timeout,
        max_retries=2,
    )

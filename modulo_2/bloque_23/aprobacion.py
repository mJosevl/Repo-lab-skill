"""Bloque 23 · nexo_desk: punto de aprobación humana.

Relanzar un job (Rerun) es una acción sensible: el agente puede PROPONERLA,
pero solo se ejecuta si un humano escribe 's'. Funciona en Windows
(usa input(), no select(), que en Windows no sirve para el teclado).
"""
from datetime import datetime

from langchain_core.tools import tool

from herramientas import buscar_job

registro_aprobaciones: list[dict] = []


def pedir_confirmacion(mensaje: str) -> str:
    """Pregunta al humano. Se reemplaza en las pruebas por una respuesta fija."""
    return input(mensaje)


def esperar_aprobacion(mensaje: str) -> bool:
    respuesta = pedir_confirmacion(mensaje)
    return respuesta.strip().lower() == "s"


def registrar_aprobacion(herramienta: str, argumentos: dict, aprobado: bool) -> None:
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "momento": datetime.now().isoformat(),
    })


@tool
def relanzar_job(nombre_job: str) -> str:
    """Relanza (Rerun) un job de Control-M. Acción sensible: requiere
    aprobación humana antes de ejecutarse."""
    job = buscar_job(nombre_job)
    if job is None:
        return f"No encontré el job {nombre_job}; no se relanzó nada."

    aprobado = esperar_aprobacion(
        f"\nnexo_desk quiere relanzar {nombre_job.upper()} "
        f"(Order ID {job['order_id']}, estado {job['estado']}). ¿Aprobar? (s/n): "
    )
    registrar_aprobacion("relanzar_job", {"nombre_job": nombre_job}, aprobado)

    if not aprobado:
        return "Relanzamiento NO aprobado por el supervisor humano. No se hizo nada."
    # Simulación: en producción aquí iría la llamada real a Control-M.
    return f"(Simulado) Rerun de {nombre_job.upper()} enviado, Order ID {job['order_id']}."


if __name__ == "__main__":
    print(relanzar_job.invoke({"nombre_job": "CARGA_INVENTARIO"}))
    print("Registro:", registro_aprobaciones)

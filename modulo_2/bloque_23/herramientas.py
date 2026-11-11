"""Bloque 22 · herramientas con args_schema (Pydantic).

Datos INVENTADOS: ningún job real de clientes.
"""
from langchain_core.tools import tool
from pydantic import BaseModel, Field

JOBS = {
    "RESPALDO_DIARIO": {
        "estado": "Ended OK", "order_id": "0a1b2", "host": "srv-demo-01",
        "historial": ["Wait Condition 22:00", "Executing 23:00", "Ended OK 23:40"],
    },
    "CARGA_INVENTARIO": {
        "estado": "Ended Not OK", "order_id": "0a1f3", "host": "srv-demo-03",
        "historial": ["Executing 02:00", "Ended Not OK 02:15 (código de salida 1)"],
    },
    "REPORTE_VENTAS": {
        "estado": "Executing (hace 3 horas)", "order_id": "0a1d9", "host": "srv-demo-01",
        "historial": ["Wait Time 06:00", "Executing 07:00"],
    },
}


def buscar_job(nombre_job: str):
    return JOBS.get(nombre_job.strip().upper())


class ArgumentosConsultaJob(BaseModel):
    nombre_job: str = Field(
        description="Nombre exacto del job de Control-M, por ejemplo 'RESPALDO_DIARIO'."
    )
    incluir_historial: bool = Field(
        default=False,
        description="Si es True, incluye los cambios de estado del día, no solo el actual.",
    )


@tool("consultar_job", args_schema=ArgumentosConsultaJob)
def consultar_job(nombre_job: str, incluir_historial: bool = False) -> str:
    """Consulta el estado de un job de Control-M y, si se pide, su historial del día."""
    job = buscar_job(nombre_job)
    if job is None:
        return f"No encontré el job {nombre_job}. Revisa el nombre exacto."
    texto = f"{nombre_job.upper()}: {job['estado']} (host {job['host']}, Order ID {job['order_id']})"
    if incluir_historial:
        texto += ". Historial: " + " -> ".join(job["historial"])
    return texto


@tool
def contar_jobs_por_estado(estado: str) -> str:
    """Cuenta cuántos jobs hay en un estado, por ejemplo 'Ended Not OK'.
    Usar cuando el operador pregunta cuántos jobs fallaron o están ejecutando."""
    nombres = [n for n, j in JOBS.items() if estado.lower() in j["estado"].lower()]
    if not nombres:
        return f"No hay jobs en estado {estado}."
    return f"{len(nombres)} job(s) en estado {estado}: {', '.join(nombres)}."


HERRAMIENTAS = [consultar_job, contar_jobs_por_estado]

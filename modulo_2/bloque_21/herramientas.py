"""Herramientas de nexo_desk. Datos INVENTADOS: ningún job real de clientes."""
from langchain_core.tools import tool

JOBS = {
    "RESPALDO_DIARIO": {"estado": "Ended OK", "order_id": "0a1b2", "host": "srv-demo-01"},
    "CIERRE_MENSUAL": {"estado": "Wait Condition", "order_id": "0a1c7", "host": "srv-demo-02"},
    "REPORTE_VENTAS": {"estado": "Executing (hace 3 horas)", "order_id": "0a1d9", "host": "srv-demo-01"},
    "CARGA_INVENTARIO": {"estado": "Ended Not OK", "order_id": "0a1f3", "host": "srv-demo-03"},
}


def _buscar(nombre_job: str):
    """Devuelve el job o None. try/except: el mismo patrón que se usaría
    con una consulta real a Control-M que puede fallar."""
    try:
        return JOBS[nombre_job.strip().upper()]
    except (KeyError, AttributeError):
        return None


@tool
def consultar_estado_job(nombre_job: str) -> str:
    """Devuelve el estado actual de un job de Control-M por su nombre.
    Usar cuando el operador pregunta si un job corrió, falló o sigue ejecutando."""
    job = _buscar(nombre_job)
    if job is None:
        return f"No encontré el job {nombre_job}. Revisa el nombre exacto."
    return f"{nombre_job.upper()} está en estado {job['estado']} (host {job['host']})."


@tool
def buscar_order_id(nombre_job: str) -> str:
    """Devuelve el Order ID de un job ordenado hoy en Control-M.
    Usar cuando el operador necesita el Order ID para revisar o relanzar un job."""
    job = _buscar(nombre_job)
    if job is None:
        return f"No encontré el job {nombre_job}, así que no hay Order ID."
    return f"El Order ID de {nombre_job.upper()} es {job['order_id']}."


HERRAMIENTAS = [consultar_estado_job, buscar_order_id]
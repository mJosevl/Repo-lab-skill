"""Pruebas de las herramientas: se llaman directo, sin modelo ni API."""
from herramientas import buscar_order_id, consultar_estado_job


def test_estado_de_un_job_que_existe():
    assert "Ended Not OK" in consultar_estado_job.invoke({"nombre_job": "CARGA_INVENTARIO"})


def test_nombre_en_minusculas_tambien_funciona():
    assert "0a1d9" in buscar_order_id.invoke({"nombre_job": "reporte_ventas"})


def test_job_inexistente_no_inventa_datos():
    respuesta = consultar_estado_job.invoke({"nombre_job": "NO_EXISTE"})
    assert respuesta.startswith("No encontré")


def test_las_herramientas_tienen_descripcion():
    # El agente decide qué herramienta usar leyendo esta descripción
    assert "estado" in consultar_estado_job.description
    assert "Order ID" in buscar_order_id.description

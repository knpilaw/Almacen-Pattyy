"""
Pruebas integrales de servicios del Backend
Ejecutar con: py tests/test_backend.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.services.auth_service import AuthService
from backend.services.producto_service import ProductoService
from backend.services.caja_service import CajaService
from backend.services.venta_service import VentaService
from backend.services.inventario_service import InventarioService
from backend.services.reporte_service import ReporteService


def run_tests():
    print(">>> INICIANDO PRUEBAS DEL BACKEND MINIMARKET PATTY <<<\n")

    # 1. Prueba de Autenticación
    print("[1] Probando AuthService...")
    user = AuthService.autenticar("patricia", "admin123")
    assert user is not None, "Error: No se pudo autenticar a 'patricia'."
    assert user.es_administrador(), "Error: Patricia debería tener rol ADMINISTRADOR."
    print(f"    OK -> Usuario autenticado: {user.nombre_completo} (Rol: {user.rol})")

    cajero = AuthService.autenticar("cajero", "cajero123")
    assert cajero is not None and not cajero.es_administrador()
    print(f"    OK -> Cajero autenticado: {cajero.nombre_completo}")

    # 2. Prueba de Búsqueda por Lector de Código de Barras
    print("\n[2] Probando ProductoService (Lector Código de Barras)...")
    coca = ProductoService.buscar_por_codigo("780223456701")
    assert coca is not None, "Error: No se encontró producto con código '780223456701'."
    print(f"    OK -> Escaneado: {coca.nombre} | Precio: ${coca.precio_venta} | Stock: {coca.stock_actual}")
    stock_inicial_coca = coca.stock_actual

    # 3. Apertura de Caja
    print("\n[3] Probando CajaService (Apertura de turno)...")
    caja = CajaService.abrir_caja(usuario_id=user.id, monto_inicial=20000)
    assert caja is not None and caja.estado == "ABIERTA"
    print(f"    OK -> Caja ID {caja.id} abierta con fondo inicial de ${caja.monto_inicial}")

    # 4. Procesamiento de Venta en el POS
    print("\n[4] Probando VentaService (Venta con descuento automático)...")
    venta = VentaService.procesar_venta(
        usuario_id=user.id,
        items=[
            {"producto_id": coca.id, "cantidad": 2},
        ],
        metodo_pago="EFECTIVO",
        monto_pagado=5000,
    )
    assert venta is not None, "Error: Falló el procesamiento de la venta."
    assert venta.total == (coca.precio_venta * 2)
    assert venta.vuelto == (5000 - venta.total)
    print(f"    OK -> Ticket generado: {venta.codigo_boleta} | Total: ${venta.total} | Vuelto: ${venta.vuelto}")

    # Verificar que el stock se descontó
    coca_despues = ProductoService.obtener_por_id(coca.id)
    assert coca_despues.stock_actual == (stock_inicial_coca - 2), "Error: El stock no se descontó correctamente."
    print(f"    OK -> Stock descontado exitosamente: {stock_inicial_coca} -> {coca_despues.stock_actual}")

    # 5. Ajuste manual de Inventario (Bodega)
    print("\n[5] Probando InventarioService (Ajuste por compra a proveedor)...")
    mov = InventarioService.registrar_ajuste(
        producto_id=coca.id,
        usuario_id=user.id,
        tipo_movimiento="ENTRADA_COMPRA",
        cantidad=10,
        motivo="Factura distribuidor N°4821",
    )
    assert mov.stock_nuevo == (coca_despues.stock_actual + 10)
    print(f"    OK -> Entrada registrada: +10 unid. Nuevo stock: {mov.stock_nuevo}")

    # 6. Reportes y Cierre de Jornada
    print("\n[6] Probando ReporteService...")
    resumen = ReporteService.resumen_dashboard()
    print(f"    OK -> Productos en catálogo: {resumen['inventario']['total_productos']}")
    print(f"    OK -> Ventas registradas hoy: {resumen['ventas_hoy']['transacciones_hoy']} transacciones")
    print(f"    OK -> Total recaudado hoy: ${resumen['ventas_hoy']['total_ventas_hoy']}")
    print(f"    OK -> Utilidad estimada hoy: ${resumen['ventas_hoy']['utilidad_estimada_hoy']}")

    mas_vendidos = ReporteService.reporte_mas_vendidos(limite=5)
    print(f"    OK -> Top productos rotación: {[p['nombre'] for p in mas_vendidos]}")

    print("\n=======================================================")
    print("  ¡TODAS LAS PRUEBAS DEL BACKEND PASARON CON ÉXITO!    ")
    print("=======================================================\n")


if __name__ == "__main__":
    run_tests()

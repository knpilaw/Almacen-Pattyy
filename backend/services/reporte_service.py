"""
Servicio para reportes analíticos, cierres consolidados e inteligencia de inventario
"""

from datetime import date
from typing import Any, Dict, List, Optional
from ..database import get_db_connection


class ReporteService:
    @staticmethod
    def resumen_dashboard() -> Dict[str, Any]:
        """Resumen ejecutivo para la pantalla principal del administrador."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # 1. Cantidad y valorización del inventario
            cursor.execute(
                """
                SELECT 
                    COUNT(*) AS total_productos,
                    COALESCE(SUM(stock_actual), 0) AS total_unidades_bodega,
                    COALESCE(SUM(stock_actual * precio_costo), 0) AS valor_inventario_costo,
                    COALESCE(SUM(stock_actual * precio_venta), 0) AS valor_inventario_venta
                FROM productos
                WHERE activo = 1
                """
            )
            inv_stats = dict(cursor.fetchone())

            # 2. Cantidad de productos con stock bajo
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1 AND stock_actual <= stock_minimo")
            inv_stats["productos_stock_bajo"] = cursor.fetchone()[0]

            # 3. Ventas de hoy
            cursor.execute(
                """
                SELECT 
                    COUNT(*) AS transacciones_hoy,
                    COALESCE(SUM(total), 0) AS total_ventas_hoy,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'EFECTIVO' THEN total ELSE 0 END), 0) AS efectivo_hoy,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'MERCADO_PAGO' THEN total ELSE 0 END), 0) AS mercado_pago_hoy
                FROM ventas
                WHERE date(fecha_hora) = date('now') AND estado = 'COMPLETADA'
                """
            )
            ventas_hoy = dict(cursor.fetchone())

            # 4. Utilidad estimada de hoy
            cursor.execute(
                """
                SELECT 
                    COALESCE(SUM((d.precio_unitario - d.costo_unitario) * d.cantidad), 0) AS utilidad_estimada_hoy
                FROM detalle_ventas d
                JOIN ventas v ON d.venta_id = v.id
                WHERE date(v.fecha_hora) = date('now') AND v.estado = 'COMPLETADA'
                """
            )
            ventas_hoy["utilidad_estimada_hoy"] = cursor.fetchone()[0]

            return {
                "inventario": inv_stats,
                "ventas_hoy": ventas_hoy,
            }
        finally:
            conn.close()

    @staticmethod
    def reporte_mas_vendidos(limite: int = 10, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> List[Dict[str, Any]]:
        """Identifica los artículos de mayor rotación (unidades vendidas e ingresos generados)."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.id,
                    p.codigo_barra,
                    p.nombre,
                    c.nombre AS categoria,
                    p.stock_actual,
                    SUM(d.cantidad) AS unidades_vendidas,
                    SUM(d.subtotal) AS total_recaudado,
                    SUM((d.precio_unitario - d.costo_unitario) * d.cantidad) AS utilidad_generada
                FROM detalle_ventas d
                JOIN ventas v ON d.venta_id = v.id
                JOIN productos p ON d.producto_id = p.id
                JOIN categorias c ON p.categoria_id = c.id
                WHERE v.estado = 'COMPLETADA'
            """
            params: List[Any] = []
            if fecha_inicio:
                query += " AND date(v.fecha_hora) >= date(?)"
                params.append(fecha_inicio)
            if fecha_fin:
                query += " AND date(v.fecha_hora) <= date(?)"
                params.append(fecha_fin)

            query += """
                GROUP BY p.id, p.codigo_barra, p.nombre, c.nombre, p.stock_actual
                ORDER BY unidades_vendidas DESC
                LIMIT ?
            """
            params.append(limite)

            cursor.execute(query, tuple(params))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def reporte_diario(fecha: Optional[str] = None) -> Dict[str, Any]:
        """Genera el consolidado diario de ventas (tipo cierre de jornada)."""
        fecha_consulta = fecha or date.today().isoformat()
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    COUNT(*) AS total_ventas,
                    COALESCE(SUM(total), 0) AS total_recaudado,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'EFECTIVO' THEN total ELSE 0 END), 0) AS total_efectivo,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'MERCADO_PAGO' THEN total ELSE 0 END), 0) AS total_mercado_pago,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'TRANSFERENCIA' THEN total ELSE 0 END), 0) AS total_transferencia
                FROM ventas
                WHERE date(fecha_hora) = date(?) AND estado = 'COMPLETADA'
                """,
                (fecha_consulta,),
            )
            totales = dict(cursor.fetchone())

            cursor.execute(
                """
                SELECT 
                    COALESCE(SUM((d.precio_unitario - d.costo_unitario) * d.cantidad), 0) AS ganancia_bruta
                FROM detalle_ventas d
                JOIN ventas v ON d.venta_id = v.id
                WHERE date(v.fecha_hora) = date(?) AND v.estado = 'COMPLETADA'
                """,
                (fecha_consulta,),
            )
            totales["ganancia_bruta"] = cursor.fetchone()[0]
            totales["fecha"] = fecha_consulta

            return totales
        finally:
            conn.close()

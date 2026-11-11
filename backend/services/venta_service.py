"""
Servicio de Ventas y Facturación Interna POS
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from ..database import get_db_connection
from ..models.venta import DetalleVenta, Venta
from .caja_service import CajaService


class VentaService:
    @staticmethod
    def generar_codigo_boleta(conn) -> str:
        """Genera un código correlativo para el ticket interno, ej: BOL-20261110-0001."""
        hoy = datetime.now().strftime("%Y%m%d")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ventas WHERE fecha_hora >= date('now', 'start of day')")
        correlativo = cursor.fetchone()[0] + 1
        return f"BOL-{hoy}-{correlativo:04d}"

    @staticmethod
    def procesar_venta(
        usuario_id: int,
        items: List[Dict[str, Any]],
        metodo_pago: str = "EFECTIVO",
        monto_pagado: int = 0,
    ) -> Venta:
        """
        Registra una venta de forma atómica:
        1. Valida disponibilidad de stock.
        2. Inserta la venta principal vinculada a la caja abierta.
        3. Inserta cada detalle (congelando precio y costo).
        4. Descuenta el stock en la tabla productos.
        5. Registra el movimiento en la bitácora de inventario.
        """
        if not items:
            raise ValueError("La venta debe contener al menos un producto.")

        if metodo_pago not in ("EFECTIVO", "MERCADO_PAGO", "TRANSFERENCIA"):
            raise ValueError(f"Método de pago '{metodo_pago}' no soportado.")

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Obtener caja activa para el usuario (si existe)
            caja_activa = CajaService.obtener_caja_activa(usuario_id)
            cierre_caja_id = caja_activa.id if caja_activa else None

            # 1. Calcular total y validar productos
            total_calculado = 0
            items_procesados = []

            for item in items:
                prod_id = int(item["producto_id"])
                cantidad = int(item["cantidad"])
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a cero.")

                cursor.execute(
                    "SELECT id, codigo_barra, nombre, precio_costo, precio_venta, stock_actual, activo FROM productos WHERE id = ?",
                    (prod_id,),
                )
                prod = cursor.fetchone()
                if not prod or not prod["activo"]:
                    raise ValueError(f"El producto ID {prod_id} no está disponible.")

                if prod["stock_actual"] < cantidad:
                    raise ValueError(
                        f"Stock insuficiente para '{prod['nombre']}'. Disponible: {prod['stock_actual']}, solicitado: {cantidad}."
                    )

                subtotal = prod["precio_venta"] * cantidad
                total_calculado += subtotal

                items_procesados.append({
                    "producto_id": prod["id"],
                    "codigo_barra": prod["codigo_barra"],
                    "nombre": prod["nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": prod["precio_venta"],
                    "costo_unitario": prod["precio_costo"],
                    "subtotal": subtotal,
                    "stock_anterior": prod["stock_actual"],
                    "stock_nuevo": prod["stock_actual"] - cantidad,
                })

            # Validar vuelto si es efectivo
            monto_pagado_final = monto_pagado if monto_pagado > 0 else total_calculado
            if metodo_pago == "EFECTIVO" and monto_pagado_final < total_calculado:
                raise ValueError("El monto entregado en efectivo es menor al total de la venta.")

            vuelto = max(0, monto_pagado_final - total_calculado)
            codigo_boleta = VentaService.generar_codigo_boleta(conn)

            # 2. Insertar encabezado de venta
            cursor.execute(
                """
                INSERT INTO ventas (
                    codigo_boleta, usuario_id, cierre_caja_id, total,
                    metodo_pago, monto_pagado, vuelto, estado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'COMPLETADA')
                """,
                (
                    codigo_boleta,
                    usuario_id,
                    cierre_caja_id,
                    total_calculado,
                    metodo_pago,
                    monto_pagado_final,
                    vuelto,
                ),
            )
            venta_id = cursor.lastrowid

            # 3. Insertar detalles, descontar stock y registrar bitácora
            detalles_entidad = []
            for item in items_procesados:
                # Detalle
                cursor.execute(
                    """
                    INSERT INTO detalle_ventas (
                        venta_id, producto_id, cantidad, precio_unitario, costo_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        venta_id,
                        item["producto_id"],
                        item["cantidad"],
                        item["precio_unitario"],
                        item["costo_unitario"],
                        item["subtotal"],
                    ),
                )
                det_id = cursor.lastrowid

                # Descontar stock
                cursor.execute(
                    """
                    UPDATE productos 
                    SET stock_actual = ?, actualizado_en = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (item["stock_nuevo"], item["producto_id"]),
                )

                # Auditoría inventario
                cursor.execute(
                    """
                    INSERT INTO movimientos_inventario (
                        producto_id, usuario_id, tipo_movimiento,
                        cantidad, stock_anterior, stock_nuevo, motivo
                    ) VALUES (?, ?, 'VENTA', ?, ?, ?, ?)
                    """,
                    (
                        item["producto_id"],
                        usuario_id,
                        item["cantidad"],
                        item["stock_anterior"],
                        item["stock_nuevo"],
                        f"Venta ticket {codigo_boleta}",
                    ),
                )

                detalles_entidad.append(
                    DetalleVenta(
                        id=det_id,
                        venta_id=venta_id,
                        producto_id=item["producto_id"],
                        cantidad=item["cantidad"],
                        precio_unitario=item["precio_unitario"],
                        costo_unitario=item["costo_unitario"],
                        subtotal=item["subtotal"],
                        producto_nombre=item["nombre"],
                        codigo_barra=item["codigo_barra"],
                    )
                )

            conn.commit()

            # Retornar objeto completo
            cursor.execute("SELECT nombre_completo FROM usuarios WHERE id = ?", (usuario_id,))
            usuario_nombre = cursor.fetchone()["nombre_completo"]

            return Venta(
                id=venta_id,
                codigo_boleta=codigo_boleta,
                usuario_id=usuario_id,
                cierre_caja_id=cierre_caja_id,
                total=total_calculado,
                metodo_pago=metodo_pago,
                monto_pagado=monto_pagado_final,
                vuelto=vuelto,
                estado="COMPLETADA",
                usuario_nombre=usuario_nombre,
                detalles=detalles_entidad,
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(venta_id: int) -> Optional[Venta]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.*, u.nombre_completo AS usuario_nombre
                FROM ventas v
                JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.id = ?
                """,
                (venta_id,),
            )
            v_row = cursor.fetchone()
            if not v_row:
                return None

            cursor.execute(
                """
                SELECT d.*, p.nombre AS producto_nombre, p.codigo_barra
                FROM detalle_ventas d
                JOIN productos p ON d.producto_id = p.id
                WHERE d.venta_id = ?
                """,
                (venta_id,),
            )
            detalles = [DetalleVenta.from_row(d) for d in cursor.fetchall()]
            venta = Venta.from_row(v_row)
            venta.detalles = detalles
            return venta
        finally:
            conn.close()

    @staticmethod
    def listar_recientes(limit: int = 50) -> List[Venta]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.*, u.nombre_completo AS usuario_nombre
                FROM ventas v
                JOIN usuarios u ON v.usuario_id = u.id
                ORDER BY v.fecha_hora DESC
                LIMIT ?
                """,
                (limit,),
            )
            ventas = [Venta.from_row(r) for r in cursor.fetchall()]
            return ventas
        finally:
            conn.close()

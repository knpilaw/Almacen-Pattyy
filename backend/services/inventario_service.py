"""
Servicio para movimientos y ajustes de inventario / bodega
"""

from typing import List, Optional
from ..database import get_db_connection
from ..models.inventario import MovimientoInventario


class InventarioService:
    @staticmethod
    def registrar_ajuste(
        producto_id: int,
        usuario_id: int,
        tipo_movimiento: str,
        cantidad: int,
        motivo: Optional[str] = None,
    ) -> MovimientoInventario:
        """
        Registra una entrada de mercadería, ajuste por conteo físico o merma.
        tipo_movimiento: 'ENTRADA_COMPRA' | 'AJUSTE_POSITIVO' | 'AJUSTE_NEGATIVO' | 'MERMA_VENCIMIENTO'
        """
        tipos_validos = ("ENTRADA_COMPRA", "AJUSTE_POSITIVO", "AJUSTE_NEGATIVO", "MERMA_VENCIMIENTO")
        if tipo_movimiento not in tipos_validos:
            raise ValueError(f"Tipo de movimiento '{tipo_movimiento}' inválido.")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, stock_actual FROM productos WHERE id = ?", (producto_id,))
            prod = cursor.fetchone()
            if not prod:
                raise ValueError("Producto no encontrado.")

            stock_anterior = prod["stock_actual"]

            # Calcular nuevo stock según operación
            if tipo_movimiento in ("ENTRADA_COMPRA", "AJUSTE_POSITIVO"):
                stock_nuevo = stock_anterior + cantidad
            else:  # AJUSTE_NEGATIVO, MERMA_VENCIMIENTO
                if stock_anterior < cantidad:
                    raise ValueError(
                        f"No es posible restar {cantidad} unidades. Stock actual disponible: {stock_anterior}."
                    )
                stock_nuevo = stock_anterior - cantidad

            # Actualizar producto
            cursor.execute(
                "UPDATE productos SET stock_actual = ?, actualizado_en = CURRENT_TIMESTAMP WHERE id = ?",
                (stock_nuevo, producto_id),
            )

            # Insertar movimiento
            cursor.execute(
                """
                INSERT INTO movimientos_inventario (
                    producto_id, usuario_id, tipo_movimiento,
                    cantidad, stock_anterior, stock_nuevo, motivo
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (producto_id, usuario_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, motivo or ""),
            )
            mov_id = cursor.lastrowid
            conn.commit()

            cursor.execute(
                """
                SELECT m.*, p.nombre AS producto_nombre, p.codigo_barra, u.nombre_completo AS usuario_nombre
                FROM movimientos_inventario m
                JOIN productos p ON m.producto_id = p.id
                JOIN usuarios u ON m.usuario_id = u.id
                WHERE m.id = ?
                """,
                (mov_id,),
            )
            return MovimientoInventario.from_row(cursor.fetchone())
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def listar_movimientos(producto_id: Optional[int] = None, limit: int = 100) -> List[MovimientoInventario]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT m.*, p.nombre AS producto_nombre, p.codigo_barra, u.nombre_completo AS usuario_nombre
                FROM movimientos_inventario m
                JOIN productos p ON m.producto_id = p.id
                JOIN usuarios u ON m.usuario_id = u.id
            """
            params = []
            if producto_id is not None:
                query += " WHERE m.producto_id = ?"
                params.append(producto_id)

            query += " ORDER BY m.fecha_hora DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, tuple(params))
            return [MovimientoInventario.from_row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

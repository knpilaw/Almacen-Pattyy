"""
Servicio para apertura, registro y Cierre de Caja
"""

from typing import Any, Dict, List, Optional
from ..database import get_db_connection
from ..models.venta import CierreCaja


class CajaService:
    @staticmethod
    def obtener_caja_activa(usuario_id: Optional[int] = None) -> Optional[CierreCaja]:
        """Busca una caja actualmente abierta. Si se pasa usuario_id, filtra por ese usuario."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT c.*, u.nombre_completo AS usuario_nombre
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.estado = 'ABIERTA'
            """
            params = []
            if usuario_id is not None:
                query += " AND c.usuario_id = ?"
                params.append(usuario_id)

            query += " ORDER BY c.id DESC LIMIT 1"
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            return CierreCaja.from_row(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def abrir_caja(usuario_id: int, monto_inicial: int) -> CierreCaja:
        """Abre un nuevo turno de caja. Si ya existe una abierta para el usuario, la retorna."""
        caja_existente = CajaService.obtener_caja_activa(usuario_id)
        if caja_existente:
            return caja_existente

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO cierres_caja (usuario_id, monto_inicial, total_esperado, estado)
                VALUES (?, ?, ?, 'ABIERTA')
                """,
                (usuario_id, monto_inicial, monto_inicial),
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
            return CajaService.obtener_por_id(nuevo_id)
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(cierre_id: int) -> Optional[CierreCaja]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.*, u.nombre_completo AS usuario_nombre
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.id = ?
                """,
                (cierre_id,),
            )
            row = cursor.fetchone()
            return CierreCaja.from_row(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def cerrar_caja(cierre_id: int, total_declarado: int, observaciones: Optional[str] = None) -> CierreCaja:
        """Calcula ventas del turno, computa diferencia respecto a lo declarado y cierra la caja."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # 1. Obtener la caja
            cursor.execute("SELECT * FROM cierres_caja WHERE id = ?", (cierre_id,))
            caja = cursor.fetchone()
            if not caja:
                raise ValueError("Turno de caja no encontrado.")

            monto_inicial = caja["monto_inicial"]

            # 2. Sumar ventas por método de pago asociadas a este turno
            cursor.execute(
                """
                SELECT 
                    COALESCE(SUM(CASE WHEN metodo_pago = 'EFECTIVO' THEN total ELSE 0 END), 0) AS ventas_efectivo,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'MERCADO_PAGO' THEN total ELSE 0 END), 0) AS ventas_mercado_pago,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'TRANSFERENCIA' THEN total ELSE 0 END), 0) AS ventas_transferencia
                FROM ventas
                WHERE cierre_caja_id = ? AND estado = 'COMPLETADA'
                """,
                (cierre_id,),
            )
            totales = cursor.fetchone()
            ventas_efectivo = totales["ventas_efectivo"]
            ventas_mp = totales["ventas_mercado_pago"]
            ventas_transf = totales["ventas_transferencia"]

            # El efectivo esperado en caja es el fondo inicial + ventas en efectivo
            total_esperado = monto_inicial + ventas_efectivo
            diferencia = total_declarado - total_esperado

            cursor.execute(
                """
                UPDATE cierres_caja SET
                    fecha_cierre = CURRENT_TIMESTAMP,
                    total_ventas_efectivo = ?,
                    total_ventas_mercado_pago = ?,
                    total_ventas_transferencia = ?,
                    total_esperado = ?,
                    total_declarado = ?,
                    diferencia = ?,
                    observaciones = ?,
                    estado = 'CERRADA'
                WHERE id = ?
                """,
                (
                    ventas_efectivo,
                    ventas_mp,
                    ventas_transf,
                    total_esperado,
                    total_declarado,
                    diferencia,
                    observaciones or "",
                    cierre_id,
                ),
            )
            conn.commit()
            return CajaService.obtener_por_id(cierre_id)
        finally:
            conn.close()

    @staticmethod
    def listar_cierres(limit: int = 30) -> List[CierreCaja]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.*, u.nombre_completo AS usuario_nombre
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                ORDER BY c.id DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [CierreCaja.from_row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

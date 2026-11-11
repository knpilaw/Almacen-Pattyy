"""
Modelo POO: MovimientoInventario
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MovimientoInventario:
    id: Optional[int]
    producto_id: int
    usuario_id: int
    tipo_movimiento: str  # 'ENTRADA_COMPRA' | 'VENTA' | 'AJUSTE_POSITIVO' | 'AJUSTE_NEGATIVO' | 'MERMA_VENCIMIENTO'
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    motivo: Optional[str] = None
    fecha_hora: Optional[str] = None
    producto_nombre: Optional[str] = None
    codigo_barra: Optional[str] = None
    usuario_nombre: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "producto_nombre": self.producto_nombre,
            "codigo_barra": self.codigo_barra,
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario_nombre,
            "tipo_movimiento": self.tipo_movimiento,
            "cantidad": self.cantidad,
            "stock_anterior": self.stock_anterior,
            "stock_nuevo": self.stock_nuevo,
            "motivo": self.motivo,
            "fecha_hora": self.fecha_hora,
        }

    @classmethod
    def from_row(cls, row) -> "MovimientoInventario":
        keys = row.keys()
        return cls(
            id=row["id"],
            producto_id=row["producto_id"],
            usuario_id=row["usuario_id"],
            tipo_movimiento=row["tipo_movimiento"],
            cantidad=row["cantidad"],
            stock_anterior=row["stock_anterior"],
            stock_nuevo=row["stock_nuevo"],
            motivo=row["motivo"] if "motivo" in keys else None,
            fecha_hora=row["fecha_hora"] if "fecha_hora" in keys else None,
            producto_nombre=row["producto_nombre"] if "producto_nombre" in keys else None,
            codigo_barra=row["codigo_barra"] if "codigo_barra" in keys else None,
            usuario_nombre=row["usuario_nombre"] if "usuario_nombre" in keys else None,
        )

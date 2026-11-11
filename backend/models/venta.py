"""
Modelos POO: Venta, DetalleVenta y CierreCaja
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DetalleVenta:
    id: Optional[int]
    venta_id: Optional[int]
    producto_id: int
    cantidad: int
    precio_unitario: int
    costo_unitario: int
    subtotal: int
    producto_nombre: Optional[str] = None
    codigo_barra: Optional[str] = None

    @property
    def utilidad_linea(self) -> int:
        return (self.precio_unitario - self.costo_unitario) * self.cantidad

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "venta_id": self.venta_id,
            "producto_id": self.producto_id,
            "producto_nombre": self.producto_nombre,
            "codigo_barra": self.codigo_barra,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "costo_unitario": self.costo_unitario,
            "subtotal": self.subtotal,
            "utilidad_linea": self.utilidad_linea,
        }

    @classmethod
    def from_row(cls, row) -> "DetalleVenta":
        keys = row.keys()
        return cls(
            id=row["id"],
            venta_id=row["venta_id"] if "venta_id" in keys else None,
            producto_id=row["producto_id"],
            cantidad=row["cantidad"],
            precio_unitario=row["precio_unitario"],
            costo_unitario=row["costo_unitario"],
            subtotal=row["subtotal"],
            producto_nombre=row["producto_nombre"] if "producto_nombre" in keys else None,
            codigo_barra=row["codigo_barra"] if "codigo_barra" in keys else None,
        )


@dataclass
class Venta:
    id: Optional[int]
    codigo_boleta: str
    usuario_id: int
    total: int
    metodo_pago: str = "EFECTIVO"  # 'EFECTIVO' | 'MERCADO_PAGO' | 'TRANSFERENCIA'
    monto_pagado: int = 0
    vuelto: int = 0
    cierre_caja_id: Optional[int] = None
    fecha_hora: Optional[str] = None
    estado: str = "COMPLETADA"
    usuario_nombre: Optional[str] = None
    detalles: List[DetalleVenta] = field(default_factory=list)

    @property
    def utilidad_total(self) -> int:
        return sum(d.utilidad_linea for d in self.detalles)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo_boleta": self.codigo_boleta,
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario_nombre,
            "cierre_caja_id": self.cierre_caja_id,
            "fecha_hora": self.fecha_hora,
            "total": self.total,
            "metodo_pago": self.metodo_pago,
            "monto_pagado": self.monto_pagado,
            "vuelto": self.vuelto,
            "estado": self.estado,
            "utilidad_total": self.utilidad_total,
            "detalles": [d.to_dict() for d in self.detalles],
        }

    @classmethod
    def from_row(cls, row) -> "Venta":
        keys = row.keys()
        return cls(
            id=row["id"],
            codigo_boleta=row["codigo_boleta"],
            usuario_id=row["usuario_id"],
            total=row["total"],
            metodo_pago=row["metodo_pago"],
            monto_pagado=row["monto_pagado"],
            vuelto=row["vuelto"],
            cierre_caja_id=row["cierre_caja_id"] if "cierre_caja_id" in keys else None,
            fecha_hora=row["fecha_hora"] if "fecha_hora" in keys else None,
            estado=row["estado"] if "estado" in keys else "COMPLETADA",
            usuario_nombre=row["usuario_nombre"] if "usuario_nombre" in keys else None,
        )


@dataclass
class CierreCaja:
    id: Optional[int]
    usuario_id: int
    monto_inicial: int
    fecha_apertura: Optional[str] = None
    fecha_cierre: Optional[str] = None
    total_ventas_efectivo: int = 0
    total_ventas_mercado_pago: int = 0
    total_ventas_transferencia: int = 0
    total_esperado: int = 0
    total_declarado: int = 0
    diferencia: int = 0
    observaciones: Optional[str] = None
    estado: str = "ABIERTA"
    usuario_nombre: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario_nombre,
            "fecha_apertura": self.fecha_apertura,
            "fecha_cierre": self.fecha_cierre,
            "monto_inicial": self.monto_inicial,
            "total_ventas_efectivo": self.total_ventas_efectivo,
            "total_ventas_mercado_pago": self.total_ventas_mercado_pago,
            "total_ventas_transferencia": self.total_ventas_transferencia,
            "total_esperado": self.total_esperado,
            "total_declarado": self.total_declarado,
            "diferencia": self.diferencia,
            "observaciones": self.observaciones,
            "estado": self.estado,
        }

    @classmethod
    def from_row(cls, row) -> "CierreCaja":
        keys = row.keys()
        return cls(
            id=row["id"],
            usuario_id=row["usuario_id"],
            monto_inicial=row["monto_inicial"],
            fecha_apertura=row["fecha_apertura"] if "fecha_apertura" in keys else None,
            fecha_cierre=row["fecha_cierre"] if "fecha_cierre" in keys else None,
            total_ventas_efectivo=row["total_ventas_efectivo"],
            total_ventas_mercado_pago=row["total_ventas_mercado_pago"],
            total_ventas_transferencia=row["total_ventas_transferencia"] if "total_ventas_transferencia" in keys else 0,
            total_esperado=row["total_esperado"],
            total_declarado=row["total_declarado"],
            diferencia=row["diferencia"],
            observaciones=row["observaciones"] if "observaciones" in keys else None,
            estado=row["estado"],
            usuario_nombre=row["usuario_nombre"] if "usuario_nombre" in keys else None,
        )

"""
Modelos POO: Categoria y Producto
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Categoria:
    id: Optional[int]
    nombre: str
    descripcion: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
        }

    @classmethod
    def from_row(cls, row) -> "Categoria":
        return cls(
            id=row["id"],
            nombre=row["nombre"],
            descripcion=row["descripcion"],
        )


@dataclass
class Producto:
    id: Optional[int]
    codigo_barra: str
    nombre: str
    categoria_id: int
    precio_costo: int
    precio_venta: int
    stock_actual: int = 0
    stock_minimo: int = 5
    unidad_medida: str = "UNIDAD"
    descripcion: Optional[str] = None
    activo: int = 1
    actualizado_en: Optional[str] = None
    categoria_nombre: Optional[str] = None

    @property
    def margen_ganancia(self) -> int:
        """Ganancia unitaria en CLP (precio_venta - precio_costo)."""
        return self.precio_venta - self.precio_costo

    @property
    def porcentaje_margen(self) -> float:
        """Porcentaje de margen sobre el costo."""
        if self.precio_costo <= 0:
            return 0.0
        return round(((self.precio_venta - self.precio_costo) / self.precio_costo) * 100, 2)

    @property
    def stock_bajo(self) -> bool:
        """Indica si el stock actual está en o bajo el umbral mínimo."""
        return self.stock_actual <= self.stock_minimo

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo_barra": self.codigo_barra,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "categoria_id": self.categoria_id,
            "categoria_nombre": self.categoria_nombre,
            "precio_costo": self.precio_costo,
            "precio_venta": self.precio_venta,
            "stock_actual": self.stock_actual,
            "stock_minimo": self.stock_minimo,
            "unidad_medida": self.unidad_medida,
            "activo": bool(self.activo),
            "stock_bajo": self.stock_bajo,
            "margen_ganancia": self.margen_ganancia,
            "porcentaje_margen": self.porcentaje_margen,
            "actualizado_en": self.actualizado_en,
        }

    @classmethod
    def from_row(cls, row) -> "Producto":
        keys = row.keys()
        return cls(
            id=row["id"],
            codigo_barra=row["codigo_barra"],
            nombre=row["nombre"],
            descripcion=row["descripcion"] if "descripcion" in keys else None,
            categoria_id=row["categoria_id"],
            precio_costo=row["precio_costo"],
            precio_venta=row["precio_venta"],
            stock_actual=row["stock_actual"],
            stock_minimo=row["stock_minimo"],
            unidad_medida=row["unidad_medida"] if "unidad_medida" in keys else "UNIDAD",
            activo=row["activo"] if "activo" in keys else 1,
            actualizado_en=row["actualizado_en"] if "actualizado_en" in keys else None,
            categoria_nombre=row["categoria_nombre"] if "categoria_nombre" in keys else None,
        )

"""
Modelo POO: Usuario
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    id: Optional[int]
    nombre_usuario: str
    password_hash: str
    nombre_completo: str
    rol: str  # 'ADMINISTRADOR' | 'CAJERO'
    activo: int = 1
    creado_en: Optional[str] = None

    def es_administrador(self) -> bool:
        return self.rol == "ADMINISTRADOR"

    def to_dict(self, incluir_password: bool = False) -> dict:
        data = {
            "id": self.id,
            "nombre_usuario": self.nombre_usuario,
            "nombre_completo": self.nombre_completo,
            "rol": self.rol,
            "activo": bool(self.activo),
            "creado_en": self.creado_en,
        }
        if incluir_password:
            data["password_hash"] = self.password_hash
        return data

    @classmethod
    def from_row(cls, row) -> "Usuario":
        return cls(
            id=row["id"],
            nombre_usuario=row["nombre_usuario"],
            password_hash=row["password_hash"],
            nombre_completo=row["nombre_completo"],
            rol=row["rol"],
            activo=row["activo"],
            creado_en=row["creado_en"],
        )

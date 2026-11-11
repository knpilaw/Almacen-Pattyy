"""
Servicio de Autenticación y Gestión de Usuarios
"""

import hashlib
from typing import List, Optional
from ..database import get_db_connection
from ..models.usuario import Usuario


def hash_password(password: str) -> str:
    """Calcula el hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


class AuthService:
    @staticmethod
    def autenticar(nombre_usuario: str, password: str) -> Optional[Usuario]:
        """Verifica credenciales y retorna el usuario si es válido y está activo."""
        hashed = hash_password(password)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM usuarios 
                WHERE LOWER(nombre_usuario) = LOWER(?) AND activo = 1
                """,
                (nombre_usuario.strip(),),
            )
            row = cursor.fetchone()
            if row and row["password_hash"] == hashed:
                return Usuario.from_row(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(usuario_id: int) -> Optional[Usuario]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
            row = cursor.fetchone()
            return Usuario.from_row(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def listar_usuarios() -> List[Usuario]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios ORDER BY id ASC")
            return [Usuario.from_row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def crear_usuario(nombre_usuario: str, password: str, nombre_completo: str, rol: str) -> Usuario:
        if rol not in ("ADMINISTRADOR", "CAJERO"):
            raise ValueError("Rol inválido. Debe ser 'ADMINISTRADOR' o 'CAJERO'.")

        hashed = hash_password(password)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, rol, activo)
                VALUES (?, ?, ?, ?, 1)
                """,
                (nombre_usuario.strip().lower(), hashed, nombre_completo.strip(), rol),
            )
            conn.commit()
            new_id = cursor.lastrowid
            return AuthService.obtener_por_id(new_id)
        finally:
            conn.close()

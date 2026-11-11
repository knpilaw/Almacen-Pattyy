"""
Gestión de conexión a la base de datos para Minimarket Patty.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "minimarket.db")


def get_db_connection() -> sqlite3.Connection:
    """Retorna una conexión a SQLite con soporte de diccionario para filas y claves foráneas activas."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def dict_from_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Convierte un objeto sqlite3.Row a un diccionario estándar de Python."""
    if row is None:
        return None
    return dict(row)


def dict_list_from_rows(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Convierte una lista de sqlite3.Row a una lista de diccionarios."""
    return [dict(r) for r in rows]

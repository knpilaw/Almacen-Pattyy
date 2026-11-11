"""
Script de inicialización de la Base de Datos para Minimarket Patty.
Crea las tablas aplicando el esquema normalizado (3FN) y carga datos de prueba iniciales.
Usa SQLite por defecto (cero configuración y 100% offline).
"""

import os
import sqlite3
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "minimarket.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "seed_data.sql")


def hash_password(password: str) -> str:
    """Genera hash SHA-256 para contraseñas de usuarios."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def inicializar_bd(db_path: str = DB_PATH, cargar_seed: bool = True):
    print(f"[*] Inicializando base de datos en: {db_path}")

    # Si ya existe, podemos crear conexión
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Habilitar claves foráneas en SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Ejecutar esquema DDL
    print("[+] Creando tablas e índices...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # 2. Cargar datos semilla si no existen productos
    if cargar_seed:
        cursor.execute("SELECT COUNT(*) FROM productos")
        count = cursor.fetchone()[0]
        if count == 0:
            print("[+] Insertando datos iniciales (categorías, usuarios, catálogo)...")
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                seed_sql = f.read()
            cursor.executescript(seed_sql)
        else:
            print("[i] La base de datos ya contiene productos. Se omitió la carga semilla.")

    conn.commit()

    # Resumen de verificación
    cursor.execute("SELECT COUNT(*) FROM categorias")
    cat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM productos")
    prod_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    user_count = cursor.fetchone()[0]

    print("\n--- Verificación de Base de Datos ---")
    print(f"  Categorías cargadas: {cat_count}")
    print(f"  Productos cargados:  {prod_count}")
    print(f"  Usuarios registrados: {user_count}")
    print("-------------------------------------")
    print("Base de datos inicializada exitosamente.\n")

    conn.close()


if __name__ == "__main__":
    inicializar_bd()

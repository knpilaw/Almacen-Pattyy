"""
Punto de entrada principal para ejecutar Minimarket Patty
Ejecutar con: py run.py
"""

import os
import sys

# Asegurar que el directorio raíz esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.init_db import inicializar_bd, DB_PATH
from backend.app import create_app

if __name__ == "__main__":
    # Si la base de datos no existe aún, la inicializa automáticamente con datos de prueba
    if not os.path.exists(DB_PATH):
        print("[!] Base de datos no encontrada. Inicializando automáticamente...")
        inicializar_bd()

    app = create_app()
    print("=====================================================================")
    print("  SISTEMA DE CONTROL DE INVENTARIO Y POS - MINIMARKET PATTY         ")
    print("  Taller de Sistemas de Información - UTEM 2026                      ")
    print("  Servidor iniciado en: http://127.0.0.1:5000                        ")
    print("=====================================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)

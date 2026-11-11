"""
Pruebas de integración HTTP de las rutas Flask API
Ejecutar con: py tests/test_api_routes.py
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app


def run_api_tests():
    print(">>> PROBANDO ENDPOINTS HTTP FLASK API <<<\n")
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    # 1. Health check
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "online"
    print("  [✓] GET /api/health -> 200 OK")

    # 2. Login
    resp = client.post(
        "/api/auth/login",
        json={"nombre_usuario": "patricia", "password": "admin123"},
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["usuario"]["rol"] == "ADMINISTRADOR"
    print("  [✓] POST /api/auth/login -> 200 OK (Sesión creada)")

    # 3. Buscar producto por código de barras (POS pistola)
    resp = client.get("/api/productos/codigo/780223456701")
    assert resp.status_code == 200
    prod = json.loads(resp.data)
    assert "Coca-Cola" in prod["nombre"]
    print(f"  [✓] GET /api/productos/codigo/780223456701 -> 200 OK ({prod['nombre']})")

    # 4. Listar productos y categorías
    resp = client.get("/api/productos")
    assert resp.status_code == 200
    assert len(json.loads(resp.data)) >= 15
    print("  [✓] GET /api/productos -> 200 OK")

    resp = client.get("/api/productos/categorias")
    assert resp.status_code == 200
    assert len(json.loads(resp.data)) >= 5
    print("  [✓] GET /api/productos/categorias -> 200 OK")

    # 5. Dashboard resumen
    resp = client.get("/api/reportes/dashboard")
    assert resp.status_code == 200
    dash = json.loads(resp.data)
    assert "inventario" in dash and "ventas_hoy" in dash
    print("  [✓] GET /api/reportes/dashboard -> 200 OK")

    # 6. Reporte productos más vendidos
    resp = client.get("/api/reportes/mas-vendidos")
    assert resp.status_code == 200
    print("  [✓] GET /api/reportes/mas-vendidos -> 200 OK")

    print("\n=======================================================")
    print("  ¡TODOS LOS ENDPOINTS HTTP API FUNCIONAN CORRECTAMENTE!")
    print("=======================================================\n")


if __name__ == "__main__":
    run_api_tests()

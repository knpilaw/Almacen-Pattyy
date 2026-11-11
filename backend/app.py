"""
Aplicación Principal Flask para Minimarket Patty
Servidor local y offline para Punto de Venta e Inventario.
"""

import os
from flask import Flask, jsonify, send_from_directory
from .routes.auth_routes import auth_bp
from .routes.producto_routes import producto_bp
from .routes.venta_routes import venta_bp
from .routes.caja_routes import caja_bp
from .routes.inventario_routes import inventario_bp
from .routes.reporte_routes import reporte_bp

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path="",
    )

    # Configuración de sesión y seguridad
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "minimarket-patty-secret-key-2026")
    app.config["JSON_AS_ASCII"] = False

    # Registro de Blueprints API
    app.register_blueprint(auth_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(venta_bp)
    app.register_blueprint(caja_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(reporte_bp)

    # Estado de salud de la API
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "online",
            "sistema": "Control de Inventario y Ventas - Minimarket Patty",
            "offline_mode": True,
        }), 200

    # Servir la aplicación frontend SPA o vistas HTML estáticas
    @app.route("/")
    def index():
        if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
            return send_from_directory(FRONTEND_DIR, "index.html")
        return jsonify({
            "mensaje": "Backend de Minimarket Patty activo.",
            "api_docs": "Endpoints disponibles bajo /api/",
        })

    @app.route("/<path:path>")
    def static_proxy(path):
        file_path = os.path.join(FRONTEND_DIR, path)
        if os.path.exists(file_path):
            return send_from_directory(FRONTEND_DIR, path)
        # Redirección amigable a index si no existe archivo específico
        if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
            return send_from_directory(FRONTEND_DIR, "index.html")
        return jsonify({"error": "Recurso no encontrado"}), 404

    return app


if __name__ == "__main__":
    app = create_app()
    print("=======================================================")
    print("  MINIMARKET PATTY - SISTEMA DE INVENTARIO Y POS       ")
    print("  Ejecutándose en modo local: http://127.0.0.1:5000    ")
    print("=======================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)

"""
Rutas de Autenticación y Sesión
"""

from flask import Blueprint, jsonify, request, session
from ..services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    nombre_usuario = data.get("nombre_usuario", "")
    password = data.get("password", "")

    if not nombre_usuario or not password:
        return jsonify({"error": "Debe ingresar usuario y contraseña."}), 400

    usuario = AuthService.autenticar(nombre_usuario, password)
    if not usuario:
        return jsonify({"error": "Credenciales inválidas o usuario inactivo."}), 401

    session["usuario_id"] = usuario.id
    session["rol"] = usuario.rol
    session["nombre_completo"] = usuario.nombre_completo

    return jsonify({
        "mensaje": "Inicio de sesión exitoso.",
        "usuario": usuario.to_dict(),
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada correctamente."}), 200


@auth_bp.route("/perfil", methods=["GET"])
def perfil():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "No hay sesión activa."}), 401

    usuario = AuthService.obtener_por_id(usuario_id)
    if not usuario:
        session.clear()
        return jsonify({"error": "Usuario no encontrado."}), 404

    return jsonify({"usuario": usuario.to_dict()}), 200

"""
Rutas para auditoría y ajustes de inventario
"""

from flask import Blueprint, jsonify, request, session
from ..services.inventario_service import InventarioService

inventario_bp = Blueprint("inventario", __name__, url_prefix="/api/inventario")


@inventario_bp.route("/ajuste", methods=["POST"])
def registrar_ajuste():
    data = request.get_json(silent=True) or {}
    producto_id = data.get("producto_id")
    tipo_movimiento = data.get("tipo_movimiento")
    cantidad = data.get("cantidad")
    motivo = data.get("motivo", "")

    usuario_id = session.get("usuario_id") or int(data.get("usuario_id", 1))

    if not producto_id or not tipo_movimiento or cantidad is None:
        return jsonify({"error": "Faltan campos obligatorios (producto_id, tipo_movimiento, cantidad)."}), 400

    try:
        mov = InventarioService.registrar_ajuste(
            producto_id=int(producto_id),
            usuario_id=usuario_id,
            tipo_movimiento=tipo_movimiento.upper(),
            cantidad=int(cantidad),
            motivo=motivo,
        )
        return jsonify({
            "mensaje": "Ajuste de inventario registrado correctamente.",
            "movimiento": mov.to_dict(),
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@inventario_bp.route("/movimientos", methods=["GET"])
def listar_movimientos():
    prod_id = request.args.get("producto_id", type=int)
    limite = request.args.get("limite", default=100, type=int)
    movs = InventarioService.listar_movimientos(producto_id=prod_id, limit=limite)
    return jsonify([m.to_dict() for m in movs]), 200

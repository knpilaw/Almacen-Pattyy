"""
Rutas para transacciones de venta en el POS
"""

from flask import Blueprint, jsonify, request, session
from ..services.venta_service import VentaService

venta_bp = Blueprint("ventas", __name__, url_prefix="/api/ventas")


@venta_bp.route("", methods=["POST"])
def registrar_venta():
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])
    metodo_pago = data.get("metodo_pago", "EFECTIVO").upper()
    monto_pagado = int(data.get("monto_pagado", 0))

    # Identificar cajero/usuario (usa sesión o ID enviado o por defecto el usuario 1)
    usuario_id = session.get("usuario_id") or int(data.get("usuario_id", 1))

    if not items:
        return jsonify({"error": "Debe agregar al menos un producto a la venta."}), 400

    try:
        venta = VentaService.procesar_venta(
            usuario_id=usuario_id,
            items=items,
            metodo_pago=metodo_pago,
            monto_pagado=monto_pagado,
        )
        return jsonify({
            "mensaje": "Venta procesada exitosamente.",
            "venta": venta.to_dict(),
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error inesperado al registrar venta: {str(e)}"}), 500


@venta_bp.route("", methods=["GET"])
def listar_ventas():
    limite = request.args.get("limite", default=50, type=int)
    ventas = VentaService.listar_recientes(limit=limite)
    return jsonify([v.to_dict() for v in ventas]), 200


@venta_bp.route("/<int:venta_id>", methods=["GET"])
def obtener_venta(venta_id):
    venta = VentaService.obtener_por_id(venta_id)
    if not venta:
        return jsonify({"error": "Venta no encontrada."}), 404
    return jsonify(venta.to_dict()), 200

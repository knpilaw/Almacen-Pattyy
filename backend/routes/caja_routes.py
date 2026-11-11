"""
Rutas para la gestión de turnos y Cierre de Caja
"""

from flask import Blueprint, jsonify, request, session
from ..services.caja_service import CajaService

caja_bp = Blueprint("caja", __name__, url_prefix="/api/caja")


@caja_bp.route("/activa", methods=["GET"])
def obtener_caja_activa():
    usuario_id = session.get("usuario_id")
    caja = CajaService.obtener_caja_activa(usuario_id=usuario_id)
    if not caja:
        return jsonify({"mensaje": "No hay ningún turno de caja abierto actualmente.", "abierta": False}), 200
    res = caja.to_dict()
    res["abierta"] = True
    return jsonify(res), 200


@caja_bp.route("/abrir", methods=["POST"])
def abrir_caja():
    data = request.get_json(silent=True) or {}
    usuario_id = session.get("usuario_id") or int(data.get("usuario_id", 1))
    monto_inicial = int(data.get("monto_inicial", 0))

    try:
        caja = CajaService.abrir_caja(usuario_id, monto_inicial)
        return jsonify({"mensaje": "Turno de caja abierto.", "caja": caja.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@caja_bp.route("/cerrar", methods=["POST"])
def cerrar_caja():
    data = request.get_json(silent=True) or {}
    cierre_id = data.get("cierre_id")
    total_declarado = int(data.get("total_declarado", 0))
    observaciones = data.get("observaciones", "")

    if not cierre_id:
        # Si no mandan ID, buscar la caja activa actual
        usuario_id = session.get("usuario_id")
        activa = CajaService.obtener_caja_activa(usuario_id)
        if not activa:
            return jsonify({"error": "No existe una caja abierta para cerrar."}), 400
        cierre_id = activa.id

    try:
        caja_cerrada = CajaService.cerrar_caja(int(cierre_id), total_declarado, observaciones)
        return jsonify({
            "mensaje": "Caja cerrada exitosamente. Cierre de jornada completado.",
            "cierre": caja_cerrada.to_dict(),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@caja_bp.route("/historial", methods=["GET"])
def listar_historial():
    limite = request.args.get("limite", default=30, type=int)
    cierres = CajaService.listar_cierres(limit=limite)
    return jsonify([c.to_dict() for c in cierres]), 200

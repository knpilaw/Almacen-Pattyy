"""
Rutas para consultas gerenciales y reportes de Minimarket Patty
"""

from flask import Blueprint, jsonify, request
from ..services.reporte_service import ReporteService

reporte_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")


@reporte_bp.route("/dashboard", methods=["GET"])
def dashboard():
    resumen = ReporteService.resumen_dashboard()
    return jsonify(resumen), 200


@reporte_bp.route("/mas-vendidos", methods=["GET"])
def mas_vendidos():
    limite = request.args.get("limite", default=10, type=int)
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    datos = ReporteService.reporte_mas_vendidos(
        limite=limite,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    return jsonify(datos), 200


@reporte_bp.route("/diario", methods=["GET"])
def reporte_diario():
    fecha = request.args.get("fecha")
    datos = ReporteService.reporte_diario(fecha)
    return jsonify(datos), 200

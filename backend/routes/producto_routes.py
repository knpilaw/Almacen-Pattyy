"""
Rutas para la gestión del catálogo de productos y categorías
"""

from flask import Blueprint, jsonify, request
from ..services.producto_service import ProductoService

producto_bp = Blueprint("productos", __name__, url_prefix="/api/productos")


@producto_bp.route("", methods=["GET"])
def listar_productos():
    categoria_id = request.args.get("categoria_id", type=int)
    busqueda = request.args.get("busqueda", type=str)
    solo_activos = request.args.get("activos", default="true").lower() == "true"

    prods = ProductoService.listar_todos(
        solo_activos=solo_activos,
        categoria_id=categoria_id,
        busqueda=busqueda,
    )
    return jsonify([p.to_dict() for p in prods]), 200


@producto_bp.route("/codigo/<codigo_barra>", methods=["GET"])
def buscar_por_codigo(codigo_barra):
    """Endpoint de alta velocidad para el lector de código de barras en el POS."""
    prod = ProductoService.buscar_por_codigo(codigo_barra)
    if not prod:
        return jsonify({"error": f"Producto con código '{codigo_barra}' no encontrado."}), 404
    return jsonify(prod.to_dict()), 200


@producto_bp.route("/bajo-stock", methods=["GET"])
def productos_bajo_stock():
    prods = ProductoService.listar_bajo_stock()
    return jsonify([p.to_dict() for p in prods]), 200


@producto_bp.route("/<int:producto_id>", methods=["GET"])
def obtener_producto(producto_id):
    prod = ProductoService.obtener_por_id(producto_id)
    if not prod:
        return jsonify({"error": "Producto no encontrado."}), 404
    return jsonify(prod.to_dict()), 200


@producto_bp.route("", methods=["POST"])
def crear_producto():
    data = request.get_json(silent=True) or {}
    campos_requeridos = ("codigo_barra", "nombre", "categoria_id", "precio_costo", "precio_venta")
    for c in campos_requeridos:
        if c not in data or str(data[c]).strip() == "":
            return jsonify({"error": f"El campo '{c}' es obligatorio."}), 400

    try:
        nuevo = ProductoService.crear_producto(data)
        return jsonify({"mensaje": "Producto creado exitosamente.", "producto": nuevo.to_dict()}), 210
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@producto_bp.route("/<int:producto_id>", methods=["PUT"])
def actualizar_producto(producto_id):
    data = request.get_json(silent=True) or {}
    try:
        actualizado = ProductoService.actualizar_producto(producto_id, data)
        if not actualizado:
            return jsonify({"error": "Producto no encontrado."}), 404
        return jsonify({"mensaje": "Producto actualizado.", "producto": actualizado.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@producto_bp.route("/<int:producto_id>", methods=["DELETE"])
def desactivar_producto(producto_id):
    ok = ProductoService.cambiar_estado(producto_id, activo=False)
    if not ok:
        return jsonify({"error": "Producto no encontrado."}), 404
    return jsonify({"mensaje": "Producto desactivado del catálogo."}), 200


# Rutas para categorías
@producto_bp.route("/categorias", methods=["GET"])
def listar_categorias():
    cats = ProductoService.listar_categorias()
    return jsonify([c.to_dict() for c in cats]), 200


@producto_bp.route("/categorias", methods=["POST"])
def crear_categoria():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"error": "El nombre de la categoría es obligatorio."}), 400

    try:
        cat = ProductoService.crear_categoria(nombre, data.get("descripcion"))
        return jsonify({"mensaje": "Categoría creada.", "categoria": cat.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

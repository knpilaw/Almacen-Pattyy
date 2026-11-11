"""
Servicio para gestión de Catálogo, Productos y Categorías
"""

from typing import Any, Dict, List, Optional
from ..database import get_db_connection
from ..models.producto import Categoria, Producto


class ProductoService:
    @staticmethod
    def buscar_por_codigo(codigo_barra: str) -> Optional[Producto]:
        """Búsqueda de producto por código de barras (optimizado para lector USB)."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, c.nombre AS categoria_nombre 
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE p.codigo_barra = ? AND p.activo = 1
                LIMIT 1
                """,
                (codigo_barra.strip(),),
            )
            row = cursor.fetchone()
            return Producto.from_row(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(producto_id: int) -> Optional[Producto]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, c.nombre AS categoria_nombre 
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE p.id = ?
                """,
                (producto_id,),
            )
            row = cursor.fetchone()
            return Producto.from_row(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def listar_todos(solo_activos: bool = True, categoria_id: Optional[int] = None, busqueda: Optional[str] = None) -> List[Producto]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.*, c.nombre AS categoria_nombre 
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE 1=1
            """
            params: List[Any] = []

            if solo_activos:
                query += " AND p.activo = 1"

            if categoria_id:
                query += " AND p.categoria_id = ?"
                params.append(categoria_id)

            if busqueda:
                termino = f"%{busqueda.strip()}%"
                query += " AND (p.nombre LIKE ? OR p.codigo_barra LIKE ?)"
                params.extend([termino, termino])

            query += " ORDER BY p.nombre ASC"
            cursor.execute(query, tuple(params))
            return [Producto.from_row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def listar_bajo_stock() -> List[Producto]:
        """Obtiene productos cuyo stock actual es menor o igual al stock mínimo de reposición."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, c.nombre AS categoria_nombre 
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE p.activo = 1 AND p.stock_actual <= p.stock_minimo
                ORDER BY p.stock_actual ASC
                """
            )
            return [Producto.from_row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def crear_producto(datos: Dict[str, Any]) -> Producto:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO productos (
                    codigo_barra, nombre, descripcion, categoria_id,
                    precio_costo, precio_venta, stock_actual, stock_minimo,
                    unidad_medida, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    datos["codigo_barra"].strip(),
                    datos["nombre"].strip(),
                    datos.get("descripcion", "").strip(),
                    int(datos["categoria_id"]),
                    int(datos["precio_costo"]),
                    int(datos["precio_venta"]),
                    int(datos.get("stock_actual", 0)),
                    int(datos.get("stock_minimo", 5)),
                    datos.get("unidad_medida", "UNIDAD"),
                ),
            )
            nuevo_id = cursor.lastrowid
            conn.commit()
            return ProductoService.obtener_por_id(nuevo_id)
        finally:
            conn.close()

    @staticmethod
    def actualizar_producto(producto_id: int, datos: Dict[str, Any]) -> Optional[Producto]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE productos SET
                    codigo_barra = ?,
                    nombre = ?,
                    descripcion = ?,
                    categoria_id = ?,
                    precio_costo = ?,
                    precio_venta = ?,
                    stock_minimo = ?,
                    unidad_medida = ?,
                    actualizado_en = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    datos["codigo_barra"].strip(),
                    datos["nombre"].strip(),
                    datos.get("descripcion", "").strip(),
                    int(datos["categoria_id"]),
                    int(datos["precio_costo"]),
                    int(datos["precio_venta"]),
                    int(datos.get("stock_minimo", 5)),
                    datos.get("unidad_medida", "UNIDAD"),
                    producto_id,
                ),
            )
            conn.commit()
            return ProductoService.obtener_por_id(producto_id)
        finally:
            conn.close()

    @staticmethod
    def cambiar_estado(producto_id: int, activo: bool) -> bool:
        """Desactiva o reactiva un producto sin borrarlo físicamente."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET activo = ? WHERE id = ?", (1 if activo else 0, producto_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def listar_categorias() -> List[Categoria]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias ORDER BY nombre ASC")
            return [Categoria.from_row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def crear_categoria(nombre: str, descripcion: Optional[str] = None) -> Categoria:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)", (nombre.strip(), descripcion))
            conn.commit()
            nuevo_id = cursor.lastrowid
            cursor.execute("SELECT * FROM categorias WHERE id = ?", (nuevo_id,))
            return Categoria.from_row(cursor.fetchone())
        finally:
            conn.close()

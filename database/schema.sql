-- =============================================================================
-- PROYECTO: Sistema de Control de Inventario y Ventas para Minimarket Patty
-- ASIGNATURA: Taller de Sistemas de Información - UTEM 2026
-- MODELO DE BASE DE DATOS RELACIONAL NORMALIZADO (3FN)
-- =============================================================================

-- Desactivar temporalmente restricciones de claves foráneas para recreación limpia
PRAGMA foreign_keys = ON;

-- 1. TABLA: usuarios
-- Almacena credenciales y roles (Administrador vs Cajero)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK(rol IN ('ADMINISTRADOR', 'CAJERO')),
    activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1)),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: categorias
-- Clasificación de los productos del minimarket (Abarrotes, Aseo, Cecinas, etc.)
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(60) NOT NULL UNIQUE,
    descripcion TEXT
);

-- 3. TABLA: productos
-- Catálogo general con costos, precios de venta, código de barras y stock
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_barra VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(120) NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER NOT NULL,
    precio_costo INTEGER NOT NULL CHECK(precio_costo >= 0),
    precio_venta INTEGER NOT NULL CHECK(precio_venta >= 0),
    stock_actual INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 5,
    unidad_medida VARCHAR(20) NOT NULL DEFAULT 'UNIDAD',
    activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1)),
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 4. TABLA: cierres_caja
-- Registro de apertura y cierre de caja diario por cajero
CREATE TABLE IF NOT EXISTS cierres_caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TIMESTAMP NULL,
    monto_inicial INTEGER NOT NULL DEFAULT 0 CHECK(monto_inicial >= 0),
    total_ventas_efectivo INTEGER NOT NULL DEFAULT 0,
    total_ventas_mercado_pago INTEGER NOT NULL DEFAULT 0,
    total_ventas_transferencia INTEGER NOT NULL DEFAULT 0,
    total_esperado INTEGER NOT NULL DEFAULT 0,
    total_declarado INTEGER NOT NULL DEFAULT 0,
    diferencia INTEGER NOT NULL DEFAULT 0,
    observaciones TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'ABIERTA' CHECK(estado IN ('ABIERTA', 'CERRADA')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 5. TABLA: ventas
-- Encabezado de la transacción comercial efectuada en el POS
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_boleta VARCHAR(30) NOT NULL UNIQUE,
    usuario_id INTEGER NOT NULL,
    cierre_caja_id INTEGER NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total INTEGER NOT NULL CHECK(total >= 0),
    metodo_pago VARCHAR(30) NOT NULL DEFAULT 'EFECTIVO' CHECK(metodo_pago IN ('EFECTIVO', 'MERCADO_PAGO', 'TRANSFERENCIA')),
    monto_pagado INTEGER NOT NULL DEFAULT 0,
    vuelto INTEGER NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'COMPLETADA' CHECK(estado IN ('COMPLETADA', 'ANULADA')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (cierre_caja_id) REFERENCES cierres_caja(id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- 6. TABLA: detalle_ventas
-- Línea de detalle de productos vendidos (conserva precio y costo histórico al vender)
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    precio_unitario INTEGER NOT NULL CHECK(precio_unitario >= 0),
    costo_unitario INTEGER NOT NULL CHECK(costo_unitario >= 0),
    subtotal INTEGER NOT NULL CHECK(subtotal >= 0),
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 7. TABLA: movimientos_inventario
-- Bitácora de auditoría para entradas de mercadería y ajustes por merma o error
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    tipo_movimiento VARCHAR(30) NOT NULL CHECK(tipo_movimiento IN ('ENTRADA_COMPRA', 'VENTA', 'AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO', 'MERMA_VENCIMIENTO')),
    cantidad INTEGER NOT NULL,
    stock_anterior INTEGER NOT NULL,
    stock_nuevo INTEGER NOT NULL,
    motivo TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- =============================================================================
-- ÍNDICES PARA ALTA VELOCIDAD EN EL PUNTO DE VENTA (BÚSQUEDA POR CÓDIGO DE BARRAS)
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_productos_codigo_barra ON productos(codigo_barra);
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_detalle_ventas_producto ON detalle_ventas(producto_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON movimientos_inventario(producto_id);

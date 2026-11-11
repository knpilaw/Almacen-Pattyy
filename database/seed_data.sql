-- =============================================================================
-- DATOS INICIALES (SEED DATA) PARA MINIMARKET PATTY
-- =============================================================================

-- 1. Categorías iniciales
INSERT INTO categorias (nombre, descripcion) VALUES
('Abarrotes', 'Arroz, fideos, aceites, salsas, conservas y legumbres'),
('Bebidas y Aguas', 'Bebidas gaseosas, aguas minerales, jugos y energéticas'),
('Cecinas y Lácteos', 'Quesos, jamones, salchichas, leches, yogures y mantequillas'),
('Panadería y Snacks', 'Pan fresco, galletas, papas fritas y snacks envasados'),
('Aseo y Limpieza', 'Detergentes, cloro, lavalozas, papel higiénico y toallas');

-- 2. Usuarios por defecto (Contraseña temporal: 'admin123' y 'cajero123')
-- Se almacenan hashes seguros SHA-256
-- admin123: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- cajero123: 1ed4353e845e2e537e017c0fac3a0d402d231809b7989e90da15191c1148a93f
INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, rol, activo) VALUES
('patricia', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Patricia Painén (Dueña)', 'ADMINISTRADOR', 1),
('cajero', '1ed4353e845e2e537e017c0fac3a0d402d231809b7989e90da15191c1148a93f', 'Cajero Turno', 'CAJERO', 1);

-- 3. Catálogo inicial de productos frecuentes en el almacén
-- Precios expresados en Pesos Chilenos (CLP)
INSERT INTO productos (codigo_barra, nombre, descripcion, categoria_id, precio_costo, precio_venta, stock_actual, stock_minimo, unidad_medida) VALUES
('780123456701', 'Arroz Grado 1 1kg Tucapel', 'Bolsa de arroz selección grano largo', 1, 1100, 1600, 24, 6, 'UNIDAD'),
('780123456702', 'Aceite Vegetal 900ml Belmont', 'Botella de aceite 100% vegetal', 1, 1450, 2100, 18, 5, 'UNIDAD'),
('780123456703', 'Fideos Spaghetti Nº5 400g Lucchetti', 'Pasta tradicional de sémola', 1, 650, 1050, 30, 8, 'UNIDAD'),
('780123456704', 'Salsa de Tomate Italiana 200g Carozzi', 'Sachet salsa tradicional', 1, 420, 700, 40, 10, 'UNIDAD'),
('780223456701', 'Coca-Cola Original 1.5L Desechable', 'Bebida de fantasía con gas', 2, 1300, 1900, 20, 6, 'UNIDAD'),
('780223456702', 'Bebida Sprite 1.5L Desechable', 'Bebida sabor lima limón', 2, 1300, 1900, 14, 5, 'UNIDAD'),
('780223456703', 'Agua Mineral Benedictino sin gas 1.6L', 'Agua purificada de vertiente', 2, 700, 1200, 16, 4, 'UNIDAD'),
('780323456701', 'Leche Entera Colun 1L Tetra', 'Leche natural UHT larga vida', 3, 850, 1250, 25, 8, 'UNIDAD'),
('780323456702', 'Vienesas Tradicionales 5 un San Jorge', 'Paquete salchichas tipo vienesa', 3, 1150, 1750, 12, 4, 'UNIDAD'),
('780323456703', 'Queso Gauda Trozo 250g Colun', 'Queso laminable mantecoso', 3, 1950, 2800, 10, 3, 'UNIDAD'),
('780423456701', 'Papas Fritas Lays Clásicas 180g', 'Bolsa tamaño para compartir', 4, 1400, 2100, 15, 5, 'UNIDAD'),
('780423456702', 'Galletas Tritón Vainilla 126g McKay', 'Galleta rellena con crema de vainilla', 4, 600, 950, 28, 6, 'UNIDAD'),
('780523456701', 'Cloro Tradicional 1L Clorinda', 'Desinfectante líquido concentrado', 5, 800, 1300, 16, 4, 'UNIDAD'),
('780523456702', 'Lavalozas Quix Limón 750ml', 'Detergente líquido desengrasante', 5, 1350, 2100, 12, 4, 'UNIDAD'),
('780523456703', 'Papel Higiénico Scott Doble Hoja 4un', 'Pack 4 rollos de 30 metros', 5, 1200, 1850, 20, 6, 'UNIDAD');

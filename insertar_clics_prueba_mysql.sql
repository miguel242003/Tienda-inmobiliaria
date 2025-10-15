-- ========================================
-- SCRIPT PARA INSERTAR CLICS DE PRUEBA EN MYSQL
-- ========================================

-- Usar la base de datos correcta
USE tienda_inmobiliaria_prod;

-- Limpiar clics existentes (opcional)
-- DELETE FROM propiedades_clickpropiedad;

-- Insertar clics para propiedad 18 (Casa de ciudadasdsa)
INSERT INTO propiedades_clickpropiedad (propiedad_id, fecha_click, ip_address, user_agent, pagina_origen) VALUES
(18, '2025-10-15 10:00:00', '192.168.1.100', 'Mozilla/5.0 Test Browser', 'home'),
(18, '2025-10-15 11:00:00', '192.168.1.101', 'Mozilla/5.0 Test Browser', 'home'),
(18, '2025-10-15 12:00:00', '192.168.1.102', 'Mozilla/5.0 Test Browser', 'home'),
(18, '2025-10-15 13:00:00', '192.168.1.103', 'Mozilla/5.0 Test Browser', 'home'),
(18, '2025-10-15 14:00:00', '192.168.1.104', 'Mozilla/5.0 Test Browser', 'home');

-- Insertar clics para propiedad 19 (casa de campo)
INSERT INTO propiedades_clickpropiedad (propiedad_id, fecha_click, ip_address, user_agent, pagina_origen) VALUES
(19, '2025-10-15 10:30:00', '192.168.1.105', 'Mozilla/5.0 Test Browser', 'home'),
(19, '2025-10-15 11:30:00', '192.168.1.106', 'Mozilla/5.0 Test Browser', 'home'),
(19, '2025-10-15 12:30:00', '192.168.1.107', 'Mozilla/5.0 Test Browser', 'home'),
(19, '2025-10-15 13:30:00', '192.168.1.108', 'Mozilla/5.0 Test Browser', 'home');

-- Insertar clics para propiedad 20 (Casa de valparaiso)
INSERT INTO propiedades_clickpropiedad (propiedad_id, fecha_click, ip_address, user_agent, pagina_origen) VALUES
(20, '2025-10-15 10:45:00', '192.168.1.109', 'Mozilla/5.0 Test Browser', 'home'),
(20, '2025-10-15 11:45:00', '192.168.1.110', 'Mozilla/5.0 Test Browser', 'home'),
(20, '2025-10-15 12:45:00', '192.168.1.111', 'Mozilla/5.0 Test Browser', 'home');

-- Verificar que se insertaron los clics
SELECT 
    p.id,
    p.titulo,
    COUNT(cp.id) as total_clicks
FROM propiedades_propiedad p
LEFT JOIN propiedades_clickpropiedad cp ON p.id = cp.propiedad_id
GROUP BY p.id, p.titulo
ORDER BY total_clicks DESC;

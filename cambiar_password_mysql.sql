-- =====================================================
-- Script para cambiar la contraseña del usuario MySQL
-- =====================================================

-- Cambiar la contraseña del usuario tienda_user
-- IMPORTANTE: Reemplaza 'NuevaContraseña123!' con tu contraseña deseada
ALTER USER 'tienda_user'@'localhost' IDENTIFIED BY 'MAS242003';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar que el usuario existe
SELECT User, Host FROM mysql.user WHERE User = 'tienda_user';


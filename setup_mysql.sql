-- =====================================================
-- Script de Configuración de Base de Datos MySQL
-- Para Tienda Inmobiliaria - Producción
-- =====================================================

-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS tienda_inmobiliaria_prod
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 2. Crear usuario con permisos limitados (solo para esta base de datos)
-- IMPORTANTE: Cambia 'tu_contraseña_segura' por una contraseña fuerte
CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';

-- 3. Otorgar permisos específicos (no superusuario)
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, 
      REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE
ON tienda_inmobiliaria_prod.* 
TO 'tienda_user'@'localhost';

-- 4. Aplicar cambios
FLUSH PRIVILEGES;

-- 5. Verificar que todo está correcto
SELECT User, Host FROM mysql.user WHERE User = 'tienda_user';
SHOW DATABASES LIKE 'tienda_inmobiliaria_prod';

-- =====================================================
-- Notas de Seguridad:
-- - El usuario 'tienda_user' solo tiene permisos en la base de datos específica
-- - NO tiene permisos de superusuario (SUPER, GRANT OPTION, etc.)
-- - Usa una contraseña fuerte con letras, números y símbolos
-- =====================================================


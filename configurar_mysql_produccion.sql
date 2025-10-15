-- ========================================
-- SCRIPT PARA CONFIGURAR MYSQL EN PRODUCCIÓN
-- ========================================

-- 1. Crear usuario MySQL
CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'M@s_242003!';

-- 2. Crear base de datos
CREATE DATABASE IF NOT EXISTS tienda_inmobiliaria_prod 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 3. Otorgar permisos
GRANT ALL PRIVILEGES ON tienda_inmobiliaria_prod.* TO 'tienda_user'@'localhost';

-- 4. Aplicar cambios
FLUSH PRIVILEGES;

-- 5. Verificar usuario creado
SELECT User, Host FROM mysql.user WHERE User = 'tienda_user';

-- 6. Verificar base de datos
SHOW DATABASES LIKE 'tienda_inmobiliaria_prod';

-- 7. Usar la base de datos
USE tienda_inmobiliaria_prod;

-- 8. Verificar tablas existentes
SHOW TABLES;

-- Script para configurar MySQL para el tracking de clics
-- Ejecutar como root en MySQL

-- Crear usuario para la aplicación
CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'M@s_242003!';

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS tienda_inmobiliaria_prod 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Otorgar permisos al usuario
GRANT ALL PRIVILEGES ON tienda_inmobiliaria_prod.* TO 'tienda_user'@'localhost';

-- Aplicar los cambios
FLUSH PRIVILEGES;

-- Verificar que el usuario fue creado
SELECT User, Host FROM mysql.user WHERE User = 'tienda_user';

-- Verificar que la base de datos fue creada
SHOW DATABASES LIKE 'tienda_inmobiliaria_prod';

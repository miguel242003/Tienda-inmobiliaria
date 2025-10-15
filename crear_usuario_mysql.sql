-- Crear usuario tienda_user para la aplicación
CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'M@s_242003!';

-- Otorgar todos los permisos sobre la base de datos
GRANT ALL PRIVILEGES ON tienda_inmobiliaria_prod.* TO 'tienda_user'@'localhost';

-- Aplicar los cambios
FLUSH PRIVILEGES;

-- Verificar que el usuario fue creado
SELECT User, Host FROM mysql.user WHERE User = 'tienda_user';

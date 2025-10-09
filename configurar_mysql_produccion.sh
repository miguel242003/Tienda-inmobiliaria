#!/bin/bash

# ============================================================================
# SCRIPT PARA CONFIGURAR MYSQL EN PRODUCCIÓN
# ============================================================================

echo "🔧 Configurando MySQL para producción..."

# 1. Copiar archivo de configuración
echo "📋 Copiando configuración de producción..."
cp config_produccion.env .env

# 2. Instalar dependencias de MySQL
echo "📦 Instalando dependencias de MySQL..."
pip install pymysql mysqlclient

# 3. Crear base de datos MySQL
echo "🗄️ Creando base de datos MySQL..."
mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS tienda_inmobiliaria_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'tu_password_mysql_aqui';
GRANT ALL PRIVILEGES ON tienda_inmobiliaria_prod.* TO 'tienda_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# 4. Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
echo "👤 Creando superusuario..."
python manage.py createsuperuser

# 6. Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Configuración de MySQL completada!"
echo "🔗 Ahora puedes acceder a tu aplicación con MySQL en producción."

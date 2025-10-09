# ============================================================================
# SCRIPT PARA CONFIGURAR MYSQL EN PRODUCCIÓN (Windows PowerShell)
# ============================================================================

Write-Host "🔧 Configurando MySQL para producción..." -ForegroundColor Green

# 1. Copiar archivo de configuración
Write-Host "📋 Copiando configuración de producción..." -ForegroundColor Yellow
Copy-Item config_produccion.env .env

# 2. Instalar dependencias de MySQL
Write-Host "📦 Instalando dependencias de MySQL..." -ForegroundColor Yellow
pip install pymysql mysqlclient

# 3. Crear base de datos MySQL (requiere MySQL instalado)
Write-Host "🗄️ Creando base de datos MySQL..." -ForegroundColor Yellow
Write-Host "⚠️  IMPORTANTE: Asegúrate de tener MySQL instalado y ejecutar estos comandos manualmente:" -ForegroundColor Red
Write-Host ""
Write-Host "CREATE DATABASE IF NOT EXISTS tienda_inmobiliaria_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" -ForegroundColor Cyan
Write-Host "CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'tu_password_mysql_aqui';" -ForegroundColor Cyan
Write-Host "GRANT ALL PRIVILEGES ON tienda_inmobiliaria_prod.* TO 'tienda_user'@'localhost';" -ForegroundColor Cyan
Write-Host "FLUSH PRIVILEGES;" -ForegroundColor Cyan
Write-Host ""

# 4. Ejecutar migraciones
Write-Host "🔄 Ejecutando migraciones..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
Write-Host "👤 Creando superusuario..." -ForegroundColor Yellow
python manage.py createsuperuser

# 6. Recopilar archivos estáticos
Write-Host "📁 Recopilando archivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

Write-Host "✅ Configuración de MySQL completada!" -ForegroundColor Green
Write-Host "🔗 Ahora puedes acceder a tu aplicación con MySQL en producción." -ForegroundColor Green

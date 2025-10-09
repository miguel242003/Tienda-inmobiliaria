#!/bin/bash

# ============================================================================
# SCRIPT DE CONFIGURACIÓN PARA PRODUCCIÓN
# ============================================================================

echo "🚀 Configurando aplicación para producción..."

# 1. Crear archivo .env
echo "📝 Creando archivo .env..."
cp config_produccion.env .env
echo "✅ Archivo .env creado. Recuerda completar los valores reales."

# 2. Instalar dependencias de producción
echo "📦 Instalando dependencias de producción..."
pip install gunicorn
pip install redis
pip install django-redis

# 3. Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# 4. Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate

# 5. Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# 6. Verificar configuración
echo "🔍 Verificando configuración..."
python manage.py check --deploy

echo "✅ Configuración completada!"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Edita el archivo .env con tus datos reales"
echo "2. Configura MySQL con los datos del .env"
echo "3. Instala y configura Nginx"
echo "4. Ejecuta: gunicorn tienda_meli.wsgi:application --bind 0.0.0.0:8000"
echo ""
echo "🔧 Para configurar Nginx, usa el archivo: nginx_config_actualizada.conf"

#!/bin/bash

echo "🔍 REVISIÓN COMPLETA DEL SISTEMA"
echo "================================="

cd /home/deploy/Tienda-inmobiliaria
source venv/bin/activate

echo ""
echo "📊 1. VERIFICANDO ESTADO DEL SISTEMA"
echo "-----------------------------------"
python manage.py check

echo ""
echo "🗄️ 2. VERIFICANDO MIGRACIONES"
echo "-----------------------------"
python manage.py showmigrations

echo ""
echo "📁 3. VERIFICANDO ARCHIVOS DE MEDIA"
echo "-----------------------------------"
echo "Propiedades:"
ls -la /home/deploy/Tienda-inmobiliaria/media/propiedades/
echo ""
echo "CVs:"
ls -la /home/deploy/Tienda-inmobiliaria/media/cvs/
echo ""
echo "Admin profiles:"
ls -la /home/deploy/Tienda-inmobiliaria/media/admin_profiles/

echo ""
echo "🔗 4. VERIFICANDO URLs AMIGABLES"
echo "--------------------------------"
python manage.py shell << 'EOF'
from propiedades.models import Propiedad
print(f"Total propiedades: {Propiedad.objects.count()}")
for prop in Propiedad.objects.all()[:5]:  # Mostrar solo las primeras 5
    print(f"ID: {prop.id}, Título: {prop.titulo}, Slug: {prop.slug}")
EOF

echo ""
echo "📧 5. VERIFICANDO CVs"
echo "---------------------"
python manage.py shell << 'EOF'
from core.models import CVSubmission
print(f"Total CVs: {CVSubmission.objects.count()}")
for cv in CVSubmission.objects.all()[:3]:  # Mostrar solo los primeros 3
    print(f"ID: {cv.id}, Nombre: {cv.nombre}, Archivo: {cv.cv_file}")
EOF

echo ""
echo "🌐 6. VERIFICANDO SERVICIOS"
echo "---------------------------"
echo "Gunicorn:"
sudo supervisorctl status tienda_inmobiliaria
echo ""
echo "Nginx:"
sudo systemctl status nginx --no-pager -l

echo ""
echo "📈 7. VERIFICANDO LOGS RECIENTES"
echo "-------------------------------"
echo "Logs de Django (últimas 10 líneas):"
tail -10 /home/deploy/Tienda-inmobiliaria/logs/django.log
echo ""
echo "Logs de Gunicorn (últimas 5 líneas):"
tail -5 /home/deploy/Tienda-inmobiliaria/logs/gunicorn.log

echo ""
echo "✅ REVISIÓN COMPLETADA"
echo "====================="
echo "Sistema verificado exitosamente"

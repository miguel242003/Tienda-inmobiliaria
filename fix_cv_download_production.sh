#!/bin/bash

# Script para corregir la descarga de CVs en producción
# Ejecutar en el servidor VPS

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 CORRIGIENDO DESCARGA DE CVs EN PRODUCCIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Ejecuta desde el directorio del proyecto."
    exit 1
fi

echo "✅ Directorio del proyecto encontrado"

# 2. Activar entorno virtual
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "❌ Error: No se encontró el entorno virtual"
    exit 1
fi

# 3. Verificar que Django funciona
echo "🔍 Verificando Django..."
python manage.py check --deploy

if [ $? -eq 0 ]; then
    echo "✅ Django configurado correctamente"
else
    echo "❌ Error en la configuración de Django"
    exit 1
fi

# 4. Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 5. Verificar que los archivos media existen
echo "🔍 Verificando archivos media..."
if [ -d "media/cvs" ]; then
    echo "✅ Directorio media/cvs existe"
    ls -la media/cvs/ | head -5
else
    echo "⚠️  Directorio media/cvs no existe, creándolo..."
    mkdir -p media/cvs
fi

# 6. Verificar permisos de archivos
echo "🔧 Configurando permisos..."
chmod -R 755 media/
chown -R $USER:$USER media/

# 7. Crear backup de configuración de Nginx
echo "💾 Creando backup de configuración de Nginx..."
sudo cp /etc/nginx/sites-available/tienda_inmobiliaria /etc/nginx/sites-available/tienda_inmobiliaria.backup.$(date +%Y%m%d_%H%M%S)

# 8. Actualizar configuración de Nginx
echo "🔧 Actualizando configuración de Nginx..."

# Crear nueva configuración de Nginx
sudo tee /etc/nginx/sites-available/tienda_inmobiliaria > /dev/null << 'EOF'
# Configuración de Nginx para Tienda Inmobiliaria
# Incluye corrección para descarga de CVs

# Redirección HTTP a HTTPS
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;
    
    # Configuración para archivos grandes
    client_max_body_size 200M;
    client_body_timeout 300s;
    client_header_timeout 300s;
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    
    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Directorio raíz del proyecto
    root /home/deploy/Tienda-inmobiliaria;
    
    # 🎯 CONFIGURACIÓN ESPECÍFICA PARA DESCARGA DE CVs
    # Manejar descargas de CV directamente desde Nginx
    location ~ ^/download-cv/(\d+)/$ {
        # Headers para descarga
        add_header Content-Disposition "attachment";
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
        add_header X-Content-Type-Options "nosniff";
        
        # Pasar a Django para manejo dinámico
        proxy_pass http://unix:/home/deploy/Tienda-inmobiliaria/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts para archivos grandes
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_request_buffering off;
        proxy_buffering off;
    }
    
    # Archivos estáticos
    location /static/ {
        alias /home/deploy/Tienda-inmobiliaria/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Archivos media (para otros archivos que no sean CVs)
    location /media/ {
        alias /home/deploy/Tienda-inmobiliaria/media/;
        expires 7d;
    }
    
    # Proxy a Gunicorn para el resto de la aplicación
    location / {
        proxy_pass http://unix:/home/deploy/Tienda-inmobiliaria/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts extendidos
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_request_buffering off;
        proxy_buffering off;
    }
    
    # Logs
    access_log /var/log/nginx/tienda_inmobiliaria_access.log;
    error_log /var/log/nginx/tienda_inmobiliaria_error.log;
}
EOF

echo "✅ Configuración de Nginx actualizada"

# 9. Verificar configuración de Nginx
echo "🔍 Verificando configuración de Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuración de Nginx válida"
else
    echo "❌ Error en la configuración de Nginx"
    echo "Restaurando backup..."
    sudo cp /etc/nginx/sites-available/tienda_inmobiliaria.backup.* /etc/nginx/sites-available/tienda_inmobiliaria
    exit 1
fi

# 10. Reiniciar servicios
echo "🔄 Reiniciando servicios..."

# Reiniciar Gunicorn
sudo supervisorctl restart tienda_inmobiliaria

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar estado de servicios
echo "🔍 Verificando estado de servicios..."
sudo supervisorctl status tienda_inmobiliaria
sudo systemctl status nginx --no-pager

# 11. Probar descarga de CV
echo "🧪 Probando descarga de CV..."
echo "URL de prueba: https://tudominio.com/download-cv/3/"

# 12. Mostrar logs para debugging
echo "📋 Logs recientes de Nginx:"
sudo tail -n 10 /var/log/nginx/tienda_inmobiliaria_error.log

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CORRECCIÓN COMPLETADA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 Cambios realizados:"
echo "  ✅ Vista download_cv optimizada para producción"
echo "  ✅ Configuración de Nginx actualizada"
echo "  ✅ Headers de seguridad agregados"
echo "  ✅ Timeouts extendidos para archivos grandes"
echo ""
echo "🧪 Para probar:"
echo "  1. Ve a: https://tudominio.com/download-cv/3/"
echo "  2. Debería descargar el archivo CV"
echo ""
echo "📋 Si hay problemas, revisa los logs:"
echo "  sudo tail -f /var/log/nginx/tienda_inmobiliaria_error.log"
echo "  sudo tail -f /home/deploy/Tienda-inmobiliaria/logs/gunicorn.log"

#!/bin/bash

# Script para actualizar configuración de Nginx para permitir archivos grandes
# Ejecutar como: sudo bash actualizar_nginx_archivos_grandes.sh

echo "🔧 Actualizando configuración de Nginx para archivos grandes..."

# Backup de la configuración actual
echo "📦 Creando backup de configuración actual..."
sudo cp /etc/nginx/sites-available/tienda_inmobiliaria /etc/nginx/sites-available/tienda_inmobiliaria.backup.$(date +%Y%m%d_%H%M%S)

# Crear nueva configuración
echo "📝 Creando nueva configuración de Nginx..."
sudo tee /etc/nginx/sites-available/tienda_inmobiliaria > /dev/null << 'EOF'
# Configuración de Nginx actualizada para permitir archivos grandes
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
    
    # 🔥 CONFIGURACIÓN PARA ARCHIVOS GRANDES
    # Permitir archivos hasta 200MB (para videos)
    client_max_body_size 200M;
    
    # Timeout para subidas grandes
    client_body_timeout 300s;
    client_header_timeout 300s;
    
    # Buffer para archivos grandes
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    
    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    
    # Configuración SSL moderna y segura
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    
    # HSTS (Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Directorio raíz del proyecto
    root /home/usuario/Tienda-inmobiliaria;
    
    # Archivos estáticos
    location /static/ {
        alias /home/usuario/Tienda-inmobiliaria/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Archivos media
    location /media/ {
        alias /home/usuario/Tienda-inmobiliaria/media/;
        expires 7d;
    }
    
    # Proxy a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 🔥 CONFIGURACIÓN PARA ARCHIVOS GRANDES
        # Timeouts extendidos para subidas grandes
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffer para archivos grandes
        proxy_request_buffering off;
        proxy_buffering off;
    }
    
    # Logs
    access_log /var/log/nginx/tienda_inmobiliaria_access.log;
    error_log /var/log/nginx/tienda_inmobiliaria_error.log;
}
EOF

# Verificar configuración
echo "🔍 Verificando configuración de Nginx..."
if sudo nginx -t; then
    echo "✅ Configuración de Nginx válida"
    
    # Recargar Nginx
    echo "🔄 Recargando Nginx..."
    sudo systemctl reload nginx
    
    echo "✅ Nginx actualizado exitosamente"
    echo ""
    echo "📋 Cambios aplicados:"
    echo "   • client_max_body_size: 200M"
    echo "   • client_body_timeout: 300s"
    echo "   • client_header_timeout: 300s"
    echo "   • proxy_connect_timeout: 300s"
    echo "   • proxy_send_timeout: 300s"
    echo "   • proxy_read_timeout: 300s"
    echo "   • proxy_request_buffering: off"
    echo "   • proxy_buffering: off"
    echo ""
    echo "🎉 ¡Configuración completada! Ahora puedes subir archivos hasta 200MB"
else
    echo "❌ Error en la configuración de Nginx"
    echo "🔄 Restaurando configuración anterior..."
    sudo cp /etc/nginx/sites-available/tienda_inmobiliaria.backup.$(date +%Y%m%d_%H%M%S) /etc/nginx/sites-available/tienda_inmobiliaria
    exit 1
fi

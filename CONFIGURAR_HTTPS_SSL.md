# 🔒 GUÍA COMPLETA: CONFIGURAR HTTPS/SSL

## 📋 Tabla de Contenidos
1. [Preparativos](#preparativos)
2. [Opción 1: Let's Encrypt (Gratuito - Recomendado)](#opción-1-lets-encrypt)
3. [Opción 2: Certificado Comercial](#opción-2-certificado-comercial)
4. [Configuración de Nginx](#configuración-de-nginx)
5. [Configuración de Apache](#configuración-de-apache)
6. [Verificación](#verificación)
7. [Renovación Automática](#renovación-automática)

---

## Preparativos

### Requisitos Previos:
- ✅ Dominio registrado apuntando a tu servidor
- ✅ Servidor con IP pública
- ✅ Puerto 80 y 443 abiertos en firewall
- ✅ Django configurado para producción

### Verificar DNS:
```bash
# Verificar que tu dominio apunte a tu servidor
nslookup tudominio.com

# O con dig
dig tudominio.com +short
```

---

## Opción 1: Let's Encrypt (Gratuito - Recomendado)

Let's Encrypt proporciona certificados SSL gratuitos válidos por 90 días con renovación automática.

### 1. Instalar Certbot

#### En Ubuntu/Debian:
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

#### En CentOS/RHEL:
```bash
sudo yum install epel-release
sudo yum install certbot python3-certbot-nginx
```

#### En Windows:
```powershell
# Descargar Certbot para Windows desde:
# https://dl.eff.org/certbot-beta-installer-win32.exe
```

### 2. Obtener Certificado SSL

#### Con Nginx (Automático):
```bash
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

#### Con Apache (Automático):
```bash
sudo certbot --apache -d tudominio.com -d www.tudominio.com
```

#### Modo Manual (Standalone):
```bash
# Detener servidor web temporalmente
sudo systemctl stop nginx

# Obtener certificado
sudo certbot certonly --standalone -d tudominio.com -d www.tudominio.com

# Reiniciar servidor web
sudo systemctl start nginx
```

### 3. Archivos Generados

Los certificados se guardan en:
```
/etc/letsencrypt/live/tudominio.com/
├── cert.pem           # Certificado del dominio
├── chain.pem          # Cadena de certificados
├── fullchain.pem      # Certificado + Cadena
└── privkey.pem        # Clave privada
```

---

## Opción 2: Certificado Comercial

### Proveedores Populares:
- Namecheap SSL
- GoDaddy SSL
- DigiCert
- Comodo

### Pasos Generales:

#### 1. Generar CSR (Certificate Signing Request):
```bash
openssl req -new -newkey rsa:2048 -nodes \
  -keyout tudominio.com.key \
  -out tudominio.com.csr
```

#### 2. Enviar CSR al proveedor y esperar validación

#### 3. Recibir certificados:
- `tudominio.com.crt` (tu certificado)
- `tudominio.com.ca-bundle` (cadena intermedia)

#### 4. Instalar en servidor (ver secciones de Nginx/Apache)

---

## Configuración de Nginx

### 1. Crear Configuración SSL

Crear archivo: `/etc/nginx/sites-available/tienda_inmobiliaria_ssl`

```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    
    # Permitir Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirigir todo a HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;
    
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
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Logs
    access_log /var/log/nginx/tienda_inmobiliaria_access.log;
    error_log /var/log/nginx/tienda_inmobiliaria_error.log;
}
```

### 2. Habilitar Configuración

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/tienda_inmobiliaria_ssl /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

---

## Configuración de Apache

### 1. Habilitar Módulos SSL

```bash
sudo a2enmod ssl
sudo a2enmod headers
sudo a2enmod rewrite
sudo systemctl restart apache2
```

### 2. Crear Configuración SSL

Crear archivo: `/etc/apache2/sites-available/tienda_inmobiliaria_ssl.conf`

```apache
# Redirigir HTTP a HTTPS
<VirtualHost *:80>
    ServerName tudominio.com
    ServerAlias www.tudominio.com
    
    # Permitir Let's Encrypt validation
    <Directory "/var/www/html/.well-known">
        Require all granted
    </Directory>
    
    # Redirigir todo a HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

# Servidor HTTPS
<VirtualHost *:443>
    ServerName tudominio.com
    ServerAlias www.tudominio.com
    
    # Certificados SSL
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/tudominio.com/cert.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/tudominio.com/privkey.pem
    SSLCertificateChainFile /etc/letsencrypt/live/tudominio.com/chain.pem
    
    # Protocolo SSL moderno
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite HIGH:!aNULL:!MD5
    SSLHonorCipherOrder on
    
    # HSTS
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    
    # Security Headers
    Header always set X-Frame-Options "DENY"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    
    # Directorio del proyecto
    DocumentRoot /home/usuario/Tienda-inmobiliaria
    
    # Archivos estáticos
    Alias /static /home/usuario/Tienda-inmobiliaria/staticfiles
    <Directory /home/usuario/Tienda-inmobiliaria/staticfiles>
        Require all granted
    </Directory>
    
    # Archivos media
    Alias /media /home/usuario/Tienda-inmobiliaria/media
    <Directory /home/usuario/Tienda-inmobiliaria/media>
        Require all granted
    </Directory>
    
    # Proxy a Gunicorn
    ProxyPreserveHost On
    ProxyPass /static !
    ProxyPass /media !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    # Logs
    ErrorLog ${APACHE_LOG_DIR}/tienda_inmobiliaria_error.log
    CustomLog ${APACHE_LOG_DIR}/tienda_inmobiliaria_access.log combined
</VirtualHost>
```

### 3. Habilitar Sitio

```bash
# Habilitar sitio
sudo a2ensite tienda_inmobiliaria_ssl.conf

# Verificar configuración
sudo apache2ctl configtest

# Recargar Apache
sudo systemctl reload apache2
```

---

## Verificación

### 1. Probar Certificado SSL

```bash
# Con openssl
openssl s_client -connect tudominio.com:443 -showcerts

# Ver detalles del certificado
echo | openssl s_client -servername tudominio.com -connect tudominio.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 2. Verificar en Navegador

Visita: `https://tudominio.com`

Verifica:
- ✅ Candado verde en la barra de direcciones
- ✅ Certificado válido
- ✅ Sin advertencias de seguridad

### 3. Pruebas de Seguridad SSL

#### SSL Labs Test:
```
https://www.ssllabs.com/ssltest/analyze.html?d=tudominio.com
```
**Objetivo:** Calificación A+

#### Security Headers:
```
https://securityheaders.com/?q=tudominio.com
```

### 4. Verificar Django Settings

Asegúrate de que en `.env` (producción):
```env
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
```

---

## Renovación Automática

### Let's Encrypt Auto-Renewal

#### 1. Verificar Renovación Automática

```bash
# Ver status del timer de renovación
sudo systemctl status certbot.timer

# Probar renovación (dry-run)
sudo certbot renew --dry-run
```

#### 2. Configurar Cron Job (si no está automático)

```bash
# Editar crontab
sudo crontab -e

# Agregar línea para renovar cada día a las 3 AM
0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

#### 3. Hook Post-Renovación

Crear script: `/etc/letsencrypt/renewal-hooks/deploy/reload-webserver.sh`

```bash
#!/bin/bash
systemctl reload nginx
# O para Apache: systemctl reload apache2
```

```bash
# Dar permisos de ejecución
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-webserver.sh
```

### Renovación Manual

```bash
# Renovar certificados
sudo certbot renew

# Forzar renovación (aunque no haya expirado)
sudo certbot renew --force-renewal

# Recargar servidor web
sudo systemctl reload nginx
```

---

## Troubleshooting

### Problema: "Connection Refused" en puerto 443

```bash
# Verificar que el puerto esté abierto
sudo netstat -tulpn | grep :443

# Verificar firewall
sudo ufw status
sudo ufw allow 443/tcp
```

### Problema: "Certificate Verify Failed"

```bash
# Verificar cadena de certificados
openssl verify -CAfile /etc/letsencrypt/live/tudominio.com/chain.pem \
  /etc/letsencrypt/live/tudominio.com/cert.pem
```

### Problema: "Mixed Content" en navegador

En Django settings.py:
```python
# Forzar HTTPS en producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## Checklist Final

- [ ] Certificado SSL instalado
- [ ] Redirección HTTP → HTTPS funciona
- [ ] Headers de seguridad configurados
- [ ] HSTS habilitado
- [ ] SSL Labs Test: Calificación A o A+
- [ ] Renovación automática configurada
- [ ] Backup de certificados realizado
- [ ] Django configurado para HTTPS
- [ ] Archivos estáticos y media cargan correctamente
- [ ] Sin advertencias "Mixed Content"

---

## Recursos Adicionales

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Best Practices](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)
- [Security Headers Guide](https://securityheaders.com/)

---

**Última actualización:** 30 de Septiembre, 2025  
**Soporte:** Para asistencia adicional, consulta la documentación oficial o contacta al equipo de desarrollo.


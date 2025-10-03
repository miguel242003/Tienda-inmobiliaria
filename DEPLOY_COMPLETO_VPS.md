# 🚀 GUÍA COMPLETA: DEPLOY A VPS OVHCLOUD

## 📋 INFORMACIÓN REQUERIDA

Antes de empezar, ten a mano:

```
✅ IP del VPS OVHcloud:      _________________
✅ Usuario root:              root
✅ Contraseña VPS:           _________________
✅ Tu dominio DonWeb:        _________________
✅ Email para SSL:           _________________
✅ URL de GitHub:            git@github.com:TU_USUARIO/Tienda-inmobiliaria.git
```

---

# PARTE 1: SUBIR CÓDIGO SEGURO A GITHUB

## Paso 1.1: Verificar que .env NO se subirá

```bash
# Verificar .gitignore
git status

# NO debe aparecer .env en la lista
# Si aparece, añádelo a .gitignore:
echo ".env" >> .gitignore
```

## Paso 1.2: Subir cambios a GitHub

```bash
git add .
git commit -m "🔒 Seguridad: Proteger datos sensibles + Preparar para producción"
git push origin main
```

---

# PARTE 2: CONFIGURACIÓN INICIAL DEL VPS

## Paso 2.1: Conectarse con PuTTY

1. Abre **PuTTY**
2. Host Name: **[IP de tu VPS]**
3. Puerto: **22**
4. Connection type: **SSH**
5. Clic en **Open**
6. Login as: **root**
7. Password: **[tu contraseña]**

## Paso 2.2: Actualizar Sistema

```bash
# Actualizar todo
apt update && apt upgrade -y

# Instalar herramientas básicas
apt install -y curl wget git vim nano htop unzip software-properties-common build-essential ufw fail2ban
```

## Paso 2.3: Crear Usuario No-Root

```bash
# Crear usuario deploy (más seguro que usar root)
adduser deploy

# Darle permisos sudo
usermod -aG sudo deploy

# Cambiar a ese usuario
su - deploy
```

**⚠️ IMPORTANTE:** A partir de ahora usa el usuario `deploy`

## Paso 2.4: Configurar Firewall

```bash
# Permitir SSH, HTTP y HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

## Paso 2.5: Configurar Fail2Ban (Anti-Hacking)

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

# PARTE 3: INSTALACIÓN DEL STACK

## Paso 3.1: Python 3.11+

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar versión
python3 --version
```

## Paso 3.2: MySQL

```bash
# Instalar MySQL
sudo apt install -y mysql-server libmysqlclient-dev pkg-config

# Asegurar MySQL
sudo mysql_secure_installation
```

**Responde:**
- Set root password? → **Y** (elige contraseña segura)
- Remove anonymous users? → **Y**
- Disallow root login remotely? → **Y**
- Remove test database? → **Y**
- Reload privilege tables? → **Y**

### Crear Base de Datos

```bash
sudo mysql
```

Ejecuta en MySQL:

```sql
CREATE DATABASE tienda_inmobiliaria_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tienda_user'@'localhost' IDENTIFIED BY 'PASSWORD_SEGURA_AQUI';
GRANT ALL PRIVILEGES ON tienda_inmobiliaria_prod.* TO 'tienda_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**📝 Guarda estos datos para el .env:**
```
DB_NAME: tienda_inmobiliaria_prod
DB_USER: tienda_user
DB_PASSWORD: [tu contraseña]
```

## Paso 3.3: Redis

```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verificar que funciona
redis-cli ping
# Debe responder: PONG
```

## Paso 3.4: Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Verificar
sudo systemctl status nginx
```

## Paso 3.5: Supervisor (Gestión de Procesos)

```bash
sudo apt install -y supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor
```

## Paso 3.6: Certbot (SSL Gratuito)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

# PARTE 4: CONFIGURAR DNS (CONECTAR DOMINIO)

## Paso 4.1: Configurar DNS en DonWeb

1. Ingresa al panel de **DonWeb**: https://www.donweb.com/
2. Ve a **"Mis Dominios"**
3. Selecciona tu dominio
4. Busca **"Administrar DNS"** o **"Zona DNS"**
5. Configura estos registros:

```
┌─────────────────────────────────────────────────┐
│ Tipo  │ Host/Nombre │ Apunta a      │ TTL      │
├─────────────────────────────────────────────────┤
│ A     │ @           │ [IP_DE_VPS]   │ 3600     │
│ A     │ www         │ [IP_DE_VPS]   │ 3600     │
└─────────────────────────────────────────────────┘

Ejemplo con IP 185.123.45.67:
┌─────────────────────────────────────────────────┐
│ A     │ @           │ 185.123.45.67 │ 3600     │
│ A     │ www         │ 185.123.45.67 │ 3600     │
└─────────────────────────────────────────────────┘
```

6. **Guarda los cambios**

## Paso 4.2: Verificar Propagación DNS

```bash
# Desde el VPS, verificar que el dominio apunta correctamente
dig tudominio.com.ar +short

# Debe mostrar la IP del VPS
```

⏱️ **Tiempo:** 15 min - 48 horas (normalmente 1-2 horas)

---

# PARTE 5: CONFIGURAR GITHUB Y CLONAR PROYECTO

## Paso 5.1: Generar Clave SSH

```bash
# Generar clave SSH
ssh-keygen -t ed25519 -C "tu_email@gmail.com"

# Presiona Enter 3 veces (ubicación por defecto, sin passphrase)

# Mostrar la clave pública
cat ~/.ssh/id_ed25519.pub
```

**Copia toda la clave** (empieza con `ssh-ed25519...`)

## Paso 5.2: Agregar Clave a GitHub

1. Ve a **GitHub.com**
2. Clic en tu foto → **Settings**
3. **SSH and GPG keys** (menú izquierdo)
4. **New SSH key**
5. Title: `VPS OVHcloud Producción`
6. Key: **Pega la clave copiada**
7. **Add SSH key**

## Paso 5.3: Probar Conexión

```bash
ssh -T git@github.com

# Debe responder:
# Hi TU_USUARIO! You've successfully authenticated...
```

## Paso 5.4: Clonar Repositorio

```bash
cd ~
git clone git@github.com:TU_USUARIO/Tienda-inmobiliaria.git
cd Tienda-inmobiliaria
```

---

# PARTE 6: CONFIGURAR PROYECTO DJANGO

## Paso 6.1: Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate

# El prompt debe cambiar a: (venv) deploy@vps:~/Tienda-inmobiliaria$
```

## Paso 6.2: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

## Paso 6.3: Crear Archivo .env

```bash
nano .env
```

**Contenido del .env (COMPLETA CON TUS DATOS):**

```env
# Django
SECRET_KEY=[GENERA_UNA_NUEVA_CON_EL_COMANDO_DE_ABAJO]
DEBUG=False
ALLOWED_HOSTS=tudominio.com.ar,www.tudominio.com.ar

# MySQL
DB_ENGINE=django.db.backends.mysql
DB_NAME=tienda_inmobiliaria_prod
DB_USER=tienda_user
DB_PASSWORD=[password_mysql_que_creaste_antes]
DB_HOST=localhost
DB_PORT=3306

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Email
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=[password_aplicacion_gmail]
ADMIN_EMAIL=tu_email@gmail.com

# CSRF
CSRF_TRUSTED_ORIGINS=https://tudominio.com.ar,https://www.tudominio.com.ar
```

**Generar SECRET_KEY:**

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Guarda el archivo: `Ctrl + O`, `Enter`, `Ctrl + X`

## Paso 6.4: Ejecutar Migraciones

```bash
cd ~/Tienda-inmobiliaria

# Activar entorno virtual si no está activo
source venv/bin/activate

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

## Paso 6.5: Recolectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

## Paso 6.6: Probar Gunicorn

```bash
gunicorn tienda_meli.tienda_meli.wsgi:application --bind 0.0.0.0:8000

# Deberías poder acceder a http://IP_VPS:8000
# Ctrl + C para detener
```

---

# PARTE 7: CONFIGURAR GUNICORN CON SUPERVISOR

## Paso 7.1: Crear Script de Inicio

```bash
nano ~/Tienda-inmobiliaria/gunicorn_start.sh
```

**Contenido:**

```bash
#!/bin/bash

NAME="tienda_inmobiliaria"
DIR=/home/deploy/Tienda-inmobiliaria
USER=deploy
GROUP=deploy
WORKERS=3
BIND=unix:/home/deploy/Tienda-inmobiliaria/gunicorn.sock
DJANGO_SETTINGS_MODULE=tienda_meli.tienda_meli.settings
DJANGO_WSGI_MODULE=tienda_meli.tienda_meli.wsgi
LOG_LEVEL=error

cd $DIR
source venv/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DIR:$PYTHONPATH

exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=-
```

```bash
# Dar permisos de ejecución
chmod +x ~/Tienda-inmobiliaria/gunicorn_start.sh
```

## Paso 7.2: Configurar Supervisor

```bash
sudo nano /etc/supervisor/conf.d/tienda_inmobiliaria.conf
```

**Contenido:**

```ini
[program:tienda_inmobiliaria]
command=/home/deploy/Tienda-inmobiliaria/gunicorn_start.sh
user=deploy
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/deploy/Tienda-inmobiliaria/logs/gunicorn.log
```

```bash
# Crear carpeta de logs
mkdir -p ~/Tienda-inmobiliaria/logs

# Recargar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status tienda_inmobiliaria
```

---

# PARTE 8: CONFIGURAR NGINX

## Paso 8.1: Crear Configuración de Nginx

```bash
sudo nano /etc/nginx/sites-available/tienda_inmobiliaria
```

**Contenido (REEMPLAZA tudominio.com.ar):**

```nginx
server {
    listen 80;
    server_name tudominio.com.ar www.tudominio.com.ar;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/deploy/Tienda-inmobiliaria/staticfiles/;
    }

    location /media/ {
        alias /home/deploy/Tienda-inmobiliaria/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/deploy/Tienda-inmobiliaria/gunicorn.sock;
    }
}
```

## Paso 8.2: Activar Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/tienda_inmobiliaria /etc/nginx/sites-enabled/

# Eliminar sitio por defecto
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

**Ahora deberías poder ver tu sitio en:** `http://tudominio.com.ar`

---

# PARTE 9: INSTALAR SSL (HTTPS)

```bash
# Instalar certificado SSL con Let's Encrypt
sudo certbot --nginx -d tudominio.com.ar -d www.tudominio.com.ar

# Sigue las instrucciones:
# - Ingresa tu email
# - Acepta términos: Y
# - Redirect HTTP to HTTPS: 2 (Sí, redirigir)
```

**¡LISTO!** Tu sitio ahora está en: `https://tudominio.com.ar` 🔒

## Renovación Automática

```bash
# Probar renovación
sudo certbot renew --dry-run

# Certbot renovará automáticamente cada 60 días
```

---

# PARTE 10: DEPLOY AUTOMÁTICO DESDE GITHUB

## Paso 10.1: Crear Script de Deploy

```bash
nano ~/deploy.sh
```

**Contenido:**

```bash
#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 INICIANDO DEPLOY..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /home/deploy/Tienda-inmobiliaria

echo "📥 Obteniendo cambios de GitHub..."
git pull origin main

echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🗄️  Ejecutando migraciones..."
python manage.py migrate

echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "🔄 Reiniciando Gunicorn..."
sudo supervisorctl restart tienda_inmobiliaria

echo "✅ ¡DEPLOY COMPLETADO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

```bash
# Dar permisos
chmod +x ~/deploy.sh
```

## Paso 10.2: Uso del Script

```bash
# Cada vez que hagas cambios en tu código:

# 1. En tu computadora:
git add .
git commit -m "Descripción de cambios"
git push origin main

# 2. En el servidor VPS (PuTTY):
~/deploy.sh
```

---

# VERIFICACIÓN FINAL

## Checklist de Seguridad

```bash
✅ Firewall activo (UFW)
✅ Fail2Ban configurado
✅ Usuario no-root creado
✅ DEBUG=False en producción
✅ SSL/HTTPS activo
✅ Datos sensibles en .env (no en código)
✅ Backups configurados (opcional)
```

## URLs de Verificación

```
✅ https://tudominio.com.ar → Debe cargar tu sitio
✅ https://tudominio.com.ar/admin → Panel admin de Django
✅ SSL válido (candado verde en navegador)
```

---

# COMANDOS ÚTILES

```bash
# Ver logs de Gunicorn
tail -f ~/Tienda-inmobiliaria/logs/gunicorn.log

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar servicios
sudo supervisorctl restart tienda_inmobiliaria
sudo systemctl restart nginx

# Ver estado de servicios
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis-server

# Actualizar proyecto
cd ~/Tienda-inmobiliaria
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart tienda_inmobiliaria
```

---

# ¡FELICIDADES! 🎉

Tu proyecto inmobiliario está ahora en producción con:
- ✅ Dominio propio
- ✅ HTTPS/SSL
- ✅ MySQL en producción
- ✅ Redis para caché
- ✅ Deploy automático desde GitHub
- ✅ Seguridad configurada

---

# SOPORTE

Si encuentras errores, revisa:
1. Logs de Gunicorn: `tail -f ~/Tienda-inmobiliaria/logs/gunicorn.log`
2. Logs de Nginx: `sudo tail -f /var/log/nginx/error.log`
3. Estado de servicios: `sudo supervisorctl status`


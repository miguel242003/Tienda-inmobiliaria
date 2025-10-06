# 🔧 Solución al Problema de Login en Otro Computador

## 📋 Descripción del Problema

Cuando intentas iniciar sesión desde otro computador en `gisa-nqn.com`, el sistema autentica las credenciales (la URL cambia a `/login/dashboard/`) pero no muestra el dashboard, sino que vuelve a mostrar el formulario de login. Esto indica que **las sesiones no se están guardando correctamente**.

## 🔍 Causa del Problema

El problema se debe a **configuración incorrecta de las sesiones** en producción:

1. **Redis no configurado**: El sistema estaba configurado para usar Redis para las sesiones, pero si Redis no está instalado o configurado en el servidor, las sesiones no se guardan.

2. **Dominio no permitido**: El dominio `gisa-nqn.com` no estaba en `ALLOWED_HOSTS` ni en `CSRF_TRUSTED_ORIGINS`.

3. **Cookies seguras sin HTTPS**: Si el sitio no tiene HTTPS configurado correctamente, las cookies con `SESSION_COOKIE_SECURE = True` no se establecen.

## ✅ Soluciones Aplicadas

He realizado los siguientes cambios en `tienda_meli/tienda_meli/settings.py`:

### 1. ✅ Cambio de Motor de Sesiones

**Antes:**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Requiere Redis
```

**Después:**
```python
# Producción: Usar cached_db (cache con fallback a base de datos)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
```

**Beneficio:** Si Redis no está disponible, las sesiones se guardan en la base de datos automáticamente.

### 2. ✅ Dominios Permitidos

**Antes:**
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
CSRF_TRUSTED_ORIGINS = [...]
```

**Después:**
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,gisa-nqn.com,www.gisa-nqn.com').split(',')
CSRF_TRUSTED_ORIGINS = [
    'https://gisa-nqn.com',
    'https://www.gisa-nqn.com',
    'http://gisa-nqn.com',  # Temporal para debug
    'http://www.gisa-nqn.com',
]
```

### 3. ✅ Configuración de Cookies de Sesión

**Añadido:**
```python
SESSION_COOKIE_AGE = 43200  # 12 horas (antes 1 hora)
SESSION_COOKIE_DOMAIN = None  # Permitir subdominios
SESSION_COOKIE_NAME = 'tienda_sessionid'  # Nombre único
```

## 🚀 Pasos para Implementar la Solución

### **Paso 1: Subir los cambios al servidor**

```bash
# En tu computadora local, confirma los cambios
git add tienda_meli/tienda_meli/settings.py
git commit -m "Fix: Corregir problema de sesiones en login desde otro computador"
git push origin main
```

### **Paso 2: En el servidor, actualizar el código**

Conéctate al servidor y ejecuta:

```bash
# Ir al directorio del proyecto
cd /ruta/a/Tienda-inmobiliaria

# Actualizar código desde repositorio
git pull origin main

# Crear tabla de sesiones en la base de datos
python manage.py migrate

# Reiniciar el servidor (Gunicorn/uWSGI)
sudo systemctl restart gunicorn  # o el nombre de tu servicio
# O si usas uWSGI:
# sudo systemctl restart uwsgi
```

### **Paso 3: Verificar configuración del archivo .env en el servidor**

Asegúrate de que el archivo `.env` en el servidor tenga:

```bash
# Dominio en producción
ALLOWED_HOSTS=gisa-nqn.com,www.gisa-nqn.com,localhost,127.0.0.1

# Modo producción
DEBUG=False

# Base de datos (MySQL recomendado para producción)
DB_ENGINE=django.db.backends.mysql
DB_NAME=tu_base_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_PORT=3306
```

### **Paso 4: Limpiar sesiones antiguas**

```bash
# Limpiar sesiones expiradas
python manage.py clearsessions
```

### **Paso 5: Verificar certificado SSL/HTTPS**

El sitio **DEBE tener HTTPS configurado** para que funcione correctamente en producción. Verifica:

```bash
# Verificar si Nginx tiene SSL configurado
sudo nginx -t
sudo systemctl status nginx

# Si no tienes SSL, instalar con Let's Encrypt (Certbot)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d gisa-nqn.com -d www.gisa-nqn.com
```

## 🧪 Verificación y Testing

### **Test 1: Verificar que el servidor responde**

```bash
curl -I https://gisa-nqn.com/login/admin-login/
```

Deberías ver: `HTTP/2 200 OK`

### **Test 2: Verificar cookies de sesión**

1. Abre el navegador en modo incógnito
2. Ve a `https://gisa-nqn.com/login/admin-login/`
3. Abre las DevTools (F12) → pestaña "Application" → "Cookies"
4. Busca la cookie `tienda_sessionid`
5. Verifica que:
   - ✅ **HttpOnly:** Yes
   - ✅ **Secure:** Yes (si tienes HTTPS)
   - ✅ **SameSite:** Lax

### **Test 3: Probar login completo**

1. Ingresa email y contraseña
2. Haz clic en "Iniciar Sesión"
3. Deberías ver el dashboard (no volver al login)
4. Recarga la página (F5) - deberías seguir en el dashboard

## 🔍 Script de Diagnóstico

He creado un script de diagnóstico. Ejecútalo en el servidor:

```bash
python diagnostico_sesiones.py
```

Este script verificará:
- ✅ Configuración de sesiones
- ✅ Base de datos de sesiones
- ✅ Permisos de archivos
- ✅ Variables de entorno
- ✅ Estado de Redis (si aplica)

## ❓ Preguntas Frecuentes

### ¿Por qué funcionaba en un computador y no en otro?

Probablemente el primer computador estaba accediendo desde `localhost` o `127.0.0.1` (desarrollo), donde las configuraciones de seguridad son más laxas. El otro computador accedía desde el dominio público (`gisa-nqn.com`), donde se aplican las configuraciones de producción.

### ¿Por qué la URL cambia pero no muestra el dashboard?

Django autentica correctamente (por eso redirige a `/dashboard/`), pero al intentar cargar el dashboard, el decorador `@login_required` verifica la sesión, no la encuentra (porque no se guardó), y redirige de vuelta al login.

### ¿Necesito Redis obligatoriamente?

No. Con el cambio a `cached_db`, el sistema usará Redis si está disponible (para mejor rendimiento), pero funcionará perfectamente con solo la base de datos si Redis no está configurado.

### ¿Cuánto tiempo dura la sesión ahora?

12 horas desde el último acceso (antes era 1 hora). Esto mejora la experiencia del usuario sin comprometer mucho la seguridad.

## 🆘 Si el Problema Persiste

Si después de aplicar estos cambios el problema continúa:

1. **Verifica los logs del servidor:**
   ```bash
   # Ver logs de Django
   tail -f logs/django.log
   
   # Ver logs de Nginx
   sudo tail -f /var/log/nginx/error.log
   
   # Ver logs de Gunicorn
   sudo journalctl -u gunicorn -f
   ```

2. **Verifica que DEBUG=False en producción:**
   ```bash
   grep DEBUG /path/to/.env
   ```

3. **Ejecuta el script de diagnóstico:**
   ```bash
   python diagnostico_sesiones.py
   ```

4. **Habilita logging temporalmente en settings.py:**
   ```python
   # Añadir al final de settings.py temporalmente
   if not DEBUG:
       LOGGING['loggers']['django']['level'] = 'INFO'
   ```

5. **Contacta con estos detalles:**
   - Salida del script de diagnóstico
   - Logs relevantes
   - Versión de Django: `python manage.py --version`
   - Sistema operativo del servidor: `uname -a`

## 📝 Resumen de Comandos Completo

```bash
# 1. En tu computadora local
git add tienda_meli/tienda_meli/settings.py
git commit -m "Fix: Corregir problema de sesiones en login"
git push origin main

# 2. En el servidor
cd /ruta/a/Tienda-inmobiliaria
git pull origin main
python manage.py migrate
python manage.py clearsessions
python diagnostico_sesiones.py
sudo systemctl restart gunicorn

# 3. Verificar
curl -I https://gisa-nqn.com/login/admin-login/
```

## ✅ Checklist Final

- [ ] Cambios subidos al repositorio
- [ ] Código actualizado en el servidor
- [ ] Migraciones ejecutadas
- [ ] Tabla de sesiones creada
- [ ] Servidor reiniciado
- [ ] HTTPS configurado
- [ ] Archivo .env verificado
- [ ] Login probado desde otro computador
- [ ] Sesión persiste después de recargar

---

**Última actualización:** 2025-10-06  
**Autor:** Asistente IA  
**Estado:** ✅ Solución implementada


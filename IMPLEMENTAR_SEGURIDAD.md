# 🔒 GUÍA DE IMPLEMENTACIÓN DE SEGURIDAD

## ✅ CAMBIOS YA APLICADOS

### 1. settings.py - Configuración de Seguridad
- ✅ Sesiones y cookies seguras (HttpOnly, Secure, SameSite)
- ✅ Headers de seguridad (HSTS, XSS, Clickjacking)
- ✅ Logging de seguridad configurado
- ✅ Password hashers mejorados (Argon2)
- ✅ DEBUG=False por defecto
- ✅ ALLOWED_HOSTS restringido

### 2. login/views.py - Validación de Entradas
- ✅ Validación de email
- ✅ Sanitización con bleach
- ✅ No devolver passwords en contextos
- ✅ Validación de longitud de contraseña

---

## 📋 PASOS SIGUIENTES (Implementar en Orden)

### PASO 1: Instalar Dependencias de Seguridad

```powershell
# Instalar argon2 para mejor hashing
pip install argon2-cffi

# Instalar bleach para sanitización
pip install bleach

# Instalar rate limiting
pip install django-ratelimit

# Instalar validación de archivos
pip install python-magic

# Opcional: Herramientas de análisis
pip install bandit safety
```

### PASO 2: Actualizar .env

```env
# CONFIGURACION DE SEGURIDAD
DEBUG=True  # Cambiar a False en producción
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
DB_ENGINE=django.db.backends.mysql
DB_NAME=tienda_inmobiliaria_prod
DB_USER=tienda_user
DB_PASSWORD=tu-contraseña-segura
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### PASO 3: Verificar Configuración

```powershell
# Verificar configuración de Django
python manage.py check --deploy

# Debería mostrar advertencias de seguridad si algo falta
```

### PASO 4: Implementar Rate Limiting (IMPORTANTE)

Agregar a `login/views.py`:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def admin_login(request):
    # Tu código existente...
    pass
```

### PASO 5: Validación Robusta de Archivos

Crear archivo `propiedades/validators.py`:

```python
import magic
from django.core.exceptions import ValidationError
import re

def validar_archivo_imagen(archivo):
    """Validación robusta de archivos de imagen"""
    
    # 1. Validar tamaño (5MB)
    if archivo.size > 5 * 1024 * 1024:
        raise ValidationError('El archivo no debe superar 5MB.')
    
    # 2. Validar tipo MIME real
    mime = magic.from_buffer(archivo.read(1024), mime=True)
    archivo.seek(0)
    
    ALLOWED_MIMES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if mime not in ALLOWED_MIMES:
        raise ValidationError(f'Tipo de archivo no permitido: {mime}')
    
    # 3. Validar extensión
    ext = archivo.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        raise ValidationError(f'Extensión no permitida: {ext}')
    
    # 4. Sanitizar nombre
    nombre_seguro = re.sub(r'[^a-zA-Z0-9._-]', '_', archivo.name)
    archivo.name = nombre_seguro
    
    return archivo

def validar_archivo_video(archivo):
    """Validación robusta de archivos de video"""
    
    # 1. Validar tamaño (200MB para videos)
    if archivo.size > 200 * 1024 * 1024:
        raise ValidationError('El video no debe superar 200MB.')
    
    # 2. Validar tipo MIME
    mime = magic.from_buffer(archivo.read(1024), mime=True)
    archivo.seek(0)
    
    ALLOWED_MIMES = ['video/mp4', 'video/mpeg', 'video/quicktime']
    if mime not in ALLOWED_MIMES:
        raise ValidationError(f'Tipo de video no permitido: {mime}')
    
    return archivo
```

### PASO 6: Actualizar requirements.txt

```bash
# Actualizar archivo requirements.txt con las nuevas dependencias
pip freeze > requirements.txt
```

### PASO 7: Crear Directorio de Logs

```powershell
# Crear directorio para logs
New-Item -Path "logs" -ItemType Directory -Force
```

### PASO 8: Configurar .gitignore

Asegurar que `.gitignore` incluya:

```gitignore
# Logs de seguridad
logs/
*.log

# Variables de entorno
.env
.env.local
.env.production

# Base de datos
*.sqlite3
db.sqlite3

# Archivos de sesión
sessions/
```

---

## 🔍 VERIFICACIÓN DE SEGURIDAD

### Verificar Headers de Seguridad

```powershell
# Iniciar servidor
python manage.py runserver

# En otro terminal, verificar headers
curl -I http://localhost:8000
```

Deberías ver headers como:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` (o SAMEORIGIN en desarrollo)

### Análisis de Seguridad del Código

```powershell
# Instalar bandit
pip install bandit

# Ejecutar análisis
bandit -r . -f json -o security_report.json

# Ver reporte
type security_report.json
```

### Verificar Vulnerabilidades en Dependencias

```powershell
# Instalar safety
pip install safety

# Ejecutar verificación
safety check

# O con más detalles
safety check --json
```

---

## 🚨 ADVERTENCIAS IMPORTANTES

### ⚠️ Antes de Ir a Producción:

1. **Cambiar DEBUG a False en .env**
   ```env
   DEBUG=False
   ```

2. **Usar SECRET_KEY única y segura**
   ```python
   # Generar nueva SECRET_KEY
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Configurar ALLOWED_HOSTS correctamente**
   ```env
   ALLOWED_HOSTS=tudominio.com,www.tudominio.com
   ```

4. **Configurar HTTPS/SSL**
   - Obtener certificado SSL (Let's Encrypt gratuito)
   - Configurar redirección HTTP → HTTPS
   - Verificar que SECURE_SSL_REDIRECT=True

5. **Cambiar credenciales de base de datos**
   ```env
   DB_PASSWORD=contraseña-muy-segura-y-larga
   ```

6. **Configurar backups automáticos**
   - Base de datos MySQL
   - Archivos media
   - Configuración (.env)

---

## 📊 CHECKLIST PRE-PRODUCCIÓN

### Seguridad:
- [ ] DEBUG=False
- [ ] SECRET_KEY única y segura
- [ ] ALLOWED_HOSTS configurado
- [ ] HTTPS/SSL configurado
- [ ] Certificado SSL válido
- [ ] Headers de seguridad activos
- [ ] Sesiones y cookies seguras
- [ ] Rate limiting implementado
- [ ] Logging configurado
- [ ] Backups configurados

### Base de Datos:
- [ ] MySQL configurado
- [ ] Usuario con permisos limitados
- [ ] Contraseña segura
- [ ] Backup automático configurado
- [ ] Sin datos de prueba

### Código:
- [ ] Sin credenciales hardcodeadas
- [ ] Todas las entradas validadas
- [ ] Archivos validados robustamente
- [ ] Sin código de debug
- [ ] Logs sensibles eliminados

### Infraestructura:
- [ ] Firewall configurado
- [ ] Puerto 22 (SSH) seguro
- [ ] Puerto 3306 (MySQL) solo local
- [ ] Nginx/Apache configurado
- [ ] Gunicorn corriendo correctamente

---

## 🔗 RECURSOS ADICIONALES

- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [OWASP Django Security](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)
- [Mozilla SSL Configuration](https://ssl-config.mozilla.org/)
- [Let's Encrypt SSL](https://letsencrypt.org/)

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisa `logs/security.log`
2. Ejecuta `python manage.py check --deploy`
3. Verifica que todas las dependencias estén instaladas
4. Consulta la documentación de Django

---

**Última actualización:** 30 de Septiembre, 2025
**Versión:** 1.0


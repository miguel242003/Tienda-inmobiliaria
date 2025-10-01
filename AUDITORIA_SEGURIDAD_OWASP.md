# 🔒 AUDITORÍA DE SEGURIDAD - OWASP TOP 10
## Tienda Inmobiliaria - Análisis Completo

**Fecha:** 30 de Septiembre, 2025
**Auditor:** Asistente de Seguridad
**Framework:** OWASP Top 10 2021

---

## 📊 RESUMEN EJECUTIVO

### ✅ Fortalezas Detectadas:
- ✅ Django ORM (protección contra SQL Injection)
- ✅ CSRF middleware activado
- ✅ Validación de contraseñas de Django
- ✅ Autenticación 2FA implementada
- ✅ Uso de formularios Django con validación

### ⚠️ VULNERABILIDADES CRÍTICAS ENCONTRADAS:

| # | Vulnerabilidad | Severidad | Estado |
|---|----------------|-----------|--------|
| 1 | Configuración de sesiones insegura | 🔴 ALTA | Pendiente |
| 2 | Headers de seguridad faltantes | 🔴 ALTA | Pendiente |
| 3 | Fuga de información en errores | 🟡 MEDIA | Pendiente |
| 4 | Credenciales en código fuente | 🔴 ALTA | Pendiente |
| 5 | XSS potencial en mensajes de usuario | 🟡 MEDIA | Pendiente |
| 6 | Rate limiting ausente | 🟡 MEDIA | Pendiente |
| 7 | Validación de archivos insuficiente | 🟡 MEDIA | Pendiente |
| 8 | CORS no configurado | 🟢 BAJA | Pendiente |

---

## 🔴 VULNERABILIDADES CRÍTICAS

### 1. A01:2021 – Broken Access Control

#### 🔍 Problema Encontrado:
**Archivo:** `login/views.py` (línea 108-113)
```python
# ❌ VULNERABLE: Se devuelve la contraseña en el contexto del template
return render(request, 'login/admin_login.html', {
    'email': email,
    'password': password,  # ⚠️ NUNCA devolver contraseñas
    'show_2fa': True,
    'credenciales': credenciales
})
```

#### ✅ Solución:
```python
# ✅ SEGURO: No devolver contraseñas en el contexto
return render(request, 'login/admin_login.html', {
    'email': email,
    'show_2fa': True,
    'requires_2fa': True
})
```

---

### 2. A02:2021 – Cryptographic Failures

#### 🔍 Problema Encontrado:
**Archivo:** `tienda_meli/tienda_meli/settings.py`

```python
# ❌ INSEGURO: Falta configuración de sesiones y cookies seguras
# Sin SESSION_COOKIE_SECURE
# Sin SESSION_COOKIE_HTTPONLY
# Sin SESSION_COOKIE_SAMESITE
# Sin CSRF_COOKIE_SECURE
```

#### ✅ Solución Requerida:
```python
# Configuración de Sesiones Seguras
SESSION_COOKIE_SECURE = not DEBUG  # Solo HTTPS en producción
SESSION_COOKIE_HTTPONLY = True  # No accesible por JavaScript
SESSION_COOKIE_SAMESITE = 'Strict'  # Protección contra CSRF
SESSION_COOKIE_AGE = 3600  # 1 hora de sesión
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# Configuración de Cookies CSRF
CSRF_COOKIE_SECURE = not DEBUG  # Solo HTTPS en producción
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 31449600  # 1 año

# Configuración de Seguridad de Contraseñas
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Más seguro
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

---

### 3. A03:2021 – Injection

#### 🔍 Problema Encontrado:
**Archivo:** `login/views.py` (línea 81-84)

```python
# ⚠️ VULNERABLE: Input sin sanitización
email = request.POST.get('email')  # Sin validación
password = request.POST.get('password')  # Sin validación
```

#### ✅ Solución:
```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import bleach

# ✅ SEGURO: Validar y sanitizar inputs
email = request.POST.get('email', '').strip()
password = request.POST.get('password', '')

# Validar email
try:
    validate_email(email)
except ValidationError:
    messages.error(request, 'Email inválido.')
    return render(request, 'login/admin_login.html')

# Sanitizar email
email = bleach.clean(email)

# Validar longitud de contraseña
if len(password) < 8:
    messages.error(request, 'Contraseña demasiado corta.')
    return render(request, 'login/admin_login.html')
```

---

### 4. A04:2021 – Insecure Design

#### 🔍 Problema Encontrado:
**Archivo:** `tienda_meli/tienda_meli/settings.py`

```python
# ❌ INSEGURO: Credenciales hardcodeadas
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', 
                             default='gsam eenf yjvg bzeu')  # ⚠️ Contraseña en código
```

```python
# ❌ INSEGURO: DEBUG por defecto en True
DEBUG = config('DEBUG', default=True, cast=bool)  # ⚠️ Peligroso en producción
```

#### ✅ Solución:
```python
# ✅ SEGURO: Sin defaults peligrosos
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # Sin default
DEBUG = config('DEBUG', default=False, cast=bool)  # False por defecto
SECRET_KEY = config('SECRET_KEY')  # REQUERIDO en .env
```

---

### 5. A05:2021 – Security Misconfiguration

#### 🔍 Problemas Encontrados:

**1. Headers de Seguridad Faltantes:**
```python
# ❌ FALTAN configuraciones importantes:
# - SECURE_HSTS_SECONDS
# - SECURE_SSL_REDIRECT
# - SECURE_BROWSER_XSS_FILTER
# - SECURE_CONTENT_TYPE_NOSNIFF
# - X_FRAME_OPTIONS
```

#### ✅ Solución Completa:
```python
# Headers de Seguridad (Producción)
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Seguridad del navegador
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'  # Protección contra Clickjacking
    
    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Configuración de ALLOWED_HOSTS estricta
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Middleware de seguridad adicional
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

---

### 6. A06:2021 – Vulnerable and Outdated Components

#### 🔍 Verificar:
```bash
# Revisar dependencias vulnerables
pip list --outdated
pip install safety
safety check
```

---

### 7. A07:2021 – Identification and Authentication Failures

#### 🔍 Problema Encontrado:
**Falta Rate Limiting en login**

#### ✅ Solución - Implementar django-ratelimit:
```python
# Instalar: pip install django-ratelimit

from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def admin_login(request):
    # Máximo 5 intentos por minuto por IP
    ...
```

---

### 8. A08:2021 – Software and Data Integrity Failures

#### 🔍 Problema Encontrado:
**Archivo:** `propiedades/views.py` - Validación de archivos insuficiente

```python
# ⚠️ VULNERABLE: Validación básica de archivos
def upload_fotos_adicionales(request):
    for archivo in request.FILES.getlist('fotos_adicionales'):
        # Validación insuficiente
```

#### ✅ Solución:
```python
import magic
from django.core.exceptions import ValidationError

def validar_archivo_imagen(archivo):
    """Validación robusta de archivos de imagen"""
    
    # 1. Validar tamaño (5MB)
    if archivo.size > 5 * 1024 * 1024:
        raise ValidationError('El archivo no debe superar 5MB.')
    
    # 2. Validar tipo MIME real (no solo extensión)
    mime = magic.from_buffer(archivo.read(1024), mime=True)
    archivo.seek(0)  # Volver al inicio
    
    ALLOWED_MIMES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if mime not in ALLOWED_MIMES:
        raise ValidationError(f'Tipo de archivo no permitido: {mime}')
    
    # 3. Validar extensión
    ext = archivo.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        raise ValidationError(f'Extensión no permitida: {ext}')
    
    # 4. Sanitizar nombre de archivo
    import re
    nombre_seguro = re.sub(r'[^a-zA-Z0-9._-]', '_', archivo.name)
    archivo.name = nombre_seguro
    
    return archivo
```

---

### 9. A09:2021 – Security Logging and Monitoring Failures

#### ✅ Configuración Requerida:
```python
# Logging de seguridad
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR.parent / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR.parent / 'logs' / 'django_security.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
```

---

### 10. A10:2021 – Server-Side Request Forgery (SSRF)

#### ✅ No se encontraron vulnerabilidades SSRF en el código actual.

---

## 🛡️ PROTECCIÓN XSS (Cross-Site Scripting)

### Templates de Django (Auto-escape activado)
✅ Django escapa automáticamente variables en templates
✅ Usar `{{ variable }}` en lugar de `{{ variable|safe }}`

### ⚠️ Revisar estos archivos:
```python
# Buscar uso de |safe o mark_safe
grep -r "|safe" templates/
grep -r "mark_safe" *.py
```

### ✅ Sanitizar entradas de usuario:
```python
import bleach

def clean_user_input(text, allow_tags=None):
    """Sanitizar entrada HTML de usuarios"""
    if allow_tags is None:
        allow_tags = []  # Sin tags por defecto
    
    return bleach.clean(
        text,
        tags=allow_tags,
        attributes={},
        strip=True
    )
```

---

## 📝 PLAN DE ACCIÓN PRIORITARIO

### 🔴 CRÍTICO (Hacer AHORA):
1. ✅ Agregar configuración de sesiones seguras
2. ✅ Agregar headers de seguridad
3. ✅ Eliminar contraseñas de defaults
4. ✅ No devolver passwords en contextos
5. ✅ Agregar validación de archivos robusta

### 🟡 IMPORTANTE (Hacer esta semana):
6. ✅ Implementar rate limiting
7. ✅ Agregar logging de seguridad
8. ✅ Sanitizar todas las entradas de usuario
9. ✅ Actualizar dependencias vulnerables
10. ✅ Implementar monitoreo de seguridad

### 🟢 RECOMENDADO (Hacer este mes):
11. ✅ Implementar WAF (Web Application Firewall)
12. ✅ Configurar backups automáticos
13. ✅ Penetration testing
14. ✅ Documentación de seguridad
15. ✅ Training de seguridad para desarrolladores

---

## 🔧 HERRAMIENTAS RECOMENDADAS

```bash
# Análisis de seguridad
pip install bandit  # Análisis estático de seguridad
pip install safety  # Vulnerabilidades en dependencias
pip install django-csp  # Content Security Policy
pip install django-ratelimit  # Rate limiting
pip install python-magic  # Validación de archivos
pip install bleach  # Sanitización HTML

# Ejecutar análisis
bandit -r . -f json -o security_report.json
safety check --json
```

---

## 📚 RECURSOS Y REFERENCIAS

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## ✅ CHECKLIST DE SEGURIDAD

- [ ] Settings.py actualizado con configuraciones seguras
- [ ] Sesiones y cookies configuradas correctamente
- [ ] Headers de seguridad implementados
- [ ] Credenciales movidas a variables de entorno
- [ ] Validación y sanitización de inputs
- [ ] Rate limiting en endpoints críticos
- [ ] Logging de seguridad configurado
- [ ] Validación robusta de archivos
- [ ] HTTPS configurado en producción
- [ ] Backups configurados
- [ ] Monitoreo de seguridad activo
- [ ] Documentación actualizada
- [ ] Team training completado

---

**Próxima revisión:** 30 días
**Contacto de seguridad:** [security@tiendainmobiliaria.com]


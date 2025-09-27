# 📧 Configuración de Gmail SMTP para Recuperación de Contraseña

## 🔧 Pasos para Configurar Gmail SMTP

### 1. **Habilitar Verificación en 2 Pasos**
1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Selecciona **"Seguridad"** en el menú lateral
3. Busca **"Verificación en 2 pasos"** y actívala
4. Sigue las instrucciones para configurarla

### 2. **Generar Contraseña de Aplicación**
1. En la sección **"Seguridad"** de tu cuenta de Google
2. Busca **"Contraseñas de aplicaciones"**
3. Selecciona **"Aplicación"** → **"Correo"**
4. Selecciona **"Dispositivo"** → **"Otro (nombre personalizado)"**
5. Escribe: `Tienda Inmobiliaria`
6. Haz clic en **"Generar"**
7. **Copia la contraseña de 16 caracteres** que aparece

### 3. **Configurar settings.py**
Edita el archivo `tienda_meli/tienda_meli/settings.py` y actualiza estas líneas:

```python
# Configuración de Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'  # ← Cambia por tu email
EMAIL_HOST_PASSWORD = 'tu-app-password'  # ← Cambia por la contraseña de aplicación
DEFAULT_FROM_EMAIL = 'Tienda Inmobiliaria <tu-email@gmail.com>'  # ← Cambia por tu email
```

### 4. **Ejemplo de Configuración**
```python
EMAIL_HOST_USER = 'miguel.astorga@gmail.com'
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # Contraseña de aplicación
DEFAULT_FROM_EMAIL = 'Tienda Inmobiliaria <miguel.astorga@gmail.com>'
```

## 🚨 **Importante - Seguridad**

### ❌ **NO uses tu contraseña normal de Gmail**
- Usa **SOLO** la contraseña de aplicación de 16 caracteres
- La contraseña de aplicación es específica para esta aplicación
- Puedes revocarla en cualquier momento desde tu cuenta de Google

### ✅ **Buenas Prácticas**
- Guarda la contraseña de aplicación en un lugar seguro
- No la compartas con nadie
- Si sospechas que está comprometida, revócala y genera una nueva

## 🧪 **Probar la Configuración**

### 1. **Probar desde Django Shell**
```python
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Probar envío de email
send_mail(
    'Prueba de Email',
    'Este es un email de prueba.',
    settings.DEFAULT_FROM_EMAIL,
    ['tu-email@gmail.com'],
    fail_silently=False,
)
```

### 2. **Probar Recuperación de Contraseña**
1. Ve a: `http://127.0.0.1:8000/login/password-reset/`
2. Ingresa tu email de administrador
3. Revisa tu correo electrónico
4. Sigue el proceso de recuperación

## 🔍 **Solución de Problemas**

### Error: "Authentication failed"
- Verifica que la verificación en 2 pasos esté activada
- Usa la contraseña de aplicación, no tu contraseña normal
- Asegúrate de que el email sea correcto

### Error: "Connection refused"
- Verifica tu conexión a internet
- Asegúrate de que el puerto 587 no esté bloqueado
- Prueba con `EMAIL_USE_TLS = True`

### Error: "SMTPAuthenticationError"
- Regenera la contraseña de aplicación
- Espera unos minutos antes de probar de nuevo
- Verifica que el email esté correcto

## 📱 **Funcionalidades Implementadas**

### ✅ **Sistema Completo de Recuperación**
- [x] Formulario para solicitar recuperación
- [x] Generación de código de 6 dígitos
- [x] Envío por Gmail SMTP
- [x] Verificación de código
- [x] Cambio de contraseña
- [x] Redirección al login
- [x] Códigos con expiración (1 hora)
- [x] Códigos de un solo uso
- [x] Templates responsivos
- [x] Email HTML profesional

### 🎯 **URLs Disponibles**
- `/login/password-reset/` - Solicitar recuperación
- `/login/password-reset-verify/<email>/` - Verificar código

### 🔗 **Enlaces en el Login**
- "¿Olvidaste tu contraseña?" en la página de login
- Enlaces de navegación entre páginas

## 🎉 **¡Listo para Usar!**

Una vez configurado Gmail SMTP, el sistema de recuperación de contraseña estará completamente funcional y listo para usar en producción.

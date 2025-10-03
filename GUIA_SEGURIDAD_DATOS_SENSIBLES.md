# 🔒 GUÍA: Protección de Datos Sensibles

## ⚠️ PROBLEMA DETECTADO

Se encontraron **datos sensibles expuestos** en el código:
- ✅ Contraseña de Gmail
- ✅ Emails expuestos
- ✅ SECRET_KEY con default inseguro

**RIESGO:** Cualquiera con acceso al repositorio de GitHub puede ver estos datos.

---

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. **Settings.py Limpio**

Se eliminaron los valores por defecto inseguros:

```python
# ❌ ANTES (INSEGURO):
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='admgisa744@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='mame neak myug fcrv')

# ✅ AHORA (SEGURO):
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

### 2. **Archivo .env.example Creado**

Se creó un archivo `.env.example` con plantilla de variables.

### 3. **.gitignore Verificado**

El archivo `.env` YA está en `.gitignore` ✅

---

## 📋 PASOS A SEGUIR

### **PASO 1: Crear tu archivo .env LOCAL**

```bash
# En tu computadora (desarrollo)
cd C:\Users\MiguelAstorga\Desktop\Tienda-inmobiliaria
copy .env.example .env
```

Luego edita `.env` con tus datos reales.

### **PASO 2: Cambiar Contraseñas Comprometidas**

Como tu contraseña de Gmail fue expuesta en el código, DEBES cambiarla:

1. Ve a: https://myaccount.google.com/apppasswords
2. Elimina la contraseña antigua: `mame neak myug fcrv`
3. Genera una NUEVA contraseña de aplicación
4. Úsala en tu archivo `.env`

### **PASO 3: Limpiar Archivos de Documentación**

Los siguientes archivos tienen datos sensibles en ejemplos:
- `MIGRACION_MYSQL.md`
- `AUDITORIA_SEGURIDAD_OWASP.md`
- `PRODUCCION_MYSQL.md`

Reemplaza los datos reales por placeholders:
```
❌ admgisa744@gmail.com
✅ tu_email@gmail.com

❌ mame neak myug fcrv
✅ xxxx xxxx xxxx xxxx
```

---

## 🚀 PARA PRODUCCIÓN (Servidor)

### En el servidor VPS, crearás un .env diferente:

```bash
# En el servidor
cd ~/Tienda-inmobiliaria
nano .env
```

Contenido del .env en PRODUCCIÓN:

```env
SECRET_KEY=[genera una nueva]
DEBUG=False
ALLOWED_HOSTS=tudominio.com.ar,www.tudominio.com.ar

DB_ENGINE=django.db.backends.mysql
DB_NAME=tienda_inmobiliaria_prod
DB_USER=tienda_user
DB_PASSWORD=[tu password de MySQL del servidor]
DB_HOST=localhost
DB_PORT=3306

REDIS_URL=redis://127.0.0.1:6379/1

EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=[tu NUEVA password de aplicación]
ADMIN_EMAIL=tu_email@gmail.com

CSRF_TRUSTED_ORIGINS=https://tudominio.com.ar,https://www.tudominio.com.ar
```

---

## ✅ VERIFICACIÓN

Para verificar que no hay datos sensibles:

```bash
# Buscar posibles datos expuestos
git grep -i "password" | grep -v ".env"
git grep -i "@gmail.com" | grep -v ".env"
```

---

## 🔐 BUENAS PRÁCTICAS

1. ✅ **NUNCA** pongas datos sensibles en el código
2. ✅ **SIEMPRE** usa variables de entorno (.env)
3. ✅ **VERIFICA** que .env esté en .gitignore
4. ✅ **USA** .env.example como plantilla (sin datos reales)
5. ✅ **CAMBIA** contraseñas si fueron expuestas
6. ✅ **GENERA** SECRET_KEY diferentes para desarrollo y producción

---

## 🆘 SI TU REPOSITORIO ES PÚBLICO

Si tu repositorio de GitHub es **PÚBLICO** y tiene estos datos:

### Acción URGENTE:

1. **Cambia TODAS las contraseñas inmediatamente**
   - Gmail App Password
   - MySQL passwords
   - SECRET_KEY

2. **Limpia el historial de Git** (opcional pero recomendado):
   ```bash
   # ⚠️ CUIDADO: Esto reescribe el historial
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch tienda_meli/tienda_meli/settings.py" \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **Considera hacer el repositorio privado** si contiene lógica de negocio sensible

---

## 📚 RECURSOS

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Python Decouple Documentation](https://pypi.org/project/python-decouple/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)


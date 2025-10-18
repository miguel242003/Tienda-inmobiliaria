# 🔧 SOLUCIÓN: Email de CV no llega a Gmail

## 📋 **Problema Identificado**
El formulario de CV se envía correctamente al dashboard, pero no llegan los emails a Gmail porque **faltan las credenciales de email configuradas**.

## ✅ **Solución Paso a Paso**

### **1. Crear archivo .env**
```bash
# Copia el archivo de ejemplo
cp env.example .env
```

### **2. Configurar credenciales de Gmail**

Edita el archivo `.env` y completa estas variables:

```env
# Tu email de Gmail
EMAIL_HOST_USER=tu_email_real@gmail.com

# Contraseña de aplicación de Gmail (NO tu contraseña normal)
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx

# Email donde quieres recibir las notificaciones de CV
ADMIN_EMAIL=tu_email_real@gmail.com
```

### **3. Generar Contraseña de Aplicación en Gmail**

1. **Ve a**: https://myaccount.google.com/apppasswords
2. **Selecciona**: "Aplicación" → "Correo"
3. **Copia** la contraseña generada (formato: `xxxx xxxx xxxx xxxx`)
4. **Pega** esta contraseña en `EMAIL_HOST_PASSWORD` en el archivo `.env`

### **4. Verificar configuración**

Ejecuta el script de prueba:
```bash
python test_email_config.py
```

### **5. Probar envío de CV**

1. Ve a `/cv/` en tu sitio
2. Completa y envía el formulario
3. Verifica que lleguen los emails:
   - **Email de confirmación** al candidato
   - **Email de notificación** al administrador

## 🔍 **Verificación de Logs**

Si sigue sin funcionar, revisa los logs:
```bash
# Ver logs de Django
tail -f logs/django.log

# Ver logs de seguridad
tail -f logs/security.log
```

## 🚨 **Problemas Comunes**

### **Error: "Authentication failed"**
- ✅ Verifica que `EMAIL_HOST_PASSWORD` sea una contraseña de aplicación
- ✅ NO uses tu contraseña normal de Gmail

### **Error: "Connection refused"**
- ✅ Verifica que `EMAIL_HOST_USER` sea tu email real de Gmail
- ✅ Verifica que tengas conexión a internet

### **Error: "Invalid credentials"**
- ✅ Regenera la contraseña de aplicación en Gmail
- ✅ Copia exactamente la contraseña generada

## 📧 **Configuración Final**

Tu archivo `.env` debe verse así:
```env
EMAIL_HOST_USER=miempresa@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
ADMIN_EMAIL=miempresa@gmail.com
```

## ✅ **Resultado Esperado**

Después de configurar correctamente:
- ✅ El formulario se envía al dashboard
- ✅ El candidato recibe email de confirmación
- ✅ El administrador recibe email de notificación
- ✅ Los emails llegan a Gmail correctamente

---
**Nota**: El archivo `.env` NO debe subirse a GitHub (ya está en .gitignore)

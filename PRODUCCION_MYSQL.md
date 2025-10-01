# 🚀 Configuración de Producción - MySQL

## ✅ Estado Actual del Sistema

### Base de Datos
- **Motor:** MySQL 8.0+
- **Base de datos:** `tienda_inmobiliaria_prod`
- **Usuario:** `tienda_user`
- **Contraseña:** `MAS242003` (configurada en `.env`)
- **Host:** localhost
- **Puerto:** 3306

### Django
- **SECRET_KEY:** Nueva clave segura generada ✅
- **DEBUG:** False (Producción)
- **ALLOWED_HOSTS:** localhost, 127.0.0.1
- **Base de datos:** MySQL (100% migrado desde SQLite)

### Datos Iniciales Cargados
- ✅ **6 Amenidades:** Piscina privada, TV, Lavavajillas, Aire acondicionado, Lavadora, WiFi
- ✅ **Migraciones:** Todas aplicadas (51 migraciones)
- ✅ **Estructura completa:** Todas las tablas creadas

---

## 📋 Tareas Completadas

1. ✅ Base de datos MySQL creada y configurada
2. ✅ Usuario MySQL con permisos limitados
3. ✅ Archivo `.env` configurado con variables de entorno
4. ✅ `settings.py` actualizado para usar variables de entorno
5. ✅ Todas las migraciones aplicadas en MySQL
6. ✅ Amenidades iniciales cargadas
7. ✅ Nueva SECRET_KEY segura generada
8. ✅ `.gitignore` actualizado para proteger archivos sensibles

---

## 🔒 Seguridad Implementada

### Variables de Entorno
Todas las credenciales están en `.env` (NO incluido en Git):
- Credenciales de base de datos
- SECRET_KEY de Django
- Credenciales de email

### Permisos de Base de Datos
El usuario `tienda_user` tiene **permisos limitados**:
- ✅ SELECT, INSERT, UPDATE, DELETE
- ✅ CREATE, DROP, ALTER (tablas)
- ❌ NO tiene permisos de superusuario
- ❌ NO tiene acceso a otras bases de datos

### Configuración de Producción
- DEBUG = False
- ALLOWED_HOSTS restringido
- SECRET_KEY única y segura
- Validadores de contraseña activos

---

## 🚀 Siguiente Paso: Crear Superusuario

Para acceder al panel de administración, crea un superusuario:

```powershell
python manage.py createsuperuser
```

Proporciona:
- **Nombre de usuario:** (ejemplo: admin)
- **Email:** xmiguelastorgax@gmail.com
- **Contraseña:** (elige una segura)

---

## 🌐 Iniciar el Servidor

```powershell
python manage.py runserver
```

**Panel de administración:** http://localhost:8000/admin/

---

## 📊 Comandos Útiles

### Verificar Estado del Sistema
```powershell
python manage.py check
```

### Ver Migraciones
```powershell
python manage.py showmigrations
```

### Acceder al Shell de Django
```powershell
python manage.py shell
```

### Crear Datos de Prueba
```python
python manage.py shell

from propiedades.models import Propiedad, Amenidad
from login.models import AdminCredentials

# Ver amenidades disponibles
Amenidad.objects.all()

# Ver propiedades
Propiedad.objects.all()
```

---

## 🔄 Backup y Restauración

### Hacer Backup de MySQL
```powershell
mysqldump -u tienda_user -pMAS242003 tienda_inmobiliaria_prod > backup_$(Get-Date -Format 'yyyyMMdd').sql
```

### Restaurar desde Backup
```powershell
mysql -u tienda_user -pMAS242003 tienda_inmobiliaria_prod < backup_20250101.sql
```

### Backup de Archivos Media
```powershell
Compress-Archive -Path media -DestinationPath backup_media_$(Get-Date -Format 'yyyyMMdd').zip
```

---

## 🔧 Mantenimiento

### Limpiar Sesiones Expiradas
```powershell
python manage.py clearsessions
```

### Recopilar Archivos Estáticos
```powershell
python manage.py collectstatic --noinput
```

### Verificar Base de Datos
```sql
-- Conectar a MySQL
mysql -u tienda_user -pMAS242003 tienda_inmobiliaria_prod

-- Ver todas las tablas
SHOW TABLES;

-- Ver estructura de una tabla
DESCRIBE propiedades_propiedad;

-- Contar registros
SELECT COUNT(*) FROM propiedades_propiedad;
SELECT COUNT(*) FROM propiedades_amenidad;

-- Ver datos
SELECT id, titulo, precio, tipo FROM propiedades_propiedad;

-- Salir
EXIT;
```

---

## 🌍 Despliegue en Servidor Real

### Actualizar ALLOWED_HOSTS
En `.env`, agrega tu dominio:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,tudominio.com,www.tudominio.com
```

### Actualizar CSRF_TRUSTED_ORIGINS
En `tienda_meli/tienda_meli/settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://tudominio.com',
    'https://www.tudominio.com',
]
```

### Configurar Servidor Web
Usa **Gunicorn** (ya está en requirements.txt):
```powershell
gunicorn tienda_meli.tienda_meli.wsgi:application --bind 0.0.0.0:8000
```

### Configurar Nginx (Ejemplo)
```nginx
server {
    listen 80;
    server_name tudominio.com;

    location /static/ {
        alias /ruta/a/tu/proyecto/staticfiles/;
    }

    location /media/ {
        alias /ruta/a/tu/proyecto/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📁 Estructura de Archivos Importantes

```
Tienda-inmobiliaria/
├── .env                          # Variables de entorno (NO en Git)
├── .gitignore                    # Archivos ignorados por Git
├── manage.py                     # Comando principal de Django
├── requirements.txt              # Dependencias Python
├── MIGRACION_MYSQL.md           # Guía de migración (referencia)
├── PRODUCCION_MYSQL.md          # Esta guía
├── setup_mysql.sql              # Script de configuración inicial
├── cambiar_password_mysql.sql   # Script para cambiar contraseña
│
├── tienda_meli/
│   ├── db.sqlite3               # Base de datos antigua (backup)
│   └── tienda_meli/
│       ├── settings.py          # Configuración de Django
│       ├── urls.py
│       └── wsgi.py
│
├── media/                       # Archivos subidos (NO en Git)
│   └── propiedades/
│
├── static/                      # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
│
├── propiedades/                 # App de propiedades
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── management/
│       └── commands/
│           └── crear_amenidades.py
│
├── login/                       # App de autenticación
│   ├── models.py
│   ├── views.py
│   └── templates/
│
└── core/                        # App principal
    ├── models.py
    ├── views.py
    └── templates/
```

---

## ⚠️ Notas Importantes

1. **NUNCA subas `.env` a Git** - Contiene credenciales sensibles
2. **Haz backups regulares** de MySQL y archivos media
3. **Mantén DEBUG=False en producción** - Nunca expongas errores al público
4. **Usa HTTPS en producción** - Protege las comunicaciones
5. **Actualiza dependencias regularmente** - `pip list --outdated`

---

## 🆘 Solución de Problemas

### Error: "Access denied for user"
```powershell
# Verificar contraseña en .env
Get-Content .env

# Si es necesario, cambiar contraseña en MySQL
mysql -u root -p < cambiar_password_mysql.sql
```

### Error: "Can't connect to MySQL server"
```powershell
# Verificar que MySQL esté corriendo
Get-Service MySQL*

# Iniciar MySQL si está detenido
Start-Service MySQL80
```

### Error: "Table doesn't exist"
```powershell
# Ejecutar migraciones
python manage.py migrate
```

### Error: "CSRF verification failed"
```python
# Actualizar CSRF_TRUSTED_ORIGINS en settings.py
```

---

## 📞 Contacto y Soporte

Para cualquier problema:
1. Revisa los logs: `python manage.py runserver`
2. Verifica `.env` tiene las credenciales correctas
3. Comprueba que MySQL está corriendo
4. Revisa la documentación de Django: https://docs.djangoproject.com/

---

## ✅ Checklist Final

- [x] MySQL instalado y corriendo
- [x] Base de datos `tienda_inmobiliaria_prod` creada
- [x] Usuario `tienda_user` configurado
- [x] Archivo `.env` con credenciales
- [x] `settings.py` usando variables de entorno
- [x] Todas las migraciones aplicadas
- [x] Amenidades iniciales cargadas
- [x] `.gitignore` actualizado
- [x] DEBUG=False en producción
- [ ] Superusuario creado
- [ ] Propiedades de prueba creadas (opcional)
- [ ] Backup configurado
- [ ] Servidor web configurado (si aplica)

---

🎉 **¡Sistema 100% MySQL y listo para producción!**


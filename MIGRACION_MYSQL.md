# 🚀 Guía de Migración a MySQL - Tienda Inmobiliaria

Esta guía te llevará paso a paso por el proceso de migración de SQLite a MySQL para tu base de datos de producción.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
- ✅ MySQL Server 8.0 o superior
- ✅ Python 3.x con pip
- ✅ Todas las dependencias del proyecto (`pip install -r requirements.txt`)

---

## 🔧 PASO 1: Instalar MySQL Server

### Windows:
1. Descarga MySQL desde: https://dev.mysql.com/downloads/installer/
2. Instala MySQL Server y MySQL Workbench
3. Durante la instalación, configura la contraseña del usuario `root`
4. Asegúrate de que el servicio MySQL esté corriendo

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql_secure_installation
```

### macOS:
```bash
brew install mysql
brew services start mysql
```

---

## 🗄️ PASO 2: Crear la Base de Datos y Usuario

### Opción A: Usando el script SQL (Recomendado)

1. **Edita el archivo `setup_mysql.sql`** y cambia `'tu_contraseña_segura'` por una contraseña fuerte

2. **Ejecuta el script desde la terminal:**

```bash
# Windows (PowerShell o CMD)
mysql -u root -p < setup_mysql.sql

# Linux/macOS
mysql -u root -p < setup_mysql.sql
```

3. Ingresa la contraseña de `root` cuando te la pida

### Opción B: Manualmente desde MySQL

```bash
# Conectarse a MySQL
mysql -u root -p

# Una vez dentro, ejecutar:
```

```sql
CREATE DATABASE tienda_inmobiliaria_prod
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER 'tienda_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, 
      REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE
ON tienda_inmobiliaria_prod.* 
TO 'tienda_user'@'localhost';

FLUSH PRIVILEGES;
EXIT;
```

---

## 🔐 PASO 3: Configurar Variables de Entorno

1. **Crea un archivo `.env`** en la raíz del proyecto (al lado de `manage.py`):

```bash
# Windows PowerShell
New-Item -Path ".env" -ItemType File

# Linux/macOS
touch .env
```

2. **Edita el archivo `.env`** con la siguiente configuración:

```env
# CONFIGURACIÓN DE BASE DE DATOS
DB_ENGINE=django.db.backends.mysql
DB_NAME=tienda_inmobiliaria_prod
DB_USER=tienda_user
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_PORT=3306

# DJANGO
SECRET_KEY=genera_una_clave_secreta_nueva_aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# EMAIL (opcional)
EMAIL_HOST_USER=xmiguelastorgax@gmail.com
EMAIL_HOST_PASSWORD=gsam eenf yjvg bzeu
```

3. **⚠️ IMPORTANTE:** Cambia:
   - `DB_PASSWORD` por la contraseña que creaste para `tienda_user`
   - `SECRET_KEY` por una nueva clave secreta (puedes generarla con: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `ALLOWED_HOSTS` por los dominios donde se ejecutará tu aplicación

4. **Verifica que `.env` esté en tu `.gitignore`** para no subir las contraseñas a Git

---

## 🔄 PASO 4: Ejecutar Migraciones

Ahora Django usará MySQL automáticamente:

```bash
# Navegar al directorio con manage.py
cd tienda_meli

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate
```

Si todo está bien, verás algo como:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, login, propiedades, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

## 👤 PASO 5: Crear Superusuario

```bash
python manage.py createsuperuser
```

Ingresa:
- **Usuario:** (ejemplo: admin)
- **Email:** tu_email@ejemplo.com
- **Contraseña:** (elige una contraseña segura)

---

## 🏠 PASO 6: Cargar Datos Iniciales

### Crear Amenidades Iniciales:

```bash
python manage.py crear_amenidades_iniciales
```

Esto creará las amenidades predeterminadas (Piscina, WiFi, Aire acondicionado, etc.)

### (Opcional) Migrar datos de SQLite a MySQL:

Si tienes datos en SQLite que quieres transferir:

```bash
# Exportar datos de SQLite
python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission > backup.json

# Cambiar a MySQL en .env (DB_ENGINE=django.db.backends.mysql)

# Importar datos a MySQL
python manage.py loaddata backup.json
```

---

## ✅ PASO 7: Verificar la Configuración

### Probar la conexión:

```bash
python manage.py check
```

### Iniciar el servidor:

```bash
python manage.py runserver
```

### Acceder al admin:

1. Ve a: http://localhost:8000/admin/
2. Inicia sesión con el superusuario que creaste
3. Verifica que puedas ver y crear propiedades

---

## 🔍 Verificación de Tabla de Datos

Puedes verificar que las tablas se crearon correctamente:

```bash
mysql -u tienda_user -p tienda_inmobiliaria_prod
```

```sql
-- Ver todas las tablas
SHOW TABLES;

-- Ver estructura de una tabla
DESCRIBE propiedades_propiedad;

-- Contar registros
SELECT COUNT(*) FROM propiedades_propiedad;

EXIT;
```

---

## 🚨 Solución de Problemas

### Error: "Access denied for user"
- Verifica que la contraseña en `.env` sea correcta
- Asegúrate de haber ejecutado `FLUSH PRIVILEGES;` en MySQL

### Error: "Unknown database"
- Verifica que la base de datos `tienda_inmobiliaria_prod` exista:
  ```sql
  SHOW DATABASES;
  ```

### Error: "Can't connect to MySQL server"
- Verifica que MySQL esté corriendo:
  ```bash
  # Windows
  Get-Service MySQL*
  
  # Linux
  sudo systemctl status mysql
  ```

### Error de módulo PyMySQL
- Reinstala pymysql:
  ```bash
  pip install pymysql
  ```

---

## 🔄 Volver a SQLite (Desarrollo)

Si necesitas volver a SQLite para desarrollo local:

1. Edita tu `.env`:
   ```env
   DB_ENGINE=django.db.backends.sqlite3
   DEBUG=True
   ```

2. El proyecto usará automáticamente SQLite

---

## 📊 Resumen de Checklist

- [ ] MySQL Server instalado y corriendo
- [ ] Base de datos `tienda_inmobiliaria_prod` creada
- [ ] Usuario `tienda_user` creado con permisos
- [ ] Archivo `.env` configurado con las credenciales correctas
- [ ] Migraciones ejecutadas (`python manage.py migrate`)
- [ ] Superusuario creado (`python manage.py createsuperuser`)
- [ ] Amenidades iniciales cargadas
- [ ] Servidor Django funciona correctamente
- [ ] Puedes acceder al panel de admin

---

## 📞 Notas Finales

- **Nunca subas el archivo `.env` a Git** - Contiene información sensible
- **Usa contraseñas fuertes** para la base de datos y el superusuario
- **En producción, configura `DEBUG=False`** en el `.env`
- **Realiza backups regulares** de tu base de datos MySQL

---

## 💾 Backup de Base de Datos

Para hacer backups periódicos:

```bash
# Exportar base de datos
mysqldump -u tienda_user -p tienda_inmobiliaria_prod > backup_$(date +%Y%m%d).sql

# Restaurar desde backup
mysql -u tienda_user -p tienda_inmobiliaria_prod < backup_20250101.sql
```

---

¡Listo! Tu proyecto ahora está configurado con MySQL de manera profesional y segura. 🎉


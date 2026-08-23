# 🏠 Tienda Inmobiliaria - Catálogo de Lujo

![Django](https://img.shields.io/badge/Django-5.2.1-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)

## ✨ Descripción

Sitio web inmobiliario de lujo desarrollado con Django, que presenta un catálogo elegante de propiedades destacadas con diseño zig-zag y estilo premium. El proyecto incluye un sistema completo de gestión de propiedades, panel administrativo y diseño responsivo.

## 🎯 Características Principales

### 🏗️ **Frontend Premium**
- **Diseño Zig-Zag**: Layout alternado para propiedades destacadas
- **Tipografías de Lujo**: Oswald para títulos, Inter para texto
- **Paleta de Colores Premium**: Grises elegantes y azules corporativos
- **Responsive Design**: Adaptable a todos los dispositivos

### 🏠 **Gestión de Propiedades**
- Catálogo de propiedades destacadas
- Sistema de búsqueda y filtros
- Galería de imágenes con zoom
- Información detallada de cada propiedad

### 🔐 **Panel Administrativo**
- Login seguro para administradores con autenticación de dos factores (TOTP + códigos de respaldo)
- CRUD completo de propiedades
- Gestión de imágenes y contenido
- Dashboard de estadísticas

### 🛡️ **Seguridad Backend**
- Hash de contraseñas con Argon2
- Rate limiting en formularios públicos y login
- Content Security Policy (django-csp)
- Validación real del tipo de archivo en uploads (python-magic), no solo por extensión
- Verificación server-side de Cloudflare Turnstile / reCAPTCHA v3 en formularios públicos
- Variables sensibles (SECRET_KEY, credenciales de BD y email) fuera del código, vía `.env`

### 🎨 **Componentes Visuales**
- Hero carousel con imágenes de alta calidad
- Sección de estadísticas animadas
- Tipos de propiedades disponibles
- Servicios inmobiliarios destacados

## 🚀 Tecnologías Utilizadas

- **Backend**: Django 5.2.1
- **Base de Datos**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework CSS**: Bootstrap 5.3.0
- **Iconos**: Font Awesome 6.4.0
- **Fuentes**: Google Fonts (Oswald, Inter)
- **Imágenes**: Pillow para procesamiento

## 📁 Estructura del Proyecto

```
Tienda_inmobiliaria/
├── core/                    # App principal
│   ├── templates/          # Templates base y home
│   ├── views.py           # Vistas principales
│   └── urls.py            # URLs principales
├── propiedades/            # App de propiedades
│   ├── models.py          # Modelo Propiedad
│   ├── views.py           # Vistas de propiedades
│   └── templates/         # Templates de propiedades
├── login/                  # App de autenticación
│   ├── views.py           # Vistas de login
│   └── templates/         # Templates de admin
├── static/                 # Archivos estáticos
│   ├── css/               # Estilos CSS
│   ├── js/                # JavaScript
│   └── images/            # Imágenes del sitio
├── media/                  # Archivos subidos por usuarios
└── tienda_meli/           # Configuración Django
    ├── settings.py        # Configuraciones del proyecto
    └── urls.py            # URLs principales
```

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- pip (gestor de paquetes Python)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/miguel242003/Tienda-inmobiliaria.git
cd Tienda-inmobiliaria
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos
```bash
# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE tienda_inmobiliaria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
DB_NAME=tienda_inmobiliaria
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
```

### 6. Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 8. Ejecutar el Servidor
```bash
python manage.py runserver
```

## 🧪 Tests

```bash
python manage.py test
```

Cubren autogeneración de slugs, formato de precio, aprobación de reseñas, hash de contraseñas de administrador, control de acceso al dashboard y páginas públicas principales.

## 🌐 Acceso al Sitio

- **Sitio Principal**: http://localhost:8000/
- **Panel Admin**: http://localhost:8000/login/admin/
- **Propiedades**: http://localhost:8000/propiedades/

## 📱 Características Responsivas

- **Desktop**: Layout completo con zig-zag
- **Tablet**: Adaptación a pantallas medianas
- **Mobile**: Diseño en columna para mejor usabilidad

## 🎨 Personalización

### Colores Principales
```css
:root {
    --bg: #F0F0F0;        /* Fondo sección */
    --ink: #2C3240;       /* Títulos y negritas */
    --muted: #6B717C;     /* Párrafos */
    --accent: #6A8ED0;    /* Precio */
}
```

### Tipografías
- **Títulos**: Oswald (Bold, 700)
- **Texto**: Inter (Regular, 400; Semi-bold, 600)

## 📊 Funcionalidades del Admin

- ✅ Gestión completa de propiedades
- ✅ Subida de imágenes
- ✅ Edición de contenido
- ✅ Estadísticas del sitio
- ✅ Gestión de usuarios

## 🔒 Seguridad

- Autenticación segura para administradores
- Validación de formularios
- Protección CSRF
- Manejo seguro de archivos

## 🚀 Despliegue

### Heroku
```bash
# Crear Procfile
echo "web: gunicorn tienda_meli.wsgi" > Procfile

# Instalar gunicorn
pip install gunicorn

# Configurar variables de entorno en Heroku
heroku config:set SECRET_KEY=tu_clave_secreta
heroku config:set DEBUG=False
```

### VPS/Dedicado
```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-server

# Configurar Gunicorn + Nginx
# (Ver documentación completa en docs/)
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Miguel Astorga**
- GitHub: [@miguel242003](https://github.com/miguel242003)

## 🙏 Agradecimientos

- Django Software Foundation
- Bootstrap Team
- Font Awesome
- Google Fonts
- Comunidad de desarrolladores Python

---

⭐ **Si te gusta este proyecto, ¡dale una estrella en GitHub!** ⭐

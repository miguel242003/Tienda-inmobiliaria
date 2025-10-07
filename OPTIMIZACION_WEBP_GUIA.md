# 🚀 Guía de Optimización WebP - Tienda Inmobiliaria

## 📋 Resumen

Esta implementación optimiza automáticamente todas las imágenes de tu sitio web al formato WebP, mejorando significativamente la velocidad de carga sin afectar la compatibilidad.

## ✨ Características Implementadas

### 🔧 Funcionalidades Principales
- **Conversión automática**: Las imágenes se convierten automáticamente a WebP al subirlas
- **Compatibilidad total**: Fallback automático a formatos originales para navegadores que no soporten WebP
- **Optimización inteligente**: Calidad 85% por defecto (configurable)
- **Redimensionamiento**: Máximo 2048px para evitar archivos excesivamente grandes
- **Migración masiva**: Comando para optimizar todas las imágenes existentes

### 🎯 Beneficios
- **Velocidad**: 25-50% menos tamaño de archivo
- **SEO**: Mejor Core Web Vitals
- **UX**: Carga más rápida de imágenes
- **Compatibilidad**: Funciona en todos los navegadores
- **Mantenimiento**: Automático, sin intervención manual

## 🛠️ Instalación

### 1. Instalar Dependencias
```bash
python install_webp_dependencies.py
```

### 2. Ejecutar Migraciones
```bash
python manage.py migrate
```

### 3. Optimizar Imágenes Existentes
```bash
# Optimizar todas las imágenes
python manage.py optimize_images

# Solo propiedades
python manage.py optimize_images --model propiedades

# Solo fotos de propiedades
python manage.py optimize_images --model fotos

# Solo fotos de perfil de admin
python manage.py optimize_images --model admin

# Con calidad personalizada
python manage.py optimize_images --quality 90

# Simulación (sin cambios reales)
python manage.py optimize_images --dry-run
```

## 📁 Archivos Creados/Modificados

### 🆕 Nuevos Archivos
- `core/image_optimizer.py` - Motor de optimización WebP
- `core/fields.py` - Campos personalizados para WebP
- `core/templatetags/webp_tags.py` - Template tags para WebP
- `core/management/commands/optimize_images.py` - Comando de migración
- `install_webp_dependencies.py` - Script de instalación

### 🔄 Archivos Modificados
- `propiedades/models.py` - Agregado WebPImageFieldMixin
- `login/models.py` - Agregado WebPImageFieldMixin
- Templates actualizados para usar WebP:
  - `propiedades/templates/propiedades/detalle_propiedad.html`
  - `propiedades/templates/propiedades/buscar_propiedades.html`
  - `propiedades/templates/propiedades/buscar_propiedades-optimized.html`
  - `propiedades/templates/propiedades/crear_resena.html`
  - `core/templates/core/home.html`

## 🎨 Uso en Templates

### Template Tag Básico
```django
{% load webp_tags %}

<!-- Imagen simple con WebP -->
{% webp_picture propiedad.imagen_principal "Título de la propiedad" "clase-css" True %}
```

### Template Tag Avanzado
```django
<!-- Con lazy loading y placeholder -->
{% webp_lazy_picture propiedad.imagen_principal "Título" "clase-css" "/static/placeholder.jpg" %}

<!-- Con srcset responsivo -->
{% webp_srcset propiedad.imagen_principal %}
```

### Filtros Disponibles
```django
<!-- Verificar si existe WebP -->
{% if propiedad.imagen_principal|has_webp %}
    <p>✅ Imagen optimizada disponible</p>
{% endif %}

<!-- Obtener URL WebP -->
<img src="{{ propiedad.imagen_principal|webp_url }}" alt="Imagen WebP">
```

## ⚙️ Configuración Avanzada

### Calidad de Compresión
```python
# En settings.py
WEBP_QUALITY = 85  # 1-100, por defecto 85
WEBP_MAX_DIMENSION = 2048  # Máximo en píxeles
```

### Campos Personalizados
```python
from core.fields import WebPImageField

class MiModelo(models.Model):
    imagen = WebPImageField(
        upload_to='imagenes/',
        webp_quality=90,  # Calidad personalizada
        auto_optimize=True,  # Optimización automática
        preserve_original=True  # Mantener original
    )
```

## 📊 Comandos de Gestión

### Optimización Manual
```bash
# Optimizar todas las imágenes
python manage.py optimize_images

# Con opciones específicas
python manage.py optimize_images \
    --quality 90 \
    --model propiedades \
    --batch-size 20 \
    --force
```

### Parámetros del Comando
- `--quality`: Calidad de compresión (1-100)
- `--dry-run`: Simulación sin cambios
- `--model`: Modelo específico (propiedades|fotos|admin|all)
- `--force`: Re-optimizar imágenes ya optimizadas
- `--batch-size`: Tamaño del lote de procesamiento

## 🔍 Monitoreo y Estadísticas

### Verificar Estado de Optimización
```django
<!-- En templates -->
{% webp_optimize_status propiedad.imagen_principal %}
```

### Estadísticas del Comando
El comando `optimize_images` muestra:
- Total de imágenes procesadas
- Imágenes exitosas vs errores
- Espacio ahorrado en bytes y porcentaje
- Tiempo de procesamiento

## 🚨 Solución de Problemas

### Error: "Pillow no está instalado"
```bash
pip install Pillow>=10.0.0
```

### Error: "No se puede convertir imagen"
- Verificar que la imagen no esté corrupta
- Comprobar permisos de escritura en media/
- Revisar logs de Django para errores específicos

### Imágenes no se optimizan automáticamente
- Verificar que los modelos hereden de `WebPImageFieldMixin`
- Comprobar que `auto_optimize=True` en los campos
- Revisar configuración de `MEDIA_ROOT` y `MEDIA_URL`

### WebP no se muestra en navegador
- Verificar que el archivo WebP existe en el sistema de archivos
- Comprobar configuración de servidor web (nginx/apache)
- Revisar headers MIME types

## 🔧 Configuración del Servidor

### Nginx
```nginx
# Agregar soporte para WebP
location ~* \.(webp)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary Accept;
}

# Servir WebP cuando el navegador lo soporte
location ~* \.(jpg|jpeg|png)$ {
    add_header Vary Accept;
    try_files $uri$webp_suffix $uri =404;
}
```

### Apache
```apache
# Habilitar módulo rewrite
RewriteEngine On

# Servir WebP si existe y el navegador lo soporta
RewriteCond %{HTTP_ACCEPT} image/webp
RewriteCond %{REQUEST_FILENAME} \.(jpe?g|png)$
RewriteCond %{REQUEST_FILENAME}.webp -f
RewriteRule ^(.+)\.(jpe?g|png)$ $1.$2.webp [T=image/webp,E=accept:1]
```

## 📈 Rendimiento Esperado

### Ahorro de Espacio
- **JPEG**: 25-35% de reducción
- **PNG**: 20-30% de reducción
- **BMP**: 50-70% de reducción

### Mejoras en Core Web Vitals
- **LCP (Largest Contentful Paint)**: Mejora del 15-25%
- **CLS (Cumulative Layout Shift)**: Sin impacto negativo
- **FID (First Input Delay)**: Mejora del 10-15%

## 🎯 Próximos Pasos

1. **Ejecutar migración**: `python manage.py optimize_images`
2. **Verificar funcionamiento**: Revisar que las imágenes se muestren correctamente
3. **Monitorear rendimiento**: Usar herramientas como PageSpeed Insights
4. **Configurar servidor**: Implementar reglas de servidor web para WebP
5. **Backup**: Hacer respaldo antes de cambios en producción

## 🆘 Soporte

Si encuentras problemas:
1. Revisar logs de Django: `tail -f logs/django.log`
2. Verificar permisos de archivos
3. Comprobar configuración de MEDIA_ROOT
4. Ejecutar comando con `--dry-run` para diagnóstico

---

**¡Tu sitio web ahora está optimizado para WebP! 🚀**

Las imágenes se cargarán más rápido, mejorando la experiencia del usuario y el SEO de tu sitio inmobiliario.

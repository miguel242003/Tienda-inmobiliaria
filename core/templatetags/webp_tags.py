"""
Template tags para manejo de imágenes WebP
"""

from django import template
from django.utils.safestring import mark_safe
from django.core.files.storage import default_storage
from core.image_optimizer import WebPOptimizer

register = template.Library()

@register.simple_tag
def webp_picture(image_field, alt_text="", css_class="", lazy_loading=True, width=None, height=None):
    """
    Genera una etiqueta <picture> con soporte WebP y fallback
    
    Args:
        image_field: Campo de imagen del modelo
        alt_text: Texto alternativo
        css_class: Clases CSS
        lazy_loading: Si habilitar lazy loading
        width: Ancho de la imagen
        height: Alto de la imagen
    
    Returns:
        HTML con <picture> y <source>
    """
    if not image_field:
        return ""
    
    # Obtener URLs
    original_url = image_field.url
    webp_path = WebPOptimizer.get_webp_path(image_field.name)
    webp_url = None
    
    if webp_path and default_storage.exists(webp_path):
        webp_url = default_storage.url(webp_path)
    
    # Construir atributos de la imagen
    img_attrs = [f'alt="{alt_text}"']
    
    if css_class:
        img_attrs.append(f'class="{css_class}"')
    
    if lazy_loading:
        img_attrs.append('loading="lazy"')
    
    if width:
        img_attrs.append(f'width="{width}"')
    
    if height:
        img_attrs.append(f'height="{height}"')
    
    img_attrs_str = ' '.join(img_attrs)
    
    # Si no hay WebP, usar imagen original simple
    if not webp_url:
        return mark_safe(f'<img src="{original_url}" {img_attrs_str}>')
    
    # Generar HTML con <picture> y <source>
    html = f'''
    <picture>
        <source srcset="{webp_url}" type="image/webp">
        <img src="{original_url}" {img_attrs_str}>
    </picture>
    '''
    
    return mark_safe(html.strip())

@register.simple_tag
def webp_srcset(image_field, sizes=None):
    """
    Genera srcset para imágenes responsivas con WebP
    
    Args:
        image_field: Campo de imagen del modelo
        sizes: Lista de tuplas (width, url) para diferentes tamaños
    
    Returns:
        String con srcset para WebP y fallback
    """
    if not image_field:
        return ""
    
    if not sizes:
        # Tamaños por defecto
        sizes = [
            (320, 0.8),
            (640, 0.8),
            (1024, 0.8),
            (1920, 0.8)
        ]
    
    webp_srcset = []
    original_srcset = []
    
    for width, quality in sizes:
        # Para cada tamaño, generar URLs WebP y original
        webp_path = WebPOptimizer.get_webp_path(image_field.name)
        if webp_path and default_storage.exists(webp_path):
            webp_url = default_storage.url(webp_path)
            webp_srcset.append(f"{webp_url} {width}w")
        
        original_srcset.append(f"{image_field.url} {width}w")
    
    if webp_srcset:
        return mark_safe(f'''
        <source srcset="{', '.join(webp_srcset)}" type="image/webp" sizes="(max-width: 320px) 320px, (max-width: 640px) 640px, (max-width: 1024px) 1024px, 1920px">
        <source srcset="{', '.join(original_srcset)}" sizes="(max-width: 320px) 320px, (max-width: 640px) 640px, (max-width: 1024px) 1024px, 1920px">
        ''')
    
    return mark_safe(f'<source srcset="{', '.join(original_srcset)}" sizes="(max-width: 320px) 320px, (max-width: 640px) 640px, (max-width: 1024px) 1024px, 1920px">')

@register.simple_tag
def webp_optimize_status(image_field):
    """
    Muestra el estado de optimización de una imagen
    
    Args:
        image_field: Campo de imagen del modelo
    
    Returns:
        String con información de optimización
    """
    if not image_field:
        return "Sin imagen"
    
    webp_path = WebPOptimizer.get_webp_path(image_field.name)
    has_webp = webp_path and default_storage.exists(webp_path)
    
    if has_webp:
        try:
            original_size = image_field.size
            webp_size = default_storage.size(webp_path)
            saved_percentage = ((original_size - webp_size) / original_size * 100) if original_size > 0 else 0
            
            return f"✅ Optimizada (WebP: {webp_size:,} bytes, Original: {original_size:,} bytes, Ahorro: {saved_percentage:.1f}%)"
        except:
            return "✅ Optimizada (WebP disponible)"
    else:
        return "⚠️ No optimizada"

@register.filter
def webp_url(image_field):
    """
    Filtro para obtener la URL WebP de una imagen
    
    Args:
        image_field: Campo de imagen del modelo
    
    Returns:
        URL de la imagen WebP o None
    """
    if not image_field:
        return None
    
    webp_path = WebPOptimizer.get_webp_path(image_field.name)
    if webp_path and default_storage.exists(webp_path):
        return default_storage.url(webp_path)
    
    return None

@register.filter
def has_webp(image_field):
    """
    Filtro para verificar si existe versión WebP
    
    Args:
        image_field: Campo de imagen del modelo
    
    Returns:
        Boolean indicando si existe WebP
    """
    if not image_field:
        return False
    
    webp_path = WebPOptimizer.get_webp_path(image_field.name)
    return webp_path and default_storage.exists(webp_path)

@register.simple_tag
def webp_lazy_picture(image_field, alt_text="", css_class="", placeholder_url=None):
    """
    Genera una etiqueta <picture> con lazy loading y placeholder
    
    Args:
        image_field: Campo de imagen del modelo
        alt_text: Texto alternativo
        css_class: Clases CSS
        placeholder_url: URL de imagen placeholder (opcional)
    
    Returns:
        HTML con <picture> y lazy loading
    """
    if not image_field:
        return ""
    
    # Obtener URLs
    original_url = image_field.url
    webp_path = WebPOptimizer.get_webp_path(image_field.name)
    webp_url = None
    
    if webp_path and default_storage.exists(webp_path):
        webp_url = default_storage.url(webp_path)
    
    # Construir atributos
    img_attrs = [f'alt="{alt_text}"']
    
    if css_class:
        img_attrs.append(f'class="{css_class}"')
    
    img_attrs.append('loading="lazy"')
    
    if placeholder_url:
        img_attrs.append(f'data-src="{original_url}"')
        img_attrs.append(f'src="{placeholder_url}"')
    else:
        img_attrs.append(f'src="{original_url}"')
    
    img_attrs_str = ' '.join(img_attrs)
    
    # Si no hay WebP, usar imagen original simple
    if not webp_url:
        return mark_safe(f'<img {img_attrs_str}>')
    
    # Generar HTML con <picture> y <source>
    if placeholder_url:
        webp_src = f'data-src="{webp_url}"'
        original_src = f'data-src="{original_url}"'
    else:
        webp_src = f'srcset="{webp_url}"'
        original_src = f'src="{original_url}"'
    
    html = f'''
    <picture>
        <source {webp_src} type="image/webp">
        <img {original_src} {img_attrs_str}>
    </picture>
    '''
    
    return mark_safe(html.strip())

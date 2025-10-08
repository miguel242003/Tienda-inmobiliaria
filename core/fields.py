"""
Campos personalizados para manejo automático de WebP
"""

from django.db import models
from django.core.files.storage import default_storage
from .image_optimizer import WebPOptimizer
import logging

logger = logging.getLogger(__name__)

class WebPImageField(models.ImageField):
    """
    Campo de imagen que automáticamente convierte a WebP
    Mantiene el archivo original y crea una versión WebP optimizada
    """
    
    def __init__(self, *args, **kwargs):
        # Configuración por defecto para WebP
        self.webp_quality = kwargs.pop('webp_quality', 85)
        self.auto_optimize = kwargs.pop('auto_optimize', True)
        self.preserve_original = kwargs.pop('preserve_original', True)
        
        super().__init__(*args, **kwargs)
    
    def save_form_data(self, instance, data):
        """Maneja la subida de archivos y conversión automática"""
        if data is not None:
            # Guardar el archivo original primero
            super().save_form_data(instance, data)
            
            # Optimizar a WebP si está habilitado
            if self.auto_optimize and data:
                try:
                    result = WebPOptimizer.optimize_image_field(
                        instance, 
                        self.name, 
                        quality=self.webp_quality,
                        replace_original=True  # Reemplazar original con WebP
                    )
                    
                    if result['status'] == 'success':
                        logger.info(f"Imagen optimizada y original reemplazada: {result['webp_path']}")
                    else:
                        logger.warning(f"No se pudo optimizar imagen: {result['message']}")
                        
                except Exception as e:
                    logger.error(f"Error en optimización automática: {e}")
    
    def get_webp_url(self, instance):
        """Retorna la URL de la versión WebP si existe"""
        if not getattr(instance, self.name):
            return None
        
        original_path = getattr(instance, self.name).name
        webp_path = WebPOptimizer.get_webp_path(original_path)
        
        if webp_path and default_storage.exists(webp_path):
            return default_storage.url(webp_path)
        
        return None
    
    def get_original_url(self, instance):
        """Retorna la URL del archivo original"""
        if not getattr(instance, self.name):
            return None
        
        return getattr(instance, self.name).url
    
    def get_picture_sources(self, instance, alt_text="", css_class="", lazy_loading=True):
        """
        Genera las etiquetas HTML <picture> con fallback
        
        Args:
            instance: Instancia del modelo
            alt_text: Texto alternativo para la imagen
            css_class: Clases CSS para la imagen
            lazy_loading: Si habilitar lazy loading
            
        Returns:
            str: HTML completo con <picture> y <source>
        """
        if not getattr(instance, self.name):
            return ""
        
        webp_url = self.get_webp_url(instance)
        original_url = self.get_original_url(instance)
        
        if not original_url:
            return ""
        
        # Atributos de la imagen
        img_attrs = f'alt="{alt_text}"'
        if css_class:
            img_attrs += f' class="{css_class}"'
        if lazy_loading:
            img_attrs += ' loading="lazy"'
        
        # Si no hay WebP, usar imagen original simple
        if not webp_url:
            return f'<img src="{original_url}" {img_attrs}>'
        
        # Generar HTML con <picture> y <source>
        html = f'''
        <picture>
            <source srcset="{webp_url}" type="image/webp">
            <img src="{original_url}" {img_attrs}>
        </picture>
        '''
        
        return html.strip()


class WebPImageFieldMixin:
    """
    Mixin para agregar funcionalidad WebP a modelos existentes
    """
    
    def get_webp_url(self, field_name):
        """Retorna la URL WebP de un campo de imagen"""
        image_field = getattr(self, field_name)
        if not image_field:
            return None
        
        webp_path = WebPOptimizer.get_webp_path(image_field.name)
        if webp_path and default_storage.exists(webp_path):
            return default_storage.url(webp_path)
        
        return None
    
    def get_picture_html(self, field_name, alt_text="", css_class="", lazy_loading=True):
        """Genera HTML <picture> para un campo de imagen"""
        image_field = getattr(self, field_name)
        if not image_field:
            return ""
        
        webp_url = self.get_webp_url(field_name)
        original_url = image_field.url
        
        # Atributos de la imagen
        img_attrs = f'alt="{alt_text}"'
        if css_class:
            img_attrs += f' class="{css_class}"'
        if lazy_loading:
            img_attrs += ' loading="lazy"'
        
        # Si no hay WebP, usar imagen original simple
        if not webp_url:
            return f'<img src="{original_url}" {img_attrs}>'
        
        # Generar HTML con <picture> y <source>
        html = f'''
        <picture>
            <source srcset="{webp_url}" type="image/webp">
            <img src="{original_url}" {img_attrs}>
        </picture>
        '''
        
        return html.strip()
    
    def optimize_image_field(self, field_name, quality=85):
        """Optimiza un campo de imagen específico"""
        return WebPOptimizer.optimize_image_field(self, field_name, quality)
    
    def optimize_video_field(self, field_name, quality=80):
        """Optimiza un campo de video específico"""
        return WebPOptimizer.optimize_video_field(self, field_name, quality)
    
    def optimize_all_images(self, quality=85):
        """Optimiza todos los campos de imagen del modelo"""
        results = {}
        
        # Obtener todos los campos de imagen del modelo
        for field in self._meta.fields:
            if isinstance(field, models.ImageField):
                results[field.name] = self.optimize_image_field(field.name, quality)
        
        return results

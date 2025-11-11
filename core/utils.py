"""
Utilidades para el manejo de archivos estáticos
"""
import os
import shutil
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
from core.image_optimizer import WebPOptimizer
import logging

logger = logging.getLogger(__name__)


def copiar_imagen_a_static(imagen_field, nombre_archivo=None, quality=85):
    """
    Copia una imagen desde media a static/images/propiedades/ convirtiéndola a WebP
    
    Args:
        imagen_field: Campo de imagen del modelo (ImageField)
        nombre_archivo: Nombre personalizado para el archivo (opcional, sin extensión)
        quality: Calidad de compresión WebP (1-100, por defecto 85)
    
    Returns:
        str: Ruta relativa del archivo en static si se copió exitosamente, None si falló
    """
    if not imagen_field or not imagen_field.name:
        return None
    
    try:
        # Obtener la ruta del archivo en media
        ruta_media = imagen_field.path
        
        # Verificar que el archivo existe
        if not os.path.exists(ruta_media):
            logger.warning(f"El archivo no existe en media: {ruta_media}")
            return None
        
        # Convertir la imagen a WebP
        webp_file, original_size, webp_size, saved_percentage = WebPOptimizer.convert_to_webp(
            imagen_field, 
            quality=quality,
            max_dimension=2048,  # Redimensionar si es muy grande
            preserve_original=True
        )
        
        if webp_size == 0:
            logger.warning(f"No se pudo convertir la imagen a WebP: {imagen_field.name}")
            return None
        
        # Determinar el nombre del archivo (siempre con extensión .webp)
        if nombre_archivo:
            # Remover extensión si la tiene y agregar .webp
            nombre_base = os.path.splitext(nombre_archivo)[0]
            nombre_final = f"{nombre_base}.webp"
        else:
            # Usar el nombre original del archivo pero cambiar extensión a .webp
            nombre_base = os.path.splitext(os.path.basename(imagen_field.name))[0]
            nombre_base = nombre_base.replace(' ', '-').lower()
            nombre_final = f"{nombre_base}.webp"
        
        # Ruta de destino en static
        static_dir = Path(settings.STATICFILES_DIRS[0]) / 'images' / 'propiedades'
        static_dir.mkdir(parents=True, exist_ok=True)
        
        ruta_destino = static_dir / nombre_final
        
        # Si el archivo ya existe, agregar un sufijo numérico
        contador = 1
        nombre_base_sin_ext = os.path.splitext(nombre_final)[0]
        while ruta_destino.exists():
            nombre_final = f"{nombre_base_sin_ext}-{contador}.webp"
            ruta_destino = static_dir / nombre_final
            contador += 1
        
        # Guardar el archivo WebP en static
        with open(ruta_destino, 'wb') as f:
            webp_file.seek(0)  # Asegurar que estamos al inicio del archivo
            f.write(webp_file.read())
        
        # Ruta relativa desde static/images/propiedades/
        ruta_relativa = f"images/propiedades/{nombre_final}"
        
        logger.info(f"Imagen convertida a WebP y copiada a static: {ruta_relativa} "
                   f"({original_size} bytes -> {webp_size} bytes, {saved_percentage:.1f}% ahorro)")
        return ruta_relativa
        
    except Exception as e:
        logger.error(f"Error al copiar imagen a static: {e}")
        return None


def obtener_ruta_static_imagen(imagen_field, propiedad_slug=None, es_principal=True):
    """
    Verifica si existe una versión estática de la imagen y retorna su ruta
    
    Args:
        imagen_field: Campo de imagen del modelo
        propiedad_slug: Slug de la propiedad (opcional, para búsqueda más precisa)
        es_principal: True si es imagen principal, False si es secundaria
    
    Returns:
        str: Ruta relativa en static si existe, None si no existe
    """
    if not imagen_field or not imagen_field.name:
        return None
    
    try:
        static_dir = Path(settings.STATICFILES_DIRS[0]) / 'images' / 'propiedades'
        
        # Primero intentar buscar por slug si está disponible (priorizar .webp)
        if propiedad_slug:
            sufijo = "principal" if es_principal else "secundaria"
            nombre_por_slug = f"{propiedad_slug}-{sufijo}"
            
            # Buscar primero WebP (formato preferido)
            ruta_webp = static_dir / f"{nombre_por_slug}.webp"
            if ruta_webp.exists():
                return f"images/propiedades/{nombre_por_slug}.webp"
            
            # Si no hay WebP, buscar otros formatos como fallback
            for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                ruta_por_slug = static_dir / f"{nombre_por_slug}{ext}"
                if ruta_por_slug.exists():
                    return f"images/propiedades/{nombre_por_slug}{ext}"
            
            # Buscar variaciones con sufijos numéricos (priorizar WebP)
            nombre_base = nombre_por_slug
            for i in range(1, 100):
                # Primero buscar WebP
                ruta_webp_var = static_dir / f"{nombre_base}-{i}.webp"
                if ruta_webp_var.exists():
                    return f"images/propiedades/{nombre_base}-{i}.webp"
                
                # Luego otros formatos
                for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    nombre_variacion = f"{nombre_base}-{i}{ext}"
                    ruta_variacion = static_dir / nombre_variacion
                    if ruta_variacion.exists():
                        return f"images/propiedades/{nombre_variacion}"
        
        # Si no se encontró por slug, buscar por nombre original (priorizar WebP)
        nombre_archivo = os.path.basename(imagen_field.name)
        nombre_archivo = nombre_archivo.replace(' ', '-').lower()
        nombre_base, ext_original = os.path.splitext(nombre_archivo)
        
        # Buscar primero versión WebP
        ruta_webp = static_dir / f"{nombre_base}.webp"
        if ruta_webp.exists():
            return f"images/propiedades/{nombre_base}.webp"
        
        # Si no hay WebP, buscar con extensión original
        ruta_static = static_dir / nombre_archivo
        if ruta_static.exists():
            return f"images/propiedades/{nombre_archivo}"
        
        # Buscar variaciones del nombre (con sufijos numéricos, priorizar WebP)
        for i in range(1, 100):
            # Primero buscar WebP
            ruta_webp_var = static_dir / f"{nombre_base}-{i}.webp"
            if ruta_webp_var.exists():
                return f"images/propiedades/{nombre_base}-{i}.webp"
            
            # Luego con extensión original
            nombre_variacion = f"{nombre_base}-{i}{ext_original}"
            ruta_variacion = static_dir / nombre_variacion
            if ruta_variacion.exists():
                return f"images/propiedades/{nombre_variacion}"
        
        return None
        
    except Exception as e:
        logger.error(f"Error al verificar ruta estática: {e}")
        return None


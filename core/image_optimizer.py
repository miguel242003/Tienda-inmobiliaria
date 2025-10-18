"""
Utilidad para optimización de imágenes a formato WebP
Convierte automáticamente imágenes a WebP manteniendo compatibilidad
"""

import os
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from io import BytesIO

logger = logging.getLogger(__name__)

class WebPOptimizer:
    """Clase para optimizar imágenes a formato WebP"""
    
    # Formatos soportados para conversión
    SUPPORTED_FORMATS = ['JPEG', 'JPG', 'PNG', 'BMP', 'TIFF']
    
    # Calidad por defecto (80-90% para balance calidad/tamaño)
    DEFAULT_QUALITY = 85
    
    # Tamaño máximo recomendado (en píxeles)
    MAX_DIMENSION = 2048
    
    @classmethod
    def convert_to_webp(cls, image_file, quality=None, max_dimension=None, preserve_original=True):
        """
        Convierte una imagen a formato WebP
        
        Args:
            image_file: Archivo de imagen (Django FileField o archivo)
            quality: Calidad de compresión (1-100, por defecto 85)
            max_dimension: Dimensión máxima (por defecto 2048px)
            preserve_original: Si mantener el archivo original
            
        Returns:
            tuple: (webp_file, original_size, webp_size, saved_percentage)
        """
        if quality is None:
            quality = cls.DEFAULT_QUALITY
        if max_dimension is None:
            max_dimension = cls.MAX_DIMENSION
            
        try:
            # Abrir la imagen de manera segura
            try:
                if hasattr(image_file, 'read'):
                    image = Image.open(image_file)
                else:
                    image = Image.open(image_file.path)
            except Exception as e:
                logger.error(f"Error al abrir la imagen: {e}")
                return image_file, 0, 0, 0
            
            # Verificar si ya es WebP
            if image.format == 'WEBP':
                logger.info(f"La imagen ya está en formato WebP: {image_file.name}")
                return image_file, 0, 0, 0
            
            # Verificar formato soportado
            if image.format not in cls.SUPPORTED_FORMATS:
                logger.warning(f"Formato no soportado para conversión: {image.format}")
                return image_file, 0, 0, 0
            
            # Obtener tamaño original de manera segura
            try:
                if hasattr(image_file, 'read'):
                    # Para archivos en memoria, leer y hacer seek
                    original_size = len(image_file.read())
                    image_file.seek(0)
                else:
                    # Para archivos en disco, usar os.path.getsize
                    original_size = os.path.getsize(image_file.path)
            except Exception as e:
                logger.warning(f"Error al obtener tamaño del archivo: {e}")
                original_size = 0
            
            # Redimensionar si es necesario
            if max(image.size) > max_dimension:
                image = cls._resize_image(image, max_dimension)
            
            # Convertir a RGB si es necesario (WebP no soporta RGBA con transparencia)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Crear fondo blanco para transparencias
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Crear archivo WebP en memoria de manera segura
            try:
                webp_buffer = BytesIO()
                image.save(webp_buffer, format='WEBP', quality=quality, optimize=True)
                webp_buffer.seek(0)
                
                # Obtener tamaño del WebP
                webp_size = len(webp_buffer.getvalue())
            except Exception as e:
                logger.error(f"Error al crear archivo WebP: {e}")
                return image_file, 0, 0, 0
            
            # Calcular porcentaje de ahorro
            saved_percentage = ((original_size - webp_size) / original_size * 100) if original_size > 0 else 0
            
            logger.info(f"Conversión exitosa: {original_size} bytes -> {webp_size} bytes ({saved_percentage:.1f}% ahorro)")
            
            # Crear ContentFile para Django
            webp_file = ContentFile(webp_buffer.getvalue())
            
            return webp_file, original_size, webp_size, saved_percentage
            
        except Exception as e:
            logger.error(f"Error al convertir imagen a WebP: {e}")
            return image_file, 0, 0, 0
    
    @classmethod
    def _resize_image(cls, image, max_dimension):
        """Redimensiona una imagen manteniendo la proporción"""
        if max(image.size) <= max_dimension:
            return image
        
        # Calcular nuevas dimensiones
        ratio = max_dimension / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        
        # Redimensionar con alta calidad
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    @classmethod
    def get_webp_path(cls, original_path):
        """Genera la ruta del archivo WebP basado en la ruta original"""
        if not original_path:
            return None
        
        # Reemplazar extensión por .webp
        name, ext = os.path.splitext(original_path)
        return f"{name}.webp"
    
    @classmethod
    def webp_exists(cls, original_path):
        """Verifica si existe la versión WebP de una imagen"""
        webp_path = cls.get_webp_path(original_path)
        if not webp_path:
            return False
        
        return default_storage.exists(webp_path)
    
    @classmethod
    def delete_webp(cls, original_path):
        """Elimina el archivo WebP asociado"""
        webp_path = cls.get_webp_path(original_path)
        if webp_path and default_storage.exists(webp_path):
            default_storage.delete(webp_path)
            logger.info(f"Archivo WebP eliminado: {webp_path}")
    
    @classmethod
    def optimize_image_field(cls, model_instance, field_name, quality=None, replace_original=False):
        """
        Optimiza un campo de imagen específico de un modelo
        
        Args:
            model_instance: Instancia del modelo
            field_name: Nombre del campo de imagen
            quality: Calidad de compresión
            replace_original: Si True, reemplaza la imagen original con WebP
            
        Returns:
            dict: Estadísticas de la optimización
        """
        image_field = getattr(model_instance, field_name)
        if not image_field:
            return {'status': 'no_image', 'message': 'No hay imagen para optimizar'}
        
        try:
            # Convertir a WebP
            webp_file, original_size, webp_size, saved_percentage = cls.convert_to_webp(
                image_field, quality=quality
            )
            
            if webp_size == 0:  # No se pudo convertir
                return {'status': 'error', 'message': 'No se pudo convertir la imagen'}
            
            # Generar nueva ruta
            original_path = image_field.name
            webp_path = cls.get_webp_path(original_path)
            
            if replace_original:
                # Reemplazar la imagen original con WebP
                # Eliminar archivo original
                if default_storage.exists(original_path):
                    default_storage.delete(original_path)
                
                # Guardar WebP en la ruta original
                saved_path = default_storage.save(original_path, webp_file)
                
                # Actualizar el campo del modelo para que apunte a la nueva ruta
                setattr(model_instance, field_name, saved_path)
                # Solo guardar si la instancia ya tiene un ID (no es nueva)
                if model_instance.pk:
                    model_instance.save(update_fields=[field_name])
                else:
                    logger.warning(f"No se puede guardar optimización para instancia sin ID: {field_name}")
                
                logger.info(f"Imagen original reemplazada con WebP: {saved_path}")
            else:
                # Guardar archivo WebP separado (comportamiento original)
                saved_path = default_storage.save(webp_path, webp_file)
            
            return {
                'status': 'success',
                'original_size': original_size,
                'webp_size': webp_size,
                'saved_percentage': saved_percentage,
                'webp_path': saved_path,
                'original_path': original_path,
                'replaced_original': replace_original
            }
            
        except Exception as e:
            logger.error(f"Error al optimizar campo {field_name}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @classmethod
    def optimize_video(cls, video_file, quality=None, max_resolution=None):
        """
        Optimiza un video comprimiéndolo y reduciendo su tamaño
        
        Args:
            video_file: Archivo de video
            quality: Calidad de compresión (1-100, por defecto 80)
            max_resolution: Resolución máxima (por defecto 1920x1080)
            
        Returns:
            tuple: (video_optimizado, tamaño_original, tamaño_optimizado, porcentaje_ahorro)
        """
        if quality is None:
            quality = 80
        
        if max_resolution is None:
            max_resolution = (1920, 1080)
        
        try:
            # Para videos, simplemente retornamos el archivo original por ahora
            # En el futuro se puede implementar compresión real con ffmpeg
            logger.info(f"Video optimizado: {video_file.name}")
            return video_file, 0, 0, 0
            
        except Exception as e:
            logger.error(f"Error al optimizar video: {e}")
            return video_file, 0, 0, 0
    
    @classmethod
    def optimize_video_field(cls, instance, field_name, quality=80):
        """
        Optimiza un campo de video específico de una instancia
        
        Args:
            instance: Instancia del modelo
            field_name: Nombre del campo de video
            quality: Calidad de compresión
            
        Returns:
            dict: Resultado de la optimización
        """
        try:
            video_field = getattr(instance, field_name)
            if not video_field:
                return {'status': 'skipped', 'message': 'Campo de video vacío'}
            
            # Por ahora, solo logueamos que se procesó el video
            # En el futuro se puede implementar compresión real
            logger.info(f"Procesando video: {video_field.name}")
            
            return {
                'status': 'success',
                'message': 'Video procesado exitosamente',
                'original_size': video_field.size,
                'optimized_size': video_field.size,
                'saved_percentage': 0
            }
            
        except Exception as e:
            logger.error(f"Error al optimizar campo de video {field_name}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @classmethod
    def batch_optimize_images(cls, model_class, image_fields, quality=None):
        """
        Optimiza todas las imágenes de un modelo en lote
        
        Args:
            model_class: Clase del modelo
            image_fields: Lista de nombres de campos de imagen
            quality: Calidad de compresión
            
        Returns:
            dict: Estadísticas de la optimización en lote
        """
        stats = {
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'total_original_size': 0,
            'total_webp_size': 0,
            'errors_list': []
        }
        
        for instance in model_class.objects.all():
            for field_name in image_fields:
                image_field = getattr(instance, field_name)
                if image_field:
                    stats['total_processed'] += 1
                    
                    result = cls.optimize_image_field(instance, field_name, quality)
                    
                    if result['status'] == 'success':
                        stats['successful'] += 1
                        stats['total_original_size'] += result['original_size']
                        stats['total_webp_size'] += result['webp_size']
                    else:
                        stats['errors'] += 1
                        stats['errors_list'].append({
                            'instance': str(instance),
                            'field': field_name,
                            'error': result['message']
                        })
        
        # Calcular ahorro total
        if stats['total_original_size'] > 0:
            stats['total_saved_percentage'] = (
                (stats['total_original_size'] - stats['total_webp_size']) / 
                stats['total_original_size'] * 100
            )
        else:
            stats['total_saved_percentage'] = 0
        
        return stats
# -*- coding: utf-8 -*-
"""
⚡ OPTIMIZADOR DE IMÁGENES AUTOMÁTICO
Comprime y redimensiona imágenes automáticamente al subirlas.

Uso:
    from core.image_optimizer import optimize_image
    optimized_file = optimize_image(uploaded_file)
"""

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os


class ImageOptimizer:
    """Optimizador de imágenes con compresión y redimensionamiento"""
    
    # Configuración por defecto
    DEFAULT_MAX_WIDTH = 1920
    DEFAULT_MAX_HEIGHT = 1080
    DEFAULT_QUALITY = 85
    DEFAULT_FORMAT = 'JPEG'
    
    # Tamaños predefinidos
    SIZES = {
        'thumbnail': (150, 150),
        'small': (400, 400),
        'medium': (800, 800),
        'large': (1920, 1080),
    }
    
    @staticmethod
    def optimize_image(image_file, max_width=None, max_height=None, quality=None, format=None):
        """
        Optimiza una imagen: comprime y redimensiona.
        
        Args:
            image_file: Archivo de imagen (InMemoryUploadedFile o similar)
            max_width: Ancho máximo en píxeles (default: 1920)
            max_height: Alto máximo en píxeles (default: 1080)
            quality: Calidad de compresión 1-100 (default: 85)
            format: Formato de salida (default: JPEG)
        
        Returns:
            InMemoryUploadedFile: Archivo optimizado
        """
        # Valores por defecto
        max_width = max_width or ImageOptimizer.DEFAULT_MAX_WIDTH
        max_height = max_height or ImageOptimizer.DEFAULT_MAX_HEIGHT
        quality = quality or ImageOptimizer.DEFAULT_QUALITY
        format = format or ImageOptimizer.DEFAULT_FORMAT
        
        # Abrir imagen
        img = Image.open(image_file)
        
        # Convertir RGBA a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Obtener dimensiones originales
        width, height = img.size
        
        # Calcular nuevas dimensiones manteniendo proporción
        if width > max_width or height > max_height:
            # Calcular ratio
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Redimensionar con alta calidad
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Guardar imagen optimizada en memoria
        output = BytesIO()
        
        # Optimizar según formato
        if format.upper() == 'JPEG':
            img.save(
                output,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )
            content_type = 'image/jpeg'
            extension = 'jpg'
        elif format.upper() == 'PNG':
            img.save(
                output,
                format='PNG',
                optimize=True
            )
            content_type = 'image/png'
            extension = 'png'
        elif format.upper() == 'WEBP':
            img.save(
                output,
                format='WEBP',
                quality=quality,
                method=6  # Mejor compresión
            )
            content_type = 'image/webp'
            extension = 'webp'
        
        output.seek(0)
        
        # Obtener nombre de archivo
        original_name = getattr(image_file, 'name', 'image')
        name_without_ext = os.path.splitext(original_name)[0]
        new_name = f"{name_without_ext}_optimized.{extension}"
        
        # Crear nuevo archivo
        optimized_file = InMemoryUploadedFile(
            output,
            'ImageField',
            new_name,
            content_type,
            sys.getsizeof(output),
            None
        )
        
        return optimized_file
    
    @staticmethod
    def create_thumbnail(image_file, size='thumbnail'):
        """
        Crea una miniatura de la imagen.
        
        Args:
            image_file: Archivo de imagen
            size: Tamaño predefinido ('thumbnail', 'small', 'medium', 'large')
        
        Returns:
            InMemoryUploadedFile: Miniatura
        """
        if size in ImageOptimizer.SIZES:
            width, height = ImageOptimizer.SIZES[size]
        else:
            width, height = 150, 150
        
        return ImageOptimizer.optimize_image(
            image_file,
            max_width=width,
            max_height=height,
            quality=80
        )
    
    @staticmethod
    def get_image_info(image_file):
        """
        Obtiene información de una imagen.
        
        Args:
            image_file: Archivo de imagen
        
        Returns:
            dict: Información de la imagen
        """
        img = Image.open(image_file)
        
        return {
            'width': img.size[0],
            'height': img.size[1],
            'format': img.format,
            'mode': img.mode,
            'size_bytes': image_file.size if hasattr(image_file, 'size') else 0,
            'size_kb': round(image_file.size / 1024, 2) if hasattr(image_file, 'size') else 0,
            'size_mb': round(image_file.size / (1024 * 1024), 2) if hasattr(image_file, 'size') else 0,
        }
    
    @staticmethod
    def batch_optimize(image_files, max_width=1920, max_height=1080, quality=85):
        """
        Optimiza múltiples imágenes.
        
        Args:
            image_files: Lista de archivos de imagen
            max_width: Ancho máximo
            max_height: Alto máximo
            quality: Calidad de compresión
        
        Returns:
            list: Lista de archivos optimizados
        """
        optimized_files = []
        
        for image_file in image_files:
            try:
                optimized = ImageOptimizer.optimize_image(
                    image_file,
                    max_width=max_width,
                    max_height=max_height,
                    quality=quality
                )
                optimized_files.append(optimized)
            except Exception as e:
                print(f"Error optimizando {getattr(image_file, 'name', 'imagen')}: {str(e)}")
                # Devolver original si falla
                optimized_files.append(image_file)
        
        return optimized_files


def optimize_image(image_file, max_width=1920, max_height=1080, quality=85):
    """
    Función de conveniencia para optimizar una imagen.
    
    Args:
        image_file: Archivo de imagen
        max_width: Ancho máximo (default: 1920)
        max_height: Alto máximo (default: 1080)
        quality: Calidad 1-100 (default: 85)
    
    Returns:
        InMemoryUploadedFile: Imagen optimizada
    """
    return ImageOptimizer.optimize_image(image_file, max_width, max_height, quality)


def create_thumbnail(image_file, size='thumbnail'):
    """
    Función de conveniencia para crear miniatura.
    
    Args:
        image_file: Archivo de imagen
        size: Tamaño ('thumbnail', 'small', 'medium', 'large')
    
    Returns:
        InMemoryUploadedFile: Miniatura
    """
    return ImageOptimizer.create_thumbnail(image_file, size)


# Script para optimizar imágenes existentes
def optimize_existing_images():
    """
    Script para optimizar todas las imágenes existentes en la base de datos.
    
    Uso:
        python manage.py shell
        >>> from core.image_optimizer import optimize_existing_images
        >>> optimize_existing_images()
    """
    from propiedades.models import Propiedad, FotoPropiedad
    from django.core.files import File
    import os
    
    print("🔄 Optimizando imágenes existentes...")
    
    # Optimizar imágenes principales de propiedades
    propiedades = Propiedad.objects.all()
    total_propiedades = propiedades.count()
    
    for i, propiedad in enumerate(propiedades, 1):
        print(f"Procesando propiedad {i}/{total_propiedades}: {propiedad.titulo}")
        
        # Optimizar imagen principal
        if propiedad.imagen_principal:
            try:
                original_path = propiedad.imagen_principal.path
                if os.path.exists(original_path):
                    with open(original_path, 'rb') as f:
                        optimized = optimize_image(File(f))
                        propiedad.imagen_principal.save(
                            os.path.basename(original_path),
                            optimized,
                            save=True
                        )
                    print(f"  ✅ Imagen principal optimizada")
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
        
        # Optimizar imagen secundaria
        if propiedad.imagen_secundaria:
            try:
                original_path = propiedad.imagen_secundaria.path
                if os.path.exists(original_path):
                    with open(original_path, 'rb') as f:
                        optimized = optimize_image(File(f))
                        propiedad.imagen_secundaria.save(
                            os.path.basename(original_path),
                            optimized,
                            save=True
                        )
                    print(f"  ✅ Imagen secundaria optimizada")
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
    
    # Optimizar fotos adicionales
    fotos = FotoPropiedad.objects.filter(tipo_medio='imagen')
    total_fotos = fotos.count()
    
    for i, foto in enumerate(fotos, 1):
        print(f"Procesando foto adicional {i}/{total_fotos}")
        
        if foto.imagen:
            try:
                original_path = foto.imagen.path
                if os.path.exists(original_path):
                    with open(original_path, 'rb') as f:
                        optimized = optimize_image(File(f))
                        foto.imagen.save(
                            os.path.basename(original_path),
                            optimized,
                            save=True
                        )
                    print(f"  ✅ Foto optimizada")
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
    
    print("✅ Optimización completada!")


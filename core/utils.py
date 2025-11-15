"""
Utilidades para el manejo de archivos estáticos
"""
import os
import shutil
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
from django.templatetags.static import static
from core.image_optimizer import WebPOptimizer
import logging

# Usar el logger de 'core' que está configurado en settings
logger = logging.getLogger('core')


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
    logger.info(f"🔍 copiar_imagen_a_static iniciado")
    logger.info(f"   imagen_field: {imagen_field}")
    logger.info(f"   imagen_field.name: {imagen_field.name if imagen_field else None}")
    logger.info(f"   nombre_archivo: {nombre_archivo}")
    
    if not imagen_field or not imagen_field.name:
        logger.error(f"❌ imagen_field o imagen_field.name es None")
        return None
    
    try:
        # Obtener la ruta del archivo en media usando default_storage
        # Usar path si está disponible, sino usar default_storage
        # Intentar obtener la ruta del archivo de diferentes formas
        ruta_media = None
        temp_file = None
        
        try:
            # Método 1: Intentar usar path directamente (más confiable en desarrollo)
            try:
                ruta_media = imagen_field.path
                if os.path.exists(ruta_media):
                    logger.debug(f"Archivo encontrado en path: {ruta_media}")
                else:
                    ruta_media = None
                    logger.debug(f"Archivo no existe en path: {imagen_field.path}")
            except (AttributeError, NotImplementedError, ValueError) as e:
                logger.debug(f"No se pudo usar path directamente: {e}")
                ruta_media = None
            
            # Método 2: Si path no funciona, intentar construir la ruta manualmente
            if not ruta_media or not os.path.exists(ruta_media):
                try:
                    ruta_manual = Path(settings.MEDIA_ROOT) / imagen_field.name
                    if os.path.exists(ruta_manual):
                        ruta_media = str(ruta_manual)
                        logger.debug(f"Archivo encontrado en ruta manual: {ruta_media}")
                except Exception as e:
                    logger.debug(f"Error al construir ruta manual: {e}")
            
            # Método 3: Si path no funciona, usar default_storage
            if not ruta_media or not os.path.exists(ruta_media):
                if default_storage.exists(imagen_field.name):
                    # Leer el archivo desde storage y crear temporal
                    with default_storage.open(imagen_field.name, 'rb') as f:
                        contenido = f.read()
                    from tempfile import NamedTemporaryFile
                    temp_file = NamedTemporaryFile(delete=False, suffix=os.path.splitext(imagen_field.name)[1])
                    temp_file.write(contenido)
                    temp_file.close()
                    ruta_media = temp_file.name
                    logger.debug(f"Archivo leído desde storage y guardado en temporal: {ruta_media}")
                else:
                    logger.warning(f"El archivo no existe en storage: {imagen_field.name}")
                    # Intentar una vez más después de un pequeño retraso
                    import time
                    time.sleep(0.5)
                    if default_storage.exists(imagen_field.name):
                        with default_storage.open(imagen_field.name, 'rb') as f:
                            contenido = f.read()
                        from tempfile import NamedTemporaryFile
                        temp_file = NamedTemporaryFile(delete=False, suffix=os.path.splitext(imagen_field.name)[1])
                        temp_file.write(contenido)
                        temp_file.close()
                        ruta_media = temp_file.name
                        logger.info(f"Archivo encontrado en segundo intento: {ruta_media}")
                    else:
                        # Último intento: verificar si existe físicamente en MEDIA_ROOT
                        try:
                            ruta_fisica = Path(settings.MEDIA_ROOT) / imagen_field.name
                            if os.path.exists(ruta_fisica):
                                ruta_media = str(ruta_fisica)
                                logger.info(f"Archivo encontrado físicamente en MEDIA_ROOT: {ruta_media}")
                            else:
                                logger.error(f"El archivo no existe en storage ni físicamente: {imagen_field.name} (buscado en: {ruta_fisica})")
                                return None
                        except Exception as e:
                            logger.error(f"Error al verificar archivo físicamente: {e}")
                            logger.error(f"El archivo no existe en storage después de reintento: {imagen_field.name}")
                            return None
        except Exception as e:
            logger.error(f"❌ EXCEPCIÓN al obtener ruta del archivo: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        
        if not ruta_media:
            logger.error(f"❌ No se pudo obtener ruta_media para: {imagen_field.name}")
            return None
        
        logger.info(f"✅ Ruta media obtenida: {ruta_media}")
        
        # Convertir la imagen a WebP
        # Si tenemos una ruta física (ya sea temporal o del filesystem), usarla directamente
        webp_file = None
        original_size = 0
        webp_size = 0
        saved_percentage = 0
        
        logger.info(f"🔄 Iniciando conversión a WebP...")
        logger.info(f"   ruta_media existe: {ruta_media and os.path.exists(ruta_media) if ruta_media else False}")
        
        try:
            # Si tenemos una ruta física, usarla directamente (más confiable)
            if ruta_media and os.path.exists(ruta_media):
                logger.info(f"✅ Usando ruta física para conversión: {ruta_media}")
                from django.core.files import File
                with open(ruta_media, 'rb') as f:
                    temp_image_field = File(f, name=os.path.basename(imagen_field.name))
                    webp_file, original_size, webp_size, saved_percentage = WebPOptimizer.convert_to_webp(
                        temp_image_field, 
                        quality=quality,
                        max_dimension=2048,
                        preserve_original=True
                    )
                    logger.info(f"✅ Imagen convertida usando ruta física: {ruta_media}")
            else:
                # Si no tenemos ruta física, intentar usar el campo directamente
                logger.warning(f"⚠️ No hay ruta física, intentando convertir usando imagen_field directamente")
                webp_file, original_size, webp_size, saved_percentage = WebPOptimizer.convert_to_webp(
                    imagen_field, 
                    quality=quality,
                    max_dimension=2048,  # Redimensionar si es muy grande
                    preserve_original=True
                )
                logger.info(f"✅ Imagen convertida usando imagen_field directamente")
        except Exception as e:
            logger.error(f"❌ EXCEPCIÓN en conversión WebP: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Si falla, intentar con el campo directamente si no lo hemos intentado
            if ruta_media and os.path.exists(ruta_media):
                logger.warning(f"⚠️ Reintentando conversión con imagen_field directamente")
                try:
                    webp_file, original_size, webp_size, saved_percentage = WebPOptimizer.convert_to_webp(
                        imagen_field, 
                        quality=quality,
                        max_dimension=2048,
                        preserve_original=True
                    )
                    logger.info(f"✅ Conversión exitosa en segundo intento")
                except Exception as e2:
                    logger.error(f"❌ ERROR en segundo intento de conversión: {e2}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return None
            else:
                logger.error(f"❌ No se pudo convertir imagen a WebP: {e}")
                return None
        
        if webp_size == 0:
            logger.error(f"❌ ERROR: No se pudo convertir la imagen a WebP (tamaño 0): {imagen_field.name}")
            logger.error(f"   Ruta media: {ruta_media}")
            logger.error(f"   Archivo existe: {ruta_media and os.path.exists(ruta_media) if ruta_media else False}")
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
        
        # Limpiar archivo temporal si se creó
        if 'temp_file' in locals() and os.path.exists(ruta_media) and ruta_media != imagen_field.path:
            try:
                os.unlink(ruta_media)
            except:
                pass
        
        # Ruta relativa desde static/images/propiedades/
        ruta_relativa = f"images/propiedades/{nombre_final}"
        
        # Verificar que el archivo WebP se creó correctamente
        if not os.path.exists(ruta_destino):
            logger.error(f"❌ ERROR: El archivo WebP no se creó en: {ruta_destino}")
            return None
        
        file_size = os.path.getsize(ruta_destino)
        if file_size == 0:
            logger.error(f"❌ ERROR: El archivo WebP está vacío: {ruta_destino}")
            return None
        
        logger.info(f"✅ Imagen convertida a WebP y copiada a static: {ruta_relativa} "
                   f"({original_size} bytes -> {webp_size} bytes, {saved_percentage:.1f}% ahorro)")
        logger.info(f"   Archivo WebP creado: {ruta_destino} ({file_size} bytes)")
        return ruta_relativa
        
    except Exception as e:
        logger.error(f"❌ EXCEPCIÓN al copiar imagen a static: {e}")
        logger.error(f"   Archivo: {imagen_field.name if imagen_field else 'None'}")
        logger.error(f"   Nombre archivo: {nombre_archivo}")
        import traceback
        logger.error(traceback.format_exc())
        # Limpiar archivo temporal si se creó
        if 'temp_file' in locals() and 'ruta_media' in locals() and os.path.exists(ruta_media):
            try:
                if ruta_media != getattr(imagen_field, 'path', None):
                    os.unlink(ruta_media)
            except:
                pass
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


def eliminar_imagenes_static_propiedad(propiedad_slug):
    """
    Elimina las imágenes estáticas (WebP) de una propiedad desde static/images/propiedades/
    
    Args:
        propiedad_slug: Slug de la propiedad
    
    Returns:
        dict: Resultado de la eliminación con lista de archivos eliminados
    """
    archivos_eliminados = []
    archivos_no_encontrados = []
    
    try:
        static_dir = Path(settings.STATICFILES_DIRS[0]) / 'images' / 'propiedades'
        
        if not static_dir.exists():
            logger.warning(f"Directorio static/images/propiedades/ no existe")
            return {
                'success': False,
                'message': 'Directorio static/images/propiedades/ no existe',
                'archivos_eliminados': [],
                'archivos_no_encontrados': []
            }
        
        # Buscar y eliminar imagen principal
        for ext in ['.webp', '.jpg', '.jpeg', '.png', '.gif']:
            nombre_principal = f"{propiedad_slug}-principal{ext}"
            ruta_principal = static_dir / nombre_principal
            
            if ruta_principal.exists():
                try:
                    ruta_principal.unlink()
                    archivos_eliminados.append(nombre_principal)
                    logger.info(f"Imagen principal eliminada: {nombre_principal}")
                except Exception as e:
                    logger.error(f"Error al eliminar imagen principal {nombre_principal}: {e}")
            else:
                # Buscar variaciones con sufijos numéricos
                for i in range(1, 100):
                    nombre_variacion = f"{propiedad_slug}-principal-{i}{ext}"
                    ruta_variacion = static_dir / nombre_variacion
                    if ruta_variacion.exists():
                        try:
                            ruta_variacion.unlink()
                            archivos_eliminados.append(nombre_variacion)
                            logger.info(f"Imagen principal eliminada: {nombre_variacion}")
                        except Exception as e:
                            logger.error(f"Error al eliminar imagen principal {nombre_variacion}: {e}")
        
        # Buscar y eliminar imagen secundaria
        for ext in ['.webp', '.jpg', '.jpeg', '.png', '.gif']:
            nombre_secundaria = f"{propiedad_slug}-secundaria{ext}"
            ruta_secundaria = static_dir / nombre_secundaria
            
            if ruta_secundaria.exists():
                try:
                    ruta_secundaria.unlink()
                    archivos_eliminados.append(nombre_secundaria)
                    logger.info(f"Imagen secundaria eliminada: {nombre_secundaria}")
                except Exception as e:
                    logger.error(f"Error al eliminar imagen secundaria {nombre_secundaria}: {e}")
            else:
                # Buscar variaciones con sufijos numéricos
                for i in range(1, 100):
                    nombre_variacion = f"{propiedad_slug}-secundaria-{i}{ext}"
                    ruta_variacion = static_dir / nombre_variacion
                    if ruta_variacion.exists():
                        try:
                            ruta_variacion.unlink()
                            archivos_eliminados.append(nombre_variacion)
                            logger.info(f"Imagen secundaria eliminada: {nombre_variacion}")
                        except Exception as e:
                            logger.error(f"Error al eliminar imagen secundaria {nombre_variacion}: {e}")
        
        return {
            'success': True,
            'message': f'Eliminadas {len(archivos_eliminados)} imágenes estáticas',
            'archivos_eliminados': archivos_eliminados,
            'archivos_no_encontrados': archivos_no_encontrados
        }
        
    except Exception as e:
        logger.error(f"Error al eliminar imágenes estáticas de propiedad {propiedad_slug}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'message': f'Error al eliminar imágenes: {str(e)}',
            'archivos_eliminados': archivos_eliminados,
            'archivos_no_encontrados': archivos_no_encontrados
        }


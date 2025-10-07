# 🔒 VALIDADORES DE SEGURIDAD PARA ARCHIVOS
# Implementación según OWASP - A08: Data Integrity Failures

import magic
from django.core.exceptions import ValidationError
import re
import os


class FileValidator:
    """Validador robusto de archivos con verificación de tipo MIME real"""
    
    # Tipos MIME permitidos para imágenes
    ALLOWED_IMAGE_MIMES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/bmp',
    ]
    
    # Tipos MIME permitidos para videos
    ALLOWED_VIDEO_MIMES = [
        'video/mp4',
        'video/mpeg',
        'video/quicktime',
        'video/x-msvideo',  # AVI
        'video/webm',
    ]
    
    # Extensiones permitidas para imágenes
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
    
    # Extensiones permitidas para videos
    ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'mpeg', 'mov', 'avi', 'webm']
    
    # Extensiones permitidas para documentos (CV)
    ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx']
    
    # Tipos MIME permitidos para documentos
    ALLOWED_DOCUMENT_MIMES = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]
    
    @staticmethod
    def validar_tamano(archivo, max_mb=20):
        """
        Valida el tamaño del archivo.
        
        Args:
            archivo: Archivo a validar
            max_mb: Tamaño máximo en MB (default: 20MB)
        
        Raises:
            ValidationError: Si el archivo excede el tamaño máximo
        """
        max_bytes = max_mb * 1024 * 1024
        if archivo.size > max_bytes:
            raise ValidationError(
                f'El archivo no debe superar {max_mb}MB. '
                f'Tamaño actual: {archivo.size / (1024*1024):.2f}MB'
            )
    
    @staticmethod
    def validar_mime_type(archivo, allowed_mimes):
        """
        Valida el tipo MIME real del archivo (no solo la extensión).
        
        Args:
            archivo: Archivo a validar
            allowed_mimes: Lista de tipos MIME permitidos
        
        Raises:
            ValidationError: Si el tipo MIME no está permitido
        """
        # Leer los primeros 2048 bytes para determinar el tipo MIME
        file_head = archivo.read(2048)
        archivo.seek(0)  # Volver al inicio del archivo
        
        # Determinar el tipo MIME real
        mime = magic.from_buffer(file_head, mime=True)
        
        if mime not in allowed_mimes:
            raise ValidationError(
                f'Tipo de archivo no permitido: {mime}. '
                f'Tipos permitidos: {", ".join(allowed_mimes)}'
            )
        
        return mime
    
    @staticmethod
    def validar_extension(archivo, allowed_extensions):
        """
        Valida la extensión del archivo.
        
        Args:
            archivo: Archivo a validar
            allowed_extensions: Lista de extensiones permitidas
        
        Raises:
            ValidationError: Si la extensión no está permitida
        """
        nombre_archivo = archivo.name.lower()
        extension = nombre_archivo.split('.')[-1] if '.' in nombre_archivo else ''
        
        if extension not in allowed_extensions:
            raise ValidationError(
                f'Extensión no permitida: .{extension}. '
                f'Extensiones permitidas: {", ".join(allowed_extensions)}'
            )
        
        return extension
    
    @staticmethod
    def sanitizar_nombre_archivo(archivo):
        """
        Sanitiza el nombre del archivo removiendo caracteres peligrosos.
        
        Args:
            archivo: Archivo a sanitizar
        
        Returns:
            str: Nombre de archivo sanitizado
        """
        # Obtener nombre y extensión
        nombre_original = archivo.name
        nombre_base = os.path.splitext(nombre_original)[0]
        extension = os.path.splitext(nombre_original)[1]
        
        # Remover caracteres peligrosos (solo permitir alfanuméricos, guiones y guiones bajos)
        nombre_limpio = re.sub(r'[^a-zA-Z0-9._-]', '_', nombre_base)
        
        # Limitar longitud del nombre
        nombre_limpio = nombre_limpio[:100]
        
        # Reconstruir nombre con extensión
        nombre_seguro = f"{nombre_limpio}{extension.lower()}"
        
        archivo.name = nombre_seguro
        return nombre_seguro


def validar_imagen(archivo, max_mb=20):
    """
    Validación completa y robusta de archivos de imagen.
    
    Args:
        archivo: Archivo de imagen a validar
        max_mb: Tamaño máximo en MB (default: 20MB)
    
    Returns:
        Archivo validado
    
    Raises:
        ValidationError: Si el archivo no pasa alguna validación
    """
    validator = FileValidator()
    
    # 1. Validar que el archivo existe
    if not archivo:
        raise ValidationError('No se proporcionó ningún archivo.')
    
    # 2. Validar tamaño
    validator.validar_tamano(archivo, max_mb)
    
    # 3. Validar tipo MIME real (no solo extensión)
    mime = validator.validar_mime_type(archivo, FileValidator.ALLOWED_IMAGE_MIMES)
    
    # 4. Validar extensión
    extension = validator.validar_extension(archivo, FileValidator.ALLOWED_IMAGE_EXTENSIONS)
    
    # 5. Validar que la extensión coincida con el tipo MIME
    mime_to_ext = {
        'image/jpeg': ['jpg', 'jpeg'],
        'image/png': ['png'],
        'image/gif': ['gif'],
        'image/webp': ['webp'],
        'image/bmp': ['bmp'],
    }
    
    if extension not in mime_to_ext.get(mime, []):
        raise ValidationError(
            f'La extensión .{extension} no coincide con el tipo de archivo real ({mime}). '
            'Posible intento de falsificación de archivo.'
        )
    
    # 6. Sanitizar nombre del archivo
    validator.sanitizar_nombre_archivo(archivo)
    
    return archivo


def validar_video(archivo, max_mb=200):
    """
    Validación completa y robusta de archivos de video.
    
    Args:
        archivo: Archivo de video a validar
        max_mb: Tamaño máximo en MB (default: 200MB)
    
    Returns:
        Archivo validado
    
    Raises:
        ValidationError: Si el archivo no pasa alguna validación
    """
    validator = FileValidator()
    
    # 1. Validar que el archivo existe
    if not archivo:
        raise ValidationError('No se proporcionó ningún archivo de video.')
    
    # 2. Validar tamaño (videos pueden ser más grandes)
    validator.validar_tamano(archivo, max_mb)
    
    # 3. Validar tipo MIME real
    mime = validator.validar_mime_type(archivo, FileValidator.ALLOWED_VIDEO_MIMES)
    
    # 4. Validar extensión
    extension = validator.validar_extension(archivo, FileValidator.ALLOWED_VIDEO_EXTENSIONS)
    
    # 5. Validar que la extensión coincida con el tipo MIME
    mime_to_ext = {
        'video/mp4': ['mp4'],
        'video/mpeg': ['mpeg'],
        'video/quicktime': ['mov'],
        'video/x-msvideo': ['avi'],
        'video/webm': ['webm'],
    }
    
    if extension not in mime_to_ext.get(mime, []):
        raise ValidationError(
            f'La extensión .{extension} no coincide con el tipo de archivo real ({mime}). '
            'Posible intento de falsificación de archivo.'
        )
    
    # 6. Sanitizar nombre del archivo
    validator.sanitizar_nombre_archivo(archivo)
    
    return archivo


def validar_documento(archivo, max_mb=10):
    """
    Validación completa y robusta de documentos (PDF, DOC, DOCX).
    
    Args:
        archivo: Archivo de documento a validar
        max_mb: Tamaño máximo en MB (default: 10MB)
    
    Returns:
        Archivo validado
    
    Raises:
        ValidationError: Si el archivo no pasa alguna validación
    """
    validator = FileValidator()
    
    # 1. Validar que el archivo existe
    if not archivo:
        raise ValidationError('No se proporcionó ningún documento.')
    
    # 2. Validar tamaño
    validator.validar_tamano(archivo, max_mb)
    
    # 3. Validar tipo MIME real
    mime = validator.validar_mime_type(archivo, FileValidator.ALLOWED_DOCUMENT_MIMES)
    
    # 4. Validar extensión
    extension = validator.validar_extension(archivo, FileValidator.ALLOWED_DOCUMENT_EXTENSIONS)
    
    # 5. Validar que la extensión coincida con el tipo MIME
    mime_to_ext = {
        'application/pdf': ['pdf'],
        'application/msword': ['doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
    }
    
    if extension not in mime_to_ext.get(mime, []):
        raise ValidationError(
            f'La extensión .{extension} no coincide con el tipo de archivo real ({mime}). '
            'Posible intento de falsificación de archivo.'
        )
    
    # 6. Sanitizar nombre del archivo
    validator.sanitizar_nombre_archivo(archivo)
    
    return archivo


def validar_imagen_o_video(archivo):
    """
    Valida si el archivo es una imagen o un video y aplica la validación correspondiente.
    
    Args:
        archivo: Archivo a validar
    
    Returns:
        tuple: (archivo_validado, tipo) donde tipo es 'imagen' o 'video'
    
    Raises:
        ValidationError: Si el archivo no es válido
    """
    validator = FileValidator()
    
    # Leer los primeros bytes para determinar el tipo
    file_head = archivo.read(2048)
    archivo.seek(0)
    
    mime = magic.from_buffer(file_head, mime=True)
    
    # Determinar si es imagen o video
    if mime in FileValidator.ALLOWED_IMAGE_MIMES:
        return validar_imagen(archivo), 'imagen'
    elif mime in FileValidator.ALLOWED_VIDEO_MIMES:
        return validar_video(archivo), 'video'
    else:
        raise ValidationError(
            f'Tipo de archivo no permitido: {mime}. '
            'Solo se permiten imágenes y videos.'
        )


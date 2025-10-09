#!/usr/bin/env python3
"""
Comando de gestión para optimizar imágenes de propiedades existentes a WebP
"""

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from propiedades.models import Propiedad, FotoPropiedad
from core.image_optimizer import WebPOptimizer
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimiza todas las imágenes de propiedades existentes a formato WebP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la reconversión de imágenes ya optimizadas',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='Calidad de compresión WebP (1-100, default: 85)',
        )

    def handle(self, *args, **options):
        force = options['force']
        quality = options['quality']
        
        self.stdout.write(
            self.style.SUCCESS('OPTIMIZADOR DE IMAGENES DE PROPIEDADES')
        )
        self.stdout.write('=' * 60)
        
        # Optimizar imágenes principales
        self.optimize_principal_images(force, quality)
        
        # Optimizar imágenes secundarias
        self.optimize_secondary_images(force, quality)
        
        # Optimizar fotos adicionales
        self.optimize_additional_photos(force, quality)
        
        self.stdout.write('=' * 60)
        self.stdout.write(
            self.style.SUCCESS('[COMPLETADO] Optimizacion completada!')
        )

    def optimize_principal_images(self, force, quality):
        """Optimiza las imágenes principales de las propiedades"""
        self.stdout.write('\nOptimizando imagenes principales...')
        
        propiedades = Propiedad.objects.filter(imagen_principal__isnull=False)
        optimized_count = 0
        
        for propiedad in propiedades:
            if self.optimize_image_field(propiedad, 'imagen_principal', force, quality):
                optimized_count += 1
                self.stdout.write(f'  [OK] {propiedad.titulo}')
        
        self.stdout.write(f'Imagenes principales optimizadas: {optimized_count}')

    def optimize_secondary_images(self, force, quality):
        """Optimiza las imágenes secundarias de las propiedades"""
        self.stdout.write('\nOptimizando imagenes secundarias...')
        
        propiedades = Propiedad.objects.filter(imagen_secundaria__isnull=False)
        optimized_count = 0
        
        for propiedad in propiedades:
            if self.optimize_image_field(propiedad, 'imagen_secundaria', force, quality):
                optimized_count += 1
                self.stdout.write(f'  [OK] {propiedad.titulo}')
        
        self.stdout.write(f'Imagenes secundarias optimizadas: {optimized_count}')

    def optimize_additional_photos(self, force, quality):
        """Optimiza las fotos adicionales de las propiedades"""
        self.stdout.write('\nOptimizando fotos adicionales...')
        
        fotos = FotoPropiedad.objects.filter(
            tipo_medio='imagen',
            imagen__isnull=False
        )
        optimized_count = 0
        
        for foto in fotos:
            if self.optimize_foto_propiedad(foto, force, quality):
                optimized_count += 1
                self.stdout.write(f'  [OK] {foto.propiedad.titulo} - Foto {foto.orden}')
        
        self.stdout.write(f'Fotos adicionales optimizadas: {optimized_count}')

    def optimize_image_field(self, instance, field_name, force, quality):
        """Optimiza un campo de imagen específico"""
        try:
            image_field = getattr(instance, field_name)
            if not image_field:
                return False
            
            # Verificar si ya existe versión WebP
            if not force:
                webp_path = WebPOptimizer.get_webp_path(image_field.name)
                if webp_path and default_storage.exists(webp_path):
                    return False
            
            # Optimizar la imagen
            result = WebPOptimizer.optimize_image_field(
                instance,
                field_name,
                quality=quality,
                replace_original=True
            )
            
            if result['status'] == 'success':
                return True
            else:
                self.stdout.write(
                    self.style.WARNING(f'[WARN] Error optimizando {instance.titulo}: {result["message"]}')
                )
                return False
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'[ERROR] Error procesando {instance.titulo}: {str(e)}')
            )
            return False

    def optimize_foto_propiedad(self, foto, force, quality):
        """Optimiza una foto de propiedad específica"""
        try:
            if not foto.imagen:
                return False
            
            # Verificar si ya existe versión WebP
            if not force:
                webp_path = WebPOptimizer.get_webp_path(foto.imagen.name)
                if webp_path and default_storage.exists(webp_path):
                    return False
            
            # Optimizar la imagen
            result = WebPOptimizer.optimize_image_field(
                foto,
                'imagen',
                quality=quality,
                replace_original=True
            )
            
            if result['status'] == 'success':
                return True
            else:
                self.stdout.write(
                    self.style.WARNING(f'[WARN] Error optimizando foto: {result["message"]}')
                )
                return False
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'[ERROR] Error procesando foto: {str(e)}')
            )
            return False

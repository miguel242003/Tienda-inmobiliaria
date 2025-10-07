"""
Comando para optimizar todas las imágenes existentes a formato WebP
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.image_optimizer import WebPOptimizer
from propiedades.models import Propiedad, FotoPropiedad
from login.models import AdminCredentials
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimiza todas las imágenes existentes a formato WebP'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='Calidad de compresión WebP (1-100, por defecto 85)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular la optimización sin hacer cambios'
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['propiedades', 'fotos', 'admin', 'all'],
            default='all',
            help='Modelo específico a optimizar'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar re-optimización de imágenes ya optimizadas'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Tamaño del lote para procesamiento (por defecto 10)'
        )
    
    def handle(self, *args, **options):
        quality = options['quality']
        dry_run = options['dry_run']
        model_choice = options['model']
        force = options['force']
        batch_size = options['batch_size']
        
        # Validar calidad
        if not 1 <= quality <= 100:
            raise CommandError('La calidad debe estar entre 1 y 100')
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando optimización de imágenes...')
        )
        self.stdout.write(f'📊 Configuración:')
        self.stdout.write(f'   • Calidad: {quality}%')
        self.stdout.write(f'   • Modo: {"Simulación" if dry_run else "Ejecución real"}')
        self.stdout.write(f'   • Modelo: {model_choice}')
        self.stdout.write(f'   • Forzar: {"Sí" if force else "No"}')
        self.stdout.write(f'   • Lote: {batch_size} imágenes')
        self.stdout.write('')
        
        total_stats = {
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'total_original_size': 0,
            'total_webp_size': 0,
            'skipped': 0
        }
        
        # Procesar según el modelo seleccionado
        if model_choice in ['propiedades', 'all']:
            stats = self._optimize_propiedades(quality, dry_run, force, batch_size)
            self._merge_stats(total_stats, stats)
        
        if model_choice in ['fotos', 'all']:
            stats = self._optimize_fotos(quality, dry_run, force, batch_size)
            self._merge_stats(total_stats, stats)
        
        if model_choice in ['admin', 'all']:
            stats = self._optimize_admin(quality, dry_run, force, batch_size)
            self._merge_stats(total_stats, stats)
        
        # Mostrar estadísticas finales
        self._show_final_stats(total_stats, dry_run)
    
    def _optimize_propiedades(self, quality, dry_run, force, batch_size):
        """Optimiza imágenes de propiedades"""
        self.stdout.write('🏠 Optimizando imágenes de propiedades...')
        
        stats = {
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'total_original_size': 0,
            'total_webp_size': 0,
            'skipped': 0
        }
        
        # Campos de imagen en Propiedad
        image_fields = ['imagen_principal', 'imagen_secundaria']
        
        # Procesar en lotes
        propiedades = Propiedad.objects.all()
        total_propiedades = propiedades.count()
        
        for i in range(0, total_propiedades, batch_size):
            batch = propiedades[i:i + batch_size]
            
            for propiedad in batch:
                for field_name in image_fields:
                    image_field = getattr(propiedad, field_name)
                    if image_field:
                        stats['total_processed'] += 1
                        
                        # Verificar si ya está optimizada
                        if not force and WebPOptimizer.webp_exists(image_field.name):
                            stats['skipped'] += 1
                            self.stdout.write(f'   ⏭️  {propiedad.titulo} - {field_name} (ya optimizada)')
                            continue
                        
                        if not dry_run:
                            try:
                                result = WebPOptimizer.optimize_image_field(
                                    propiedad, field_name, quality
                                )
                                
                                if result['status'] == 'success':
                                    stats['successful'] += 1
                                    stats['total_original_size'] += result['original_size']
                                    stats['total_webp_size'] += result['webp_size']
                                    
                                    saved_percentage = result['saved_percentage']
                                    self.stdout.write(
                                        f'   ✅ {propiedad.titulo} - {field_name} '
                                        f'(Ahorro: {saved_percentage:.1f}%)'
                                    )
                                else:
                                    stats['errors'] += 1
                                    self.stdout.write(
                                        f'   ❌ {propiedad.titulo} - {field_name}: {result["message"]}'
                                    )
                                    
                            except Exception as e:
                                stats['errors'] += 1
                                self.stdout.write(
                                    f'   ❌ {propiedad.titulo} - {field_name}: {str(e)}'
                                )
                        else:
                            # Modo simulación
                            stats['successful'] += 1
                            self.stdout.write(f'   🔍 {propiedad.titulo} - {field_name} (simulado)')
        
        return stats
    
    def _optimize_fotos(self, quality, dry_run, force, batch_size):
        """Optimiza imágenes de fotos de propiedades"""
        self.stdout.write('📸 Optimizando fotos de propiedades...')
        
        stats = {
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'total_original_size': 0,
            'total_webp_size': 0,
            'skipped': 0
        }
        
        # Procesar en lotes
        fotos = FotoPropiedad.objects.filter(tipo_medio='imagen', imagen__isnull=False)
        total_fotos = fotos.count()
        
        for i in range(0, total_fotos, batch_size):
            batch = fotos[i:i + batch_size]
            
            for foto in batch:
                if foto.imagen:
                    stats['total_processed'] += 1
                    
                    # Verificar si ya está optimizada
                    if not force and WebPOptimizer.webp_exists(foto.imagen.name):
                        stats['skipped'] += 1
                        self.stdout.write(f'   ⏭️  {foto.propiedad.titulo} - Foto {foto.orden} (ya optimizada)')
                        continue
                    
                    if not dry_run:
                        try:
                            result = WebPOptimizer.optimize_image_field(foto, 'imagen', quality)
                            
                            if result['status'] == 'success':
                                stats['successful'] += 1
                                stats['total_original_size'] += result['original_size']
                                stats['total_webp_size'] += result['webp_size']
                                
                                saved_percentage = result['saved_percentage']
                                self.stdout.write(
                                    f'   ✅ {foto.propiedad.titulo} - Foto {foto.orden} '
                                    f'(Ahorro: {saved_percentage:.1f}%)'
                                )
                            else:
                                stats['errors'] += 1
                                self.stdout.write(
                                    f'   ❌ {foto.propiedad.titulo} - Foto {foto.orden}: {result["message"]}'
                                )
                                
                        except Exception as e:
                            stats['errors'] += 1
                            self.stdout.write(
                                f'   ❌ {foto.propiedad.titulo} - Foto {foto.orden}: {str(e)}'
                            )
                    else:
                        # Modo simulación
                        stats['successful'] += 1
                        self.stdout.write(f'   🔍 {foto.propiedad.titulo} - Foto {foto.orden} (simulado)')
        
        return stats
    
    def _optimize_admin(self, quality, dry_run, force, batch_size):
        """Optimiza imágenes de perfil de administradores"""
        self.stdout.write('👤 Optimizando fotos de perfil de administradores...')
        
        stats = {
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'total_original_size': 0,
            'total_webp_size': 0,
            'skipped': 0
        }
        
        # Procesar en lotes
        admins = AdminCredentials.objects.filter(foto_perfil__isnull=False)
        total_admins = admins.count()
        
        for i in range(0, total_admins, batch_size):
            batch = admins[i:i + batch_size]
            
            for admin in batch:
                if admin.foto_perfil:
                    stats['total_processed'] += 1
                    
                    # Verificar si ya está optimizada
                    if not force and WebPOptimizer.webp_exists(admin.foto_perfil.name):
                        stats['skipped'] += 1
                        self.stdout.write(f'   ⏭️  {admin.email} - Foto perfil (ya optimizada)')
                        continue
                    
                    if not dry_run:
                        try:
                            result = WebPOptimizer.optimize_image_field(admin, 'foto_perfil', quality)
                            
                            if result['status'] == 'success':
                                stats['successful'] += 1
                                stats['total_original_size'] += result['original_size']
                                stats['total_webp_size'] += result['webp_size']
                                
                                saved_percentage = result['saved_percentage']
                                self.stdout.write(
                                    f'   ✅ {admin.email} - Foto perfil '
                                    f'(Ahorro: {saved_percentage:.1f}%)'
                                )
                            else:
                                stats['errors'] += 1
                                self.stdout.write(
                                    f'   ❌ {admin.email} - Foto perfil: {result["message"]}'
                                )
                                
                        except Exception as e:
                            stats['errors'] += 1
                            self.stdout.write(
                                f'   ❌ {admin.email} - Foto perfil: {str(e)}'
                            )
                    else:
                        # Modo simulación
                        stats['successful'] += 1
                        self.stdout.write(f'   🔍 {admin.email} - Foto perfil (simulado)')
        
        return stats
    
    def _merge_stats(self, total_stats, stats):
        """Combina estadísticas"""
        for key in total_stats:
            total_stats[key] += stats[key]
    
    def _show_final_stats(self, stats, dry_run):
        """Muestra estadísticas finales"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS FINALES'))
        self.stdout.write('=' * 50)
        
        if dry_run:
            self.stdout.write('🔍 MODO SIMULACIÓN - No se realizaron cambios reales')
            self.stdout.write('')
        
        self.stdout.write(f'📈 Total procesadas: {stats["total_processed"]}')
        self.stdout.write(f'✅ Exitosas: {stats["successful"]}')
        self.stdout.write(f'⏭️  Omitidas: {stats["skipped"]}')
        self.stdout.write(f'❌ Errores: {stats["errors"]}')
        
        if stats['total_original_size'] > 0:
            total_saved = stats['total_original_size'] - stats['total_webp_size']
            saved_percentage = (total_saved / stats['total_original_size']) * 100
            
            self.stdout.write('')
            self.stdout.write('💾 OPTIMIZACIÓN DE ESPACIO:')
            self.stdout.write(f'   • Tamaño original: {stats["total_original_size"]:,} bytes')
            self.stdout.write(f'   • Tamaño WebP: {stats["total_webp_size"]:,} bytes')
            self.stdout.write(f'   • Espacio ahorrado: {total_saved:,} bytes ({saved_percentage:.1f}%)')
            
            # Convertir a MB
            original_mb = stats['total_original_size'] / (1024 * 1024)
            webp_mb = stats['total_webp_size'] / (1024 * 1024)
            saved_mb = total_saved / (1024 * 1024)
            
            self.stdout.write('')
            self.stdout.write('📏 EN MEGABYTES:')
            self.stdout.write(f'   • Original: {original_mb:.2f} MB')
            self.stdout.write(f'   • WebP: {webp_mb:.2f} MB')
            self.stdout.write(f'   • Ahorro: {saved_mb:.2f} MB')
        
        if stats['errors'] > 0:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'⚠️  Se encontraron {stats["errors"]} errores durante la optimización'))
        
        if not dry_run and stats['successful'] > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🎉 ¡Optimización completada exitosamente!'))
            self.stdout.write('💡 Las imágenes WebP se servirán automáticamente cuando estén disponibles')

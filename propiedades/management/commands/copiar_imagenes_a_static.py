"""
Comando de gestión para copiar todas las imágenes de propiedades a static
"""
from django.core.management.base import BaseCommand
from propiedades.models import Propiedad
from core.utils import copiar_imagen_a_static
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Copia todas las imágenes de propiedades (principal y secundaria) a static/images/propiedades/ como WebP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Slug de una propiedad específica para copiar (opcional)',
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar copia incluso si el archivo ya existe en static',
        )

    def handle(self, *args, **options):
        slug_especifico = options.get('slug')
        forzar = options.get('forzar', False)
        
        if slug_especifico:
            propiedades = Propiedad.objects.filter(slug=slug_especifico)
            if not propiedades.exists():
                self.stdout.write(self.style.ERROR(f'No se encontró propiedad con slug: {slug_especifico}'))
                return
        else:
            propiedades = Propiedad.objects.all()
        
        total_propiedades = propiedades.count()
        self.stdout.write(self.style.SUCCESS(f'Procesando {total_propiedades} propiedades...'))
        
        copiadas = 0
        errores = 0
        omitidas = 0
        
        for propiedad in propiedades:
            self.stdout.write(f'\n--- Procesando: {propiedad.titulo} (slug: {propiedad.slug}) ---')
            
            # Copiar imagen principal
            if propiedad.imagen_principal:
                if default_storage.exists(propiedad.imagen_principal.name):
                    try:
                        nombre_archivo = f"{propiedad.slug}-principal"
                        resultado = copiar_imagen_a_static(
                            propiedad.imagen_principal,
                            nombre_archivo,
                            quality=85
                        )
                        if resultado:
                            self.stdout.write(self.style.SUCCESS(f'  ✓ Imagen principal copiada: {resultado}'))
                            copiadas += 1
                        else:
                            self.stdout.write(self.style.WARNING(f'  ✗ No se pudo copiar imagen principal'))
                            errores += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ Error al copiar imagen principal: {e}'))
                        errores += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Imagen principal no existe en storage: {propiedad.imagen_principal.name}'))
                    errores += 1
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ Propiedad sin imagen principal'))
                omitidas += 1
            
            # Copiar imagen secundaria
            if propiedad.imagen_secundaria:
                if default_storage.exists(propiedad.imagen_secundaria.name):
                    try:
                        nombre_archivo = f"{propiedad.slug}-secundaria"
                        resultado = copiar_imagen_a_static(
                            propiedad.imagen_secundaria,
                            nombre_archivo,
                            quality=85
                        )
                        if resultado:
                            self.stdout.write(self.style.SUCCESS(f'  ✓ Imagen secundaria copiada: {resultado}'))
                            copiadas += 1
                        else:
                            self.stdout.write(self.style.WARNING(f'  ✗ No se pudo copiar imagen secundaria'))
                            errores += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ Error al copiar imagen secundaria: {e}'))
                        errores += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Imagen secundaria no existe en storage: {propiedad.imagen_secundaria.name}'))
                    errores += 1
            else:
                omitidas += 1
        
        # Resumen
        self.stdout.write(self.style.SUCCESS(f'\n=== RESUMEN ==='))
        self.stdout.write(self.style.SUCCESS(f'Imágenes copiadas exitosamente: {copiadas}'))
        self.stdout.write(self.style.WARNING(f'Errores: {errores}'))
        self.stdout.write(self.style.WARNING(f'Omitidas (sin imagen): {omitidas}'))


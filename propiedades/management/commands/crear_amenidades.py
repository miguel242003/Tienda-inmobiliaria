from django.core.management.base import BaseCommand
from propiedades.models import Amenidad

class Command(BaseCommand):
    help = 'Crea las amenidades iniciales para las propiedades'

    def handle(self, *args, **options):
        amenidades_data = [
            {
                'nombre': 'Piscina privada',
                'icono': 'fa-swimming-pool',
                'descripcion': 'Piscina privada disponible para los huéspedes'
            },
            {
                'nombre': 'TV',
                'icono': 'fa-tv',
                'descripcion': 'Televisor disponible en la propiedad'
            },
            {
                'nombre': 'Lavavajillas',
                'icono': 'fa-utensils',
                'descripcion': 'Lavavajillas incluido en la cocina'
            },
            {
                'nombre': 'Aire acondicionado',
                'icono': 'fa-snowflake',
                'descripcion': 'Sistema de aire acondicionado disponible'
            },
            {
                'nombre': 'Lavadora',
                'icono': 'fa-tshirt',
                'descripcion': 'Lavadora disponible para los huéspedes'
            },
            {
                'nombre': 'WiFi',
                'icono': 'fa-wifi',
                'descripcion': 'Conexión WiFi gratuita incluida'
            },
            {
                'nombre': 'Estacionamiento',
                'icono': 'fa-car',
                'descripcion': 'Lugar de estacionamiento disponible'
            }
        ]

        for amenidad_data in amenidades_data:
            amenidad, created = Amenidad.objects.get_or_create(
                nombre=amenidad_data['nombre'],
                defaults={
                    'icono': amenidad_data['icono'],
                    'descripcion': amenidad_data['descripcion']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Amenidad creada: {amenidad.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Amenidad ya existe: {amenidad.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS('Proceso de creación de amenidades completado')
        )

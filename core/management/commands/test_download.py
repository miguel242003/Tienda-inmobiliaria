from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import RequestFactory
from core.models import CVSubmission
from core.views import download_cv


class Command(BaseCommand):
    help = 'Prueba la funcionalidad de descarga de CV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cv-id',
            type=int,
            help='ID del CV a probar',
            default=3
        )

    def handle(self, *args, **options):
        cv_id = options['cv_id']
        
        self.stdout.write(f'Probando descarga de CV ID: {cv_id}')
        
        try:
            # Verificar que el CV existe
            cv = CVSubmission.objects.get(id=cv_id)
            self.stdout.write(f'✅ CV encontrado: {cv.nombre_completo}')
            self.stdout.write(f'📁 Archivo: {cv.cv_file.name}')
            self.stdout.write(f'📏 Tamaño: {cv.get_file_size()}')
            
            # Probar la URL
            url = reverse('core:download_cv', args=[cv_id])
            self.stdout.write(f'🔗 URL generada: {url}')
            
            # Simular una request
            factory = RequestFactory()
            request = factory.get(url)
            
            # Probar la vista
            response = download_cv(request, cv_id)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ Descarga funcionando correctamente'))
                self.stdout.write(f'📄 Content-Type: {response.get("Content-Type")}')
                self.stdout.write(f'📥 Content-Disposition: {response.get("Content-Disposition")}')
            else:
                self.stdout.write(self.style.ERROR(f'❌ Error en descarga: {response.status_code}'))
                
        except CVSubmission.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ CV con ID {cv_id} no encontrado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            
            # Mostrar más detalles del error
            import traceback
            self.stdout.write('\nDetalles del error:')
            self.stdout.write(traceback.format_exc())

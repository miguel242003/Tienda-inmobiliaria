from django.core.management.base import BaseCommand
from django.test import Client
from propiedades.models import Propiedad


class Command(BaseCommand):
    help = 'Prueba que la función showTab esté disponible en el JavaScript'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Probando disponibilidad de función showTab...'))
        
        # Obtener una propiedad de prueba
        try:
            propiedad = Propiedad.objects.first()
            if not propiedad:
                self.stdout.write(self.style.ERROR('❌ No hay propiedades en la base de datos'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error obteniendo propiedad: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'📋 Usando propiedad: {propiedad.titulo}'))
        
        # Crear cliente de prueba
        client = Client()
        
        # Obtener la página de detalle
        try:
            response = client.get(f'/propiedades/{propiedad.id}/')
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ Página de detalle cargada correctamente'))
                
                # Verificar que la función showTab esté en el contenido
                content = response.content.decode('utf-8')
                
                if 'function showTab(tabName)' in content:
                    self.stdout.write(self.style.SUCCESS('✅ Función showTab encontrada en el HTML'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Función showTab NO encontrada en el HTML'))
                
                if 'data-tab=' in content:
                    self.stdout.write(self.style.SUCCESS('✅ Botones con data-tab encontrados'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Botones con data-tab NO encontrados'))
                
                if 'addEventListener(\'click\', function()' in content:
                    self.stdout.write(self.style.SUCCESS('✅ Event listeners para pestañas encontrados'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Event listeners para pestañas NO encontrados'))
                
                # Verificar que no haya errores de sintaxis obvios
                if 'window.onclick = function(event)' in content:
                    count = content.count('window.onclick = function(event)')
                    if count == 1:
                        self.stdout.write(self.style.SUCCESS('✅ Solo una función window.onclick encontrada'))
                    else:
                        self.stdout.write(self.style.WARNING(f'⚠️ {count} funciones window.onclick encontradas (puede causar conflictos)'))
                
            else:
                self.stdout.write(self.style.ERROR(f'❌ Error cargando página: {response.status_code}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error en la prueba: {e}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Prueba de JavaScript completada'))

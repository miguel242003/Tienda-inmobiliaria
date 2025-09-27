from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from propiedades.models import Propiedad
from core.models import ContactSubmission
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Prueba el formulario de contacto integrado en la vista de detalle de propiedad'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Iniciando prueba del formulario integrado...'))
        
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
        
        # Datos del formulario
        fecha_entrada = date.today() + timedelta(days=7)
        fecha_salida = fecha_entrada + timedelta(days=3)
        
        form_data = {
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@ejemplo.com',
            'telefono': '+1 555 987 654',
            'asunto': 'alquiler',
            'mensaje': f'Hola, me interesa alquilar la propiedad "{propiedad.titulo}". '
                      f'¿Podrían contactarme para coordinar una visita y conocer más detalles sobre el alquiler? '
                      f'Entrada: 13:00 PM, Salida: 10:00 AM. '
                      f'Gracias.',
            'fecha_entrada': fecha_entrada,
            'fecha_salida': fecha_salida,
        }
        
        # Simular envío del formulario
        self.stdout.write(self.style.WARNING('📤 Enviando formulario...'))
        
        try:
            response = client.post(f'/propiedades/{propiedad.id}/', data=form_data)
            
            if response.status_code == 302:  # Redirect después del éxito
                self.stdout.write(self.style.SUCCESS('✅ Formulario enviado exitosamente'))
                
                # Verificar que se creó el registro en la base de datos
                contact_submissions = ContactSubmission.objects.filter(
                    nombre='Juan Pérez',
                    email='juan.perez@ejemplo.com'
                ).order_by('-fecha_envio')
                
                if contact_submissions.exists():
                    submission = contact_submissions.first()
                    self.stdout.write(self.style.SUCCESS(f'✅ Registro creado en BD: ID {submission.id}'))
                    self.stdout.write(self.style.SUCCESS(f'📧 Email: {submission.email}'))
                    self.stdout.write(self.style.SUCCESS(f'📅 Fecha entrada: {submission.fecha_entrada}'))
                    self.stdout.write(self.style.SUCCESS(f'📅 Fecha salida: {submission.fecha_salida}'))
                    
                    # Verificar que el mensaje contiene información de la propiedad
                    if propiedad.titulo in submission.mensaje:
                        self.stdout.write(self.style.SUCCESS('✅ Información de propiedad incluida en el mensaje'))
                    else:
                        self.stdout.write(self.style.WARNING('⚠️ Información de propiedad no encontrada en el mensaje'))
                else:
                    self.stdout.write(self.style.ERROR('❌ No se encontró el registro en la base de datos'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Error en la respuesta: {response.status_code}'))
                if hasattr(response, 'content'):
                    self.stdout.write(self.style.ERROR(f'Contenido: {response.content.decode()}'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error enviando formulario: {e}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Prueba del formulario integrado completada'))
        self.stdout.write(self.style.SUCCESS(f'🏠 Propiedad utilizada: {propiedad.titulo} (ID: {propiedad.id})'))

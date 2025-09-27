from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from core.models import CVSubmission
from datetime import datetime


class Command(BaseCommand):
    help = 'Prueba el envío de emails de CV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de destino para la prueba',
            default='xmiguelastorgax@gmail.com'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(f'Probando envío de emails de CV a: {email}')
        
        try:
            # Simular un CV submission
            cv_data = {
                'id': 999,  # ID de prueba
                'nombre_completo': 'Juan Pérez (Prueba)',
                'email': email,
                'telefono': '+54 9 11 1234-5678',
                'posicion_interes': 'agente_inmobiliario',
                'anos_experiencia': '3-5',
                'nivel_educativo': 'universitario',
                'carta_presentacion': 'Esta es una carta de presentación de prueba para verificar que el sistema de emails de CV funciona correctamente.',
                'fecha_envio': datetime.now()
            }
            
            # Probar email de confirmación al candidato
            self.stdout.write('📧 Enviando email de confirmación al candidato...')
            
            subject = 'Confirmación de Recepción de CV - Tienda Inmobiliaria'
            
            html_content = render_to_string('core/emails/cv_confirmation.html', {
                'cv_submission': type('obj', (object,), cv_data)(),
                'site_name': 'Tienda Inmobiliaria'
            })
            
            text_content = f"""
            Confirmación de Recepción de CV - Tienda Inmobiliaria
            
            Hola {cv_data['nombre_completo']},
            
            Hemos recibido tu currículum para la posición de Agente Inmobiliario.
            
            Detalles de tu aplicación:
            - Nombre: {cv_data['nombre_completo']}
            - Email: {cv_data['email']}
            - Posición: Agente Inmobiliario
            - Fecha de envío: {cv_data['fecha_envio'].strftime('%d/%m/%Y %H:%M')}
            
            Revisaremos tu perfil y te contactaremos pronto si coincide con nuestras necesidades.
            
            Gracias por tu interés en formar parte de nuestro equipo.
            
            Saludos,
            Equipo de Recursos Humanos
            Tienda Inmobiliaria
            """
            
            result1 = send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_content,
                fail_silently=False,
            )
            
            if result1:
                self.stdout.write(self.style.SUCCESS('✅ Email de confirmación enviado'))
            else:
                self.stdout.write(self.style.ERROR('❌ Error en email de confirmación'))
            
            # Probar email de notificación al administrador
            self.stdout.write('📧 Enviando email de notificación al administrador...')
            
            subject = f'Nuevo CV Recibido - {cv_data["nombre_completo"]}'
            
            html_content = render_to_string('core/emails/cv_notification.html', {
                'cv_submission': type('obj', (object,), cv_data)(),
                'site_name': 'Tienda Inmobiliaria',
                'request': type('obj', (object,), {'get_host': lambda: 'localhost:8000'})(),
                'download_url': f'http://localhost:8000/download-cv/{cv_data["id"]}/'
            })
            
            text_content = f"""
            Nuevo CV Recibido - Tienda Inmobiliaria
            
            Se ha recibido un nuevo currículum:
            
            Información del Candidato:
            - Nombre: {cv_data['nombre_completo']}
            - Email: {cv_data['email']}
            - Teléfono: {cv_data['telefono']}
            - Posición de Interés: Agente Inmobiliario
            - Años de Experiencia: 3-5 años
            - Nivel Educativo: Universitario
            - Fecha de Envío: {cv_data['fecha_envio'].strftime('%d/%m/%Y %H:%M')}
            
            Carta de Presentación:
            {cv_data['carta_presentacion']}
            
            Por favor revisa el CV en el panel de administración.
            
            Saludos,
            Sistema de Recursos Humanos
            """
            
            admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            result2 = send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                html_message=html_content,
                fail_silently=False,
            )
            
            if result2:
                self.stdout.write(self.style.SUCCESS('✅ Email de notificación enviado'))
            else:
                self.stdout.write(self.style.ERROR('❌ Error en email de notificación'))
            
            if result1 and result2:
                self.stdout.write(self.style.SUCCESS('🎉 Todos los emails enviados exitosamente!'))
                self.stdout.write('Revisa tu bandeja de entrada (y spam) en unos minutos.')
                self.stdout.write('Deberías recibir 2 emails:')
                self.stdout.write('1. Confirmación de recepción de CV')
                self.stdout.write('2. Notificación de nuevo CV (como administrador)')
            else:
                self.stdout.write(self.style.ERROR('❌ Algunos emails fallaron'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al enviar emails de CV: {str(e)}')
            )
            
            # Mostrar más detalles del error
            import traceback
            self.stdout.write('\nDetalles del error:')
            self.stdout.write(traceback.format_exc())

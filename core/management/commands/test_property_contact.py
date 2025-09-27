from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from core.models import ContactSubmission
from propiedades.models import Propiedad
from datetime import datetime

class Command(BaseCommand):
    help = 'Prueba el sistema de contacto desde detalle de propiedad'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Iniciando prueba del sistema de contacto desde detalle de propiedad...'))
        
        # Obtener una propiedad de ejemplo
        try:
            propiedad = Propiedad.objects.first()
            if not propiedad:
                self.stdout.write(self.style.ERROR('❌ No hay propiedades en la base de datos'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error obteniendo propiedad: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'📋 Usando propiedad: {propiedad.titulo}'))
        
        # Crear datos de prueba con información de la propiedad
        from datetime import date, timedelta
        fecha_entrada = date.today() + timedelta(days=7)  # 7 días en el futuro
        fecha_salida = fecha_entrada + timedelta(days=3)  # 3 días después de la entrada
        
        contact_data = {
            'nombre': 'María González',
            'email': 'maria.gonzalez@ejemplo.com',
            'telefono': '+1 555 123 456',
            'asunto': 'alquiler',
            'mensaje': f'Hola, me interesa alquilar la propiedad "{propiedad.titulo}". '
                      f'¿Podrían contactarme para coordinar una visita y conocer más detalles sobre el alquiler? '
                      f'Entrada: 13:00 PM, Salida: 10:00 AM. '
                      f'Gracias.\n\n'
                      f'--- Información de la Propiedad ---\n'
                      f'ID: {propiedad.id}\n'
                      f'Título: {propiedad.titulo}',
            'fecha_entrada': fecha_entrada,
            'fecha_salida': fecha_salida,
            'fecha_envio': datetime.now()
        }
        
        # Crear instancia de prueba
        contact_submission = ContactSubmission(**contact_data)
        contact_submission.id = 999  # ID temporal para pruebas
        
        self.stdout.write(self.style.SUCCESS('📧 Probando email de confirmación al cliente...'))
        
        # Probar email de confirmación
        try:
            subject = 'Confirmación de Recepción de Mensaje - Tienda Inmobiliaria'
            
            html_content = render_to_string('core/emails/contact_confirmation.html', {
                'contact_submission': contact_submission,
                'site_name': 'Tienda Inmobiliaria'
            })
            
            text_content = f"""
            Confirmación de Recepción de Mensaje - Tienda Inmobiliaria
            
            Hola {contact_submission.nombre},
            
            Hemos recibido tu mensaje sobre: {contact_submission.get_asunto_display()}
            
            Detalles de tu consulta:
            - Nombre: {contact_submission.nombre}
            - Email: {contact_submission.email}
            - Teléfono: {contact_submission.telefono or 'No proporcionado'}
            - Asunto: {contact_submission.get_asunto_display()}
            - Fecha de envío: {contact_submission.fecha_envio.strftime('%d/%m/%Y %H:%M')}
            
            Tu mensaje:
            {contact_submission.mensaje}
            
            Revisaremos tu consulta y te contactaremos pronto.
            
            Gracias por contactarnos.
            
            Saludos,
            Equipo de Atención al Cliente
            Tienda Inmobiliaria
            """
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_submission.email],
                html_message=html_content,
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('✅ Email de confirmación enviado exitosamente'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error enviando email de confirmación: {e}'))
        
        self.stdout.write(self.style.SUCCESS('📧 Probando email de notificación al administrador...'))
        
        # Probar email de notificación
        try:
            subject = f'Nuevo Mensaje de Contacto - {contact_submission.nombre}'
            
            html_content = render_to_string('core/emails/contact_notification.html', {
                'contact_submission': contact_submission,
                'site_name': 'Tienda Inmobiliaria'
            })
            
            text_content = f"""
            Nuevo Mensaje de Contacto - Tienda Inmobiliaria
            
            Se ha recibido un nuevo mensaje de contacto:
            
            Información del Cliente:
            - Nombre: {contact_submission.nombre}
            - Email: {contact_submission.email}
            - Teléfono: {contact_submission.telefono or 'No proporcionado'}
            - Asunto: {contact_submission.get_asunto_display()}
            - Fecha de envío: {contact_submission.fecha_envio.strftime('%d/%m/%Y %H:%M')}
            
            Mensaje:
            {contact_submission.mensaje}
            
            Saludos,
            Sistema de Contacto
            """
            
            admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                html_message=html_content,
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('✅ Email de notificación enviado exitosamente'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error enviando email de notificación: {e}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Prueba del sistema de contacto desde detalle de propiedad completada'))
        self.stdout.write(self.style.WARNING('📬 Revisa tu bandeja de entrada para verificar los emails'))
        self.stdout.write(self.style.SUCCESS(f'🏠 Propiedad utilizada: {propiedad.titulo} (ID: {propiedad.id})'))

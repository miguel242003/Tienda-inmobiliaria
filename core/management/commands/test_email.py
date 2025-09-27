from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Prueba el envío de emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de destino para la prueba',
            default='xmiguelastorgax@gmail.com'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(f'Probando envío de email a: {email}')
        self.stdout.write(f'Configuración SMTP:')
        self.stdout.write(f'  HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'  PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'  TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'  FROM: {settings.DEFAULT_FROM_EMAIL}')
        
        try:
            # Email simple de prueba
            subject = 'Prueba de Email - Tienda Inmobiliaria'
            message = '''
            Este es un email de prueba para verificar que la configuración de email funciona correctamente.
            
            Si recibes este email, significa que:
            - La configuración SMTP está correcta
            - Gmail está aceptando los emails
            - El sistema de envío funciona
            
            Fecha: {}
            
            Saludos,
            Sistema de Pruebas
            '''.format(settings.EMAIL_HOST_USER)
            
            html_message = '''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">📧 Prueba de Email - Tienda Inmobiliaria</h2>
                <p>Este es un email de prueba para verificar que la configuración de email funciona correctamente.</p>
                
                <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin: 0;">✅ Si recibes este email, significa que:</h3>
                    <ul>
                        <li>La configuración SMTP está correcta</li>
                        <li>Gmail está aceptando los emails</li>
                        <li>El sistema de envío funciona</li>
                    </ul>
                </div>
                
                <p><strong>Fecha:</strong> {}</p>
                <p><strong>Remitente:</strong> {}</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 14px;">
                    Saludos,<br>
                    Sistema de Pruebas - Tienda Inmobiliaria
                </p>
            </body>
            </html>
            '''.format(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_USER)
            
            # Enviar email
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Email enviado exitosamente a {email}')
                )
                self.stdout.write('Revisa tu bandeja de entrada (y spam) en unos minutos.')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Error: No se pudo enviar el email')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al enviar email: {str(e)}')
            )
            self.stdout.write('Posibles causas:')
            self.stdout.write('1. Contraseña de aplicación incorrecta')
            self.stdout.write('2. Gmail bloqueando el envío')
            self.stdout.write('3. Configuración SMTP incorrecta')
            self.stdout.write('4. Problemas de conectividad')
            
            # Mostrar más detalles del error
            import traceback
            self.stdout.write('\nDetalles del error:')
            self.stdout.write(traceback.format_exc())

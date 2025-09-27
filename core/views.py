from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str
import os
from propiedades.models import Propiedad
from .forms import CVSubmissionForm, ContactSubmissionForm
from .models import CVSubmission, ContactSubmission

# Crea tus vistas aquí.

def home(request):
    """Vista principal del home"""
    try:
        # SECCIÓN DE PROPIEDADES EN VENTA COMENTADA PARA FUTURA ACTUALIZACIÓN
        # propiedades_destacadas = Propiedad.objects.filter(
        #     estado='disponible',
        #     operacion='venta'
        # ).order_by('-fecha_creacion')[:8]
        
        # Obtener propiedades en alquiler (alquiler y alquiler temporal)
        propiedades_alquiler = Propiedad.objects.filter(
            estado='disponible',
            operacion__in=['alquiler', 'alquiler_temporal']
        ).order_by('-fecha_creacion')[:2]
        
        # Contar propiedades por tipo de operación
        propiedades_alquiler_count = Propiedad.objects.filter(
            estado='disponible',
            operacion='alquiler'
        ).count()
        
        propiedades_alquiler_temporal_count = Propiedad.objects.filter(
            estado='disponible',
            operacion='alquiler_temporal'
        ).count()
        
        # Obtener reseñas aprobadas para mostrar en testimonios
        from propiedades.models import Resena
        resenas_aprobadas = Resena.objects.filter(
            estado='aprobada'
        ).select_related('propiedad').order_by('-fecha_creacion')[:6]
        
        # Debug: imprimir información sobre las propiedades de alquiler encontradas
        print(f"DEBUG: Propiedades en alquiler encontradas: {propiedades_alquiler.count()}")
        print(f"DEBUG: Propiedades de alquiler: {propiedades_alquiler_count}")
        print(f"DEBUG: Propiedades de alquiler temporal: {propiedades_alquiler_temporal_count}")
        for p in propiedades_alquiler:
            print(f"DEBUG: - {p.titulo} (Operación: {p.operacion}, Estado: {p.estado})")
        
        # Estadísticas básicas (solo para alquiler)
        # Comentado para futura actualización
        # total_propiedades = Propiedad.objects.count()
        # propiedades_disponibles = Propiedad.objects.filter(estado='disponible').count()
        
        context = {
            'propiedades_alquiler': propiedades_alquiler,
            'propiedades_alquiler_count': propiedades_alquiler_count,
            'propiedades_alquiler_temporal_count': propiedades_alquiler_temporal_count,
            'hay_propiedades_alquiler': len(propiedades_alquiler) > 0,
            'resenas_aprobadas': resenas_aprobadas,
        }
        
    except Exception as e:
        # En caso de error, crear un contexto básico
        context = {
            'propiedades_alquiler': [],
            'propiedades_alquiler_count': 0,
            'propiedades_alquiler_temporal_count': 0,
            'hay_propiedades_alquiler': False,
            'resenas_aprobadas': [],
            'error_message': 'Error al cargar las propiedades'
        }
        print(f"Error en vista home: {e}")
    
    return render(request, 'core/home.html', context)

def about(request):
    """Vista sobre nosotros"""
    return render(request, 'core/about.html')

def contact(request):
    """Vista de contacto"""
    if request.method == 'POST':
        form = ContactSubmissionForm(request.POST)
        if form.is_valid():
            try:
                # Guardar el mensaje de contacto
                contact_submission = form.save()
                
                # Obtener información de la propiedad si viene del formulario de detalle
                propiedad_id = request.POST.get('propiedad_id')
                propiedad_titulo = request.POST.get('propiedad_titulo')
                
                if propiedad_id and propiedad_titulo:
                    # Agregar información de la propiedad al mensaje
                    mensaje_original = contact_submission.mensaje
                    mensaje_con_propiedad = f"{mensaje_original}\n\n--- Información de la Propiedad ---\nID: {propiedad_id}\nTítulo: {propiedad_titulo}"
                    contact_submission.mensaje = mensaje_con_propiedad
                    contact_submission.save()
                
                # Enviar email de confirmación al usuario
                send_contact_confirmation_email(contact_submission)
                
                # Enviar email de notificación al administrador
                send_contact_notification_email(contact_submission)
                
                messages.success(
                    request, 
                    '¡Mensaje enviado exitosamente! Hemos recibido tu consulta y te contactaremos pronto.'
                )
                return redirect('core:contact')
                
            except Exception as e:
                messages.error(
                    request, 
                    f'Error al enviar el mensaje: {str(e)}. Por favor intenta nuevamente o contacta directamente con nosotros.'
                )
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ContactSubmissionForm()
    
    return render(request, 'core/contact.html', {'form': form})

def consorcio(request):
    """Vista para la página de Consorcio"""
    return render(request, 'core/consorcio.html')

def cv(request):
    """Vista para envío de currículum"""
    if request.method == 'POST':
        form = CVSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Guardar el CV
                cv_submission = form.save()
                
                # Enviar email de confirmación al candidato
                send_cv_confirmation_email(cv_submission)
                
                # Enviar email de notificación al administrador
                send_cv_notification_email(cv_submission)
                
                messages.success(
                    request, 
                    '¡CV enviado exitosamente! Hemos recibido tu currículum y te contactaremos pronto si tu perfil coincide con nuestras necesidades.'
                )
                return redirect('core:cv')
                
            except Exception as e:
                messages.error(
                    request, 
                    f'Error al enviar el CV: {str(e)}. Por favor intenta nuevamente o contacta directamente con nosotros.'
                )
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CVSubmissionForm()
    
    return render(request, 'core/cv.html', {'form': form})


def send_cv_confirmation_email(cv_submission):
    """Envía email de confirmación al candidato"""
    subject = 'Confirmación de Recepción de CV - Tienda Inmobiliaria'
    
    # Crear el contenido del email
    html_content = render_to_string('core/emails/cv_confirmation.html', {
        'cv_submission': cv_submission,
        'site_name': 'Tienda Inmobiliaria'
    })
    
    text_content = f"""
    Confirmación de Recepción de CV - Tienda Inmobiliaria
    
    Hola {cv_submission.nombre_completo},
    
    Hemos recibido tu currículum para la posición de {cv_submission.get_posicion_interes_display()}.
    
    Detalles de tu aplicación:
    - Nombre: {cv_submission.nombre_completo}
    - Email: {cv_submission.email}
    - Posición: {cv_submission.get_posicion_interes_display()}
    - Fecha de envío: {cv_submission.fecha_envio.strftime('%d/%m/%Y %H:%M')}
    
    Revisaremos tu perfil y te contactaremos pronto si coincide con nuestras necesidades.
    
    Gracias por tu interés en formar parte de nuestro equipo.
    
    Saludos,
    Equipo de Recursos Humanos
    Tienda Inmobiliaria
    """
    
    try:
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cv_submission.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email de confirmación: {e}")
        return False


def send_cv_notification_email(cv_submission):
    """Envía email de notificación al administrador"""
    subject = f'Nuevo CV Recibido - {cv_submission.nombre_completo}'
    
    # Crear el contenido del email
    html_content = render_to_string('core/emails/cv_notification.html', {
        'cv_submission': cv_submission,
        'site_name': 'Tienda Inmobiliaria',
        'request': type('obj', (object,), {'get_host': lambda: 'localhost:8000'})(),
        'download_url': f'http://localhost:8000/download-cv/{cv_submission.id}/'
    })
    
    text_content = f"""
    Nuevo CV Recibido - Tienda Inmobiliaria
    
    Se ha recibido un nuevo currículum:
    
    Información del Candidato:
    - Nombre: {cv_submission.nombre_completo}
    - Email: {cv_submission.email}
    - Teléfono: {cv_submission.telefono or 'No proporcionado'}
    - Posición de Interés: {cv_submission.get_posicion_interes_display()}
    - Años de Experiencia: {cv_submission.get_anos_experiencia_display() or 'No especificado'}
    - Nivel Educativo: {cv_submission.get_nivel_educativo_display() or 'No especificado'}
    - Fecha de Envío: {cv_submission.fecha_envio.strftime('%d/%m/%Y %H:%M')}
    
    Archivo CV: {cv_submission.cv_file.name}
    Tamaño: {cv_submission.get_file_size()}
    
    Para descargar el CV, visita: http://localhost:8000/download-cv/{cv_submission.id}/
    
    Carta de Presentación:
    {cv_submission.carta_presentacion or 'No incluida'}
    
    Saludos,
    Sistema de Recursos Humanos
    """
    
    try:
        # Enviar al email del administrador (configurado en settings)
        admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email de notificación: {e}")
        return False


def download_cv(request, cv_id):
    """Vista para descargar archivos CV"""
    try:
        # Obtener el CV o devolver 404 si no existe
        cv_submission = get_object_or_404(CVSubmission, id=cv_id)
        
        # Verificar que el archivo existe
        if not cv_submission.cv_file:
            raise Http404("Archivo CV no encontrado")
        
        # Obtener la ruta del archivo
        file_path = cv_submission.cv_file.path
        
        # Verificar que el archivo existe físicamente
        if not os.path.exists(file_path):
            raise Http404("Archivo CV no encontrado en el servidor")
        
        # Obtener el nombre del archivo original
        filename = os.path.basename(cv_submission.cv_file.name)
        
        # Leer el archivo
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            
            # Configurar headers para la descarga
            response['Content-Disposition'] = f'attachment; filename="{smart_str(filename)}"'
            response['Content-Length'] = os.path.getsize(file_path)
            
            return response
            
    except Exception as e:
        print(f"Error descargando CV: {e}")
        raise Http404("Error al descargar el archivo CV")


def send_contact_confirmation_email(contact_submission):
    """Envía email de confirmación al usuario que envió el mensaje de contacto"""
    subject = 'Confirmación de Recepción de Mensaje - Tienda Inmobiliaria'
    
    # Usar la fecha real de envío
    fecha_corregida = contact_submission.fecha_envio
    
    # Crear el contenido del email
    html_content = render_to_string('core/emails/contact_confirmation.html', {
        'contact_submission': contact_submission,
        'fecha_corregida': fecha_corregida,
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
    - Fecha de envío: {fecha_corregida.strftime('%d/%m/%Y %H:%M')}
    
    Tu mensaje:
    {contact_submission.mensaje}
    
    Revisaremos tu consulta y te contactaremos pronto.
    
    Gracias por contactarnos.
    
    Saludos,
    Equipo de Atención al Cliente
    Tienda Inmobiliaria
    """
    
    try:
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_submission.email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email de confirmación de contacto: {e}")
        return False


def send_contact_notification_email(contact_submission):
    """Envía email de notificación al administrador sobre nuevo mensaje de contacto"""
    subject = f'Nuevo Mensaje de Contacto - {contact_submission.nombre}'
    
    # Usar la fecha real de envío
    fecha_corregida = contact_submission.fecha_envio
    
    # Crear el contenido del email
    html_content = render_to_string('core/emails/contact_notification.html', {
        'contact_submission': contact_submission,
        'fecha_corregida': fecha_corregida,
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
    - Fecha de envío: {fecha_corregida.strftime('%d/%m/%Y %H:%M')}
    
    Mensaje:
    {contact_submission.mensaje}
    
    Saludos,
    Sistema de Contacto
    """
    
    try:
        # Enviar al email del administrador (configurado en settings)
        admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email de notificación de contacto: {e}")
        return False



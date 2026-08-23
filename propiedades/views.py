from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django_ratelimit.decorators import ratelimit
from django.conf import settings
from .models import Propiedad, ClickPropiedad, Amenidad
from .forms import PropiedadForm
from .validators import validar_imagen, validar_video, validar_imagen_o_video
from core.utils import turnstile_must_pass
import json
import logging
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

logger = logging.getLogger(__name__)

# Crea tus vistas aquí.

def lista_propiedades(request):
    """Vista para listar todas las propiedades - ahora usa la funcionalidad de búsqueda"""
    # Usar la misma lógica que buscar_propiedades pero sin filtros por defecto
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    operacion = request.GET.get('operacion', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    
    propiedades = Propiedad.objects.filter(estado='disponible')
    
    if query:
        propiedades = propiedades.filter(titulo__icontains=query)
    
    if tipo:
        propiedades = propiedades.filter(tipo=tipo)
    
    if operacion:
        propiedades = propiedades.filter(operacion=operacion)
    
    if precio_min:
        propiedades = propiedades.filter(precio__gte=precio_min)
    
    if precio_max:
        propiedades = propiedades.filter(precio__lte=precio_max)
    
    propiedades = propiedades.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(propiedades, 9)  # 9 propiedades por página
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número, mostrar la primera página
        page_obj = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera del rango, mostrar la última página
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tipo': tipo,
        'operacion': operacion,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'total_resultados': propiedades.count(),
    }
    
    return render(request, 'propiedades/buscar_propiedades.html', context)

@ratelimit(key='ip', rate='1/d', method='POST', block=False, group='formulario_consulta_propiedad')
def detalle_propiedad(request, slug):
    """Vista para mostrar el detalle de una propiedad"""
    try:
        # Solo mostrar propiedades disponibles (excluir eliminadas)
        propiedad = Propiedad.objects.get(slug=slug, estado='disponible')
    except Propiedad.DoesNotExist:
        # Si no se encuentra por slug, puede que el título haya cambiado y un enlace
        # antiguo apunte a un slug desactualizado. Solo redirigimos si el slug pedido
        # coincide EXACTAMENTE con slugify(titulo) de alguna propiedad: una coincidencia
        # parcial (ej. mismo prefijo) podría redirigir a una propiedad equivocada.
        from django.utils.text import slugify

        for prop in Propiedad.objects.filter(estado='disponible').only('slug', 'titulo'):
            if slugify(prop.titulo) == slug:
                return redirect('propiedades:detalle', slug=prop.slug)

        # Si no se encuentra ninguna coincidencia, mostrar 404
        propiedad = get_object_or_404(Propiedad, slug=slug, estado='disponible')
    
    # Procesar formulario de contacto si es POST
    if request.method == 'POST':
        # Rate limiting por IP: mostrar aviso en la misma página como los otros formularios
        if getattr(request, 'limited', False):
            from core.forms import ContactSubmissionForm
            from .models import Resena
            messages.error(
                request,
                'Has enviado demasiados formularios recientemente. Intenta nuevamente más tarde.',
            )
            propiedades_relacionadas = Propiedad.objects.filter(
                tipo=propiedad.tipo,
                operacion=propiedad.operacion,
                estado='disponible'
            ).exclude(id=propiedad.id)[:3]
            resenas_aprobadas = Resena.objects.filter(
                propiedad=propiedad,
                estado='aprobada'
            ).order_by('-fecha_creacion')
            promedio_calificacion = round(
                sum(r.calificacion for r in resenas_aprobadas) / resenas_aprobadas.count(), 1
            ) if resenas_aprobadas.exists() else 0.0
            total_resenas_aprobadas = resenas_aprobadas.count() if resenas_aprobadas.exists() else 0
            initial_data = {
                'asunto': 'alquiler',
                'mensaje': f'Hola, me interesa alquilar la propiedad "{propiedad.titulo}". '
                          f'¿Podrían contactarme para coordinar una visita y conocer más detalles sobre el alquiler? '
                          f'Entrada: 13:00 PM, Salida: 10:00 AM. Gracias.'
            }
            contact_form = ContactSubmissionForm(initial=initial_data)
            context = {
                'propiedad': propiedad,
                'propiedades_relacionadas': propiedades_relacionadas,
                'titulo_pagina': propiedad.titulo,
                'resenas_aprobadas': resenas_aprobadas,
                'promedio_calificacion': promedio_calificacion,
                'total_resenas_aprobadas': total_resenas_aprobadas,
                'contact_form': contact_form,
                'turnstile_site_key': settings.TURNSTILE_SITE_KEY,
            }
            return render(request, 'propiedades/detalle_propiedad.html', context, status=429)

        from core.forms import ContactSubmissionForm
        from core.models import ContactSubmission
        from core.views import send_contact_confirmation_email, send_contact_notification_email

        # Honeypot: si viene con contenido, descartamos silenciosamente
        if request.POST.get('honeypot'):
            messages.success(
                request,
                '¡Mensaje enviado exitosamente! Hemos recibido tu consulta y te contactaremos pronto.',
            )
            return redirect('propiedades:detalle', slug=propiedad.slug)

        ok_turnstile, msg_turnstile = turnstile_must_pass(request)
        if not ok_turnstile:
            from .models import Resena

            messages.error(request, msg_turnstile)
            contact_form = ContactSubmissionForm(
                request.POST, es_consulta_propiedad=True
            )
            propiedades_relacionadas = Propiedad.objects.filter(
                tipo=propiedad.tipo,
                operacion=propiedad.operacion,
                estado='disponible',
            ).exclude(id=propiedad.id)[:3]
            resenas_aprobadas = Resena.objects.filter(
                propiedad=propiedad,
                estado='aprobada',
            ).order_by('-fecha_creacion')
            promedio_calificacion = (
                round(
                    sum(r.calificacion for r in resenas_aprobadas)
                    / resenas_aprobadas.count(),
                    1,
                )
                if resenas_aprobadas.exists()
                else 0.0
            )
            total_resenas_aprobadas = (
                resenas_aprobadas.count() if resenas_aprobadas.exists() else 0
            )
            return render(
                request,
                'propiedades/detalle_propiedad.html',
                {
                    'propiedad': propiedad,
                    'propiedades_relacionadas': propiedades_relacionadas,
                    'titulo_pagina': propiedad.titulo,
                    'resenas_aprobadas': resenas_aprobadas,
                    'promedio_calificacion': promedio_calificacion,
                    'total_resenas_aprobadas': total_resenas_aprobadas,
                    'contact_form': contact_form,
                    'turnstile_site_key': settings.TURNSTILE_SITE_KEY,
                },
            )

        form = ContactSubmissionForm(request.POST, es_consulta_propiedad=True)
        if form.is_valid():
            try:
                # Guardar el mensaje de contacto
                contact_submission = form.save()
                
                # Agregar información de la propiedad al mensaje
                mensaje_original = contact_submission.mensaje
                mensaje_con_propiedad = f"{mensaje_original}\n\n--- Información de la Propiedad ---\nID: {propiedad.id}\nTítulo: {propiedad.titulo}"
                contact_submission.mensaje = mensaje_con_propiedad
                contact_submission.save()
                
                # Incrementar contador de consulta de propiedad
                from core.models import FormularioCount
                FormularioCount.incrementar_conteo('consulta_propiedad')
                
                # Enviar email de confirmación al usuario
                send_contact_confirmation_email(contact_submission)
                
                # Enviar email de notificación al administrador
                send_contact_notification_email(contact_submission)
                
                messages.success(
                    request, 
                    '¡Mensaje enviado exitosamente! Hemos recibido tu consulta y te contactaremos pronto.'
                )
                return redirect('propiedades:detalle', slug=propiedad.slug)
                
            except Exception as e:
                logger.error(f"Error al procesar formulario de contacto de propiedad: {e}", exc_info=True)
                messages.error(
                    request,
                    'No pudimos enviar tu mensaje. Por favor intenta nuevamente o contacta directamente con nosotros.'
                )
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # Obtener propiedades relacionadas
    propiedades_relacionadas = Propiedad.objects.filter(
        tipo=propiedad.tipo,
        operacion=propiedad.operacion,
        estado='disponible'  # Solo mostrar propiedades disponibles
    ).exclude(id=propiedad.id)[:3]
    
    # Obtener reseñas aprobadas de la propiedad
    from .models import Resena
    resenas_aprobadas = Resena.objects.filter(
        propiedad=propiedad,
        estado='aprobada'
    ).order_by('-fecha_creacion')
    
    # Calcular promedio de calificaciones
    if resenas_aprobadas.exists():
        promedio_calificacion = round(
            sum(resena.calificacion for resena in resenas_aprobadas) / resenas_aprobadas.count(), 1
        )
        total_resenas_aprobadas = resenas_aprobadas.count()
    else:
        promedio_calificacion = 0.0
        total_resenas_aprobadas = 0
    
    # Importar el formulario de contacto
    from core.forms import ContactSubmissionForm
    
    # Crear formulario con datos iniciales de la propiedad
    initial_data = {
        'asunto': 'alquiler',  # Pre-seleccionar "Alquiler"
        'mensaje': f'Hola, me interesa alquilar la propiedad "{propiedad.titulo}". '
                  f'¿Podrían contactarme para coordinar una visita y conocer más detalles sobre el alquiler? '
                  f'Entrada: 13:00 PM, Salida: 10:00 AM. '
                  f'Gracias.'
    }
    
    form = ContactSubmissionForm(initial=initial_data)
    
    context = {
        'propiedad': propiedad,
        'propiedades_relacionadas': propiedades_relacionadas,
        'titulo_pagina': propiedad.titulo,
        'resenas_aprobadas': resenas_aprobadas,
        'promedio_calificacion': promedio_calificacion,
        'total_resenas_aprobadas': total_resenas_aprobadas,
        'contact_form': form,
        'turnstile_site_key': settings.TURNSTILE_SITE_KEY,
    }
    return render(request, 'propiedades/detalle_propiedad.html', context)

def buscar_propiedades(request):
    """Vista para buscar propiedades"""
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    operacion = request.GET.get('operacion', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    
    propiedades = Propiedad.objects.filter(estado='disponible')
    
    if query:
        propiedades = propiedades.filter(titulo__icontains=query)
    
    if tipo:
        propiedades = propiedades.filter(tipo=tipo)
    
    if operacion:
        propiedades = propiedades.filter(operacion=operacion)
    
    if precio_min:
        propiedades = propiedades.filter(precio__gte=precio_min)
    
    if precio_max:
        propiedades = propiedades.filter(precio__lte=precio_max)
    
    propiedades = propiedades.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(propiedades, 9)  # 9 propiedades por página
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número, mostrar la primera página
        page_obj = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera del rango, mostrar la última página
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tipo': tipo,
        'operacion': operacion,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'total_resultados': propiedades.count(),
    }
    
    return render(request, 'propiedades/buscar_propiedades.html', context)

@login_required
@require_POST
def upload_fotos_adicionales(request):
    """Vista para subir fotos adicionales via AJAX (solo administradores)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción.'}, status=403)

    try:
        propiedad_id = request.POST.get('propiedad_id')
        fotos = request.FILES.getlist('fotos')

        if not propiedad_id or not fotos:
            return JsonResponse({'success': False, 'error': 'Datos incompletos'})

        # Solo permitir agregar fotos a propiedades disponibles (excluir eliminadas)
        propiedad = get_object_or_404(Propiedad, id=propiedad_id, estado='disponible')

        # Validar cada archivo (tipo MIME real, tamaño y extensión) antes de guardar nada
        for foto in fotos:
            try:
                validar_imagen(foto)
            except ValidationError as ve:
                return JsonResponse({'success': False, 'error': str(ve)}, status=400)

        # Guardar cada foto
        fotos_guardadas = []
        for i, foto in enumerate(fotos):
            from .models import FotoPropiedad
            foto_obj = FotoPropiedad.objects.create(
                propiedad=propiedad,
                imagen=foto,
                orden=i + 1,
                descripcion=f"Foto adicional {i + 1}"
            )
            fotos_guardadas.append({
                'id': foto_obj.id,
                'url': foto_obj.imagen.url,
                'nombre': foto_obj.imagen.name
            })

        return JsonResponse({
            'success': True,
            'fotos': fotos_guardadas,
            'mensaje': f'{len(fotos)} fotos subidas exitosamente'
        })

    except Exception as e:
        logger.error(f"Error en upload_fotos_adicionales: {e}")
        return JsonResponse({'success': False, 'error': 'No se pudieron subir las fotos.'})

def _asignar_administrador(request, propiedad):
    """Asigna a la propiedad el AdminCredentials del usuario autenticado,
    creándolo si todavía no existe (ej. un superusuario creado con
    `createsuperuser` que nunca pasó por el flujo de configuración de admin).
    Es best-effort: si falla, se registra el error pero no se interrumpe la
    creación de la propiedad. Se usa una transacción anidada (savepoint) para
    que un fallo acá no deje la conexión en un estado roto para las queries
    posteriores (guardar la propiedad, etc.)."""
    if not (hasattr(request, 'user') and request.user.is_authenticated):
        return

    try:
        with transaction.atomic():
            from login.models import AdminCredentials

            admin_creds = getattr(request.user, 'admincredentials', None)
            if not admin_creds:
                admin_creds = AdminCredentials.objects.filter(email=request.user.email).first()
            if not admin_creds:
                admin_creds = AdminCredentials.objects.create(
                    user=request.user,
                    email=request.user.email,
                    nombre=request.user.get_full_name() or request.user.username,
                    telefono='',
                    activo=True
                )

            propiedad.administrador = admin_creds
    except Exception as e:
        logger.warning(f"No se pudo asignar administrador a la propiedad: {e}")


def guardar_archivos_adicionales(propiedad, archivos, orden_inicial=0):
    """Valida y guarda una lista de archivos (imagen o video) como FotoPropiedad
    de `propiedad`, optimizándolos a WebP/comprimidos cuando corresponde.
    Usada tanto al crear como al editar una propiedad.
    Devuelve la lista de instancias FotoPropiedad creadas."""
    from .models import FotoPropiedad
    from core.utils import copiar_imagen_a_static

    fotos_creadas = []
    for i, archivo in enumerate(archivos):
        try:
            archivo, tipo_medio = validar_imagen_o_video(archivo)
        except ValidationError as ve:
            logger.warning(f"Archivo adicional rechazado ({archivo.name}): {ve}")
            continue

        orden = orden_inicial + i + 1
        foto = FotoPropiedad(
            propiedad=propiedad,
            tipo_medio=tipo_medio,
            orden=orden,
            descripcion=f"Foto adicional {orden}",
        )
        if tipo_medio == 'imagen':
            foto.imagen = archivo
        else:
            foto.video = archivo

        try:
            foto.save()
        except Exception as e:
            logger.error(f"Error al guardar archivo adicional ({archivo.name}): {e}", exc_info=True)
            continue

        fotos_creadas.append(foto)

        # Optimización (WebP para imágenes, compresión para video); no crítica.
        try:
            if tipo_medio == 'imagen':
                foto.optimize_image_field('imagen', quality=85)
                nombre_archivo = f"{propiedad.slug}-adicional-{foto.orden}"
                copiar_imagen_a_static(foto.imagen, nombre_archivo, quality=85)
            else:
                foto.optimize_video_field('video', quality=80)
        except Exception as e:
            logger.warning(f"Error optimizando archivo adicional ({archivo.name}, no crítico): {e}")

    return fotos_creadas


def _contexto_form_propiedad(form):
    return {
        'form': form,
        'titulo_pagina': 'Crear Nueva Propiedad',
        'amenidades': Amenidad.objects.all(),
    }


@login_required
@ratelimit(key='user', rate='20/h', method='POST', block=False)
def crear_propiedad(request):
    """Vista para crear una nueva propiedad."""
    try:
        if getattr(request, 'limited', False):
            messages.error(request, 'Has excedido el límite de creación de propiedades. Intenta más tarde.')
            return redirect('login:dashboard')

        if request.method != 'POST':
            return render(request, 'propiedades/crear_propiedad.html', _contexto_form_propiedad(PropiedadForm()))

        es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if not request.POST.get('titulo'):
            error_msg = "El título es requerido"
            if es_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
            return redirect('login:dashboard')

        form = PropiedadForm(request.POST, request.FILES)

        if not form.is_valid():
            logger.warning(f"Errores del formulario al crear propiedad: {form.errors}")
            if es_ajax:
                errors = {field: [str(err) for err in field_errors] for field, field_errors in form.errors.items()}
                if form.non_field_errors():
                    errors['__all__'] = [str(err) for err in form.non_field_errors()]
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor corrige los errores en el formulario.',
                    'errors': errors
                })
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            return render(request, 'propiedades/crear_propiedad.html', _contexto_form_propiedad(form))

        try:
            propiedad = form.save(commit=False)
            _asignar_administrador(request, propiedad)

            try:
                propiedad.save()
                propiedad.refresh_from_db()
            except Exception as db_error:
                logger.error(f"Error al guardar propiedad: {db_error}", exc_info=True)
                if 'Duplicate entry' in str(db_error):
                    error_msg = "Ya existe una propiedad con estos datos. Por favor, verifica la información."
                elif 'Connection' in str(db_error):
                    error_msg = "Error de conexión con la base de datos. Intenta nuevamente."
                elif 'Permission' in str(db_error):
                    error_msg = "Error de permisos. Contacta al administrador."
                else:
                    error_msg = "Error al guardar la propiedad. Intenta nuevamente."

                if es_ajax:
                    return JsonResponse({'success': False, 'message': error_msg})
                messages.error(request, error_msg)
                return render(request, 'propiedades/crear_propiedad.html', _contexto_form_propiedad(form))

            try:
                form.save_m2m()
            except Exception as m2m_error:
                logger.warning(f"Error guardando relaciones M2M: {m2m_error}")

            try:
                guardar_archivos_adicionales(propiedad, request.FILES.getlist('fotos_adicionales'))
            except Exception as e:
                logger.error(f"Error al procesar archivos adicionales: {e}", exc_info=True)

            # La conversión de imágenes a WebP corre en background (Celery) y
            # ya no bloquea el request, así que no hay mensajes de conversión
            # que mostrar todavía en esta respuesta. Se mantiene la clave por
            # compatibilidad con el JS de la plantilla (crear_propiedad.html),
            # que ya maneja bien el caso de lista vacía.
            if es_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Propiedad creada exitosamente.',
                    'propiedad_id': propiedad.id,
                    'redirect_url': reverse('propiedades:detalle', args=[propiedad.slug]),
                    'conversion_messages': []
                })

            messages.success(request, 'Propiedad creada exitosamente.')
            return redirect('propiedades:detalle', slug=propiedad.slug)

        except Exception as e:
            logger.error(f"Error al crear la propiedad: {e}", exc_info=True)
            user_friendly_message = "Hubo un problema al crear la propiedad. Por favor, verifica los datos e intenta nuevamente."
            messages.error(request, user_friendly_message)

            if es_ajax:
                return JsonResponse({
                    'success': False,
                    'message': user_friendly_message,
                    'error_details': str(e) if settings.DEBUG else None
                })
            return render(request, 'propiedades/crear_propiedad.html', _contexto_form_propiedad(form))

    except Exception as e:
        logger.critical(f"Error crítico en crear_propiedad: {e}", exc_info=True)
        error_type = type(e).__name__

        if 'DatabaseError' in error_type or 'OperationalError' in error_type:
            user_friendly_message = "Error de conexión con la base de datos. Por favor, intenta nuevamente en unos minutos."
        elif 'PermissionDenied' in error_type:
            user_friendly_message = "No tienes permisos para realizar esta acción."
        elif 'ValidationError' in error_type:
            user_friendly_message = "Los datos proporcionados no son válidos. Por favor, verifica la información."
        elif 'ImportError' in error_type:
            user_friendly_message = "Error de configuración del sistema. Contacta al administrador."
        else:
            user_friendly_message = "Ha ocurrido un error inesperado. Por favor, intenta nuevamente o contacta al administrador."

        messages.error(request, user_friendly_message)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': user_friendly_message,
                'error_details': str(e) if settings.DEBUG else None
            })

        return render(request, 'propiedades/crear_propiedad.html', _contexto_form_propiedad(PropiedadForm()))

@csrf_exempt
@require_POST
def registrar_click(request):
    """Vista AJAX para registrar clics en botones 'Ver Detalle'"""
    try:
        data = json.loads(request.body)
        propiedad_id = data.get('propiedad_id')
        pagina_origen = data.get('pagina_origen', 'home')
        
        if not propiedad_id:
            return JsonResponse({'success': False, 'error': 'ID de propiedad requerido'})
        
        # Solo permitir registrar clics en propiedades disponibles (excluir eliminadas)
        propiedad = get_object_or_404(Propiedad, id=propiedad_id, estado='disponible')
        
        # Obtener información del request
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Crear el registro de click
        click = ClickPropiedad.objects.create(
            propiedad=propiedad,
            ip_address=ip_address,
            user_agent=user_agent,
            pagina_origen=pagina_origen
        )
        
        return JsonResponse({
            'success': True,
            'click_id': click.id,
            'total_clicks': propiedad.get_total_clicks()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'})
    except Exception as e:
        logger.error(f"Error en registrar_click: {e}")
        return JsonResponse({'success': False, 'error': 'No se pudo registrar el click.'})

def crear_resena(request, slug):
    """Vista para crear una nueva reseña de una propiedad"""
    # Solo permitir crear reseñas en propiedades disponibles (excluir eliminadas)
    propiedad = get_object_or_404(Propiedad, slug=slug, estado='disponible')
    
    if request.method == 'POST':
        from .forms import ResenaForm
        
        form = ResenaForm(request.POST)
        if form.is_valid():
            # Crear la reseña
            resena = form.save(commit=False)
            resena.propiedad = propiedad
            
            # Obtener IP del usuario
            ip_address = request.META.get('REMOTE_ADDR')
            resena.ip_address = ip_address
            
            resena.save()
            
            # Verificar si es una petición AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Reseña enviada exitosamente. Será revisada antes de publicarse.',
                    'resena_id': resena.id
                })
            else:
                messages.success(request, 'Reseña enviada exitosamente. Será revisada antes de publicarse.')
                return redirect('propiedades:detalle', propiedad.slug)
        else:
            # Verificar si es una petición AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Devolver errores del formulario en formato JSON
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(error) for error in field_errors]
                
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor corrige los errores en el formulario.',
                    'errors': errors
                })
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        from .forms import ResenaForm
        form = ResenaForm()
    
    context = {
        'form': form,
        'propiedad': propiedad,
        'titulo_pagina': f'Escribir Reseña - {propiedad.titulo}'
    }
    return render(request, 'propiedades/crear_resena.html', context)

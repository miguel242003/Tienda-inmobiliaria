from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from .models import Propiedad, ClickPropiedad, Amenidad
from .forms import PropiedadForm
from .validators import validar_imagen, validar_video, validar_imagen_o_video
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

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

def detalle_propiedad(request, slug):
    """Vista para mostrar el detalle de una propiedad"""
    propiedad = get_object_or_404(Propiedad, slug=slug)
    
    # Procesar formulario de contacto si es POST
    if request.method == 'POST':
        from core.forms import ContactSubmissionForm
        from core.models import ContactSubmission
        from core.views import send_contact_confirmation_email, send_contact_notification_email
        
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
                messages.error(
                    request, 
                    f'Error al enviar el mensaje: {str(e)}. Por favor intenta nuevamente o contacta directamente con nosotros.'
                )
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # Obtener propiedades relacionadas
    propiedades_relacionadas = Propiedad.objects.filter(
        tipo=propiedad.tipo,
        operacion=propiedad.operacion
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
        'contact_form': form
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

@csrf_exempt
def upload_fotos_adicionales(request):
    """Vista para subir fotos adicionales via AJAX"""
    if request.method == 'POST':
        try:
            propiedad_id = request.POST.get('propiedad_id')
            fotos = request.FILES.getlist('fotos')
            
            if not propiedad_id or not fotos:
                return JsonResponse({'success': False, 'error': 'Datos incompletos'})
            
            propiedad = get_object_or_404(Propiedad, id=propiedad_id)
            
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
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@ratelimit(key='user', rate='20/h', method='POST', block=False)
def crear_propiedad(request):
    """
    Vista para crear una nueva propiedad.
    
    🔒 SEGURIDAD:
    - Rate limiting: Máximo 20 propiedades por hora por usuario
    - Validación robusta de archivos con python-magic
    - Verificación de tipo MIME real
    """
    # Verificar rate limit
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Has excedido el límite de creación de propiedades. Intenta más tarde.')
        return redirect('login:dashboard')
    
    if request.method == 'POST':
        form = PropiedadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 🔒 VALIDAR IMÁGENES PRINCIPALES
                if 'imagen_principal' in request.FILES:
                    try:
                        archivo = request.FILES['imagen_principal']
                        # Debug: Log información del archivo
                        print(f"DEBUG - Archivo imagen_principal:")
                        print(f"  - Nombre: {archivo.name}")
                        print(f"  - Tamaño: {archivo.size} bytes")
                        print(f"  - Content-Type: {archivo.content_type}")
                        print(f"  - Charset: {getattr(archivo, 'charset', 'N/A')}")
                        
                        validar_imagen(archivo, max_mb=20)
                    except ValidationError as e:
                        error_message = f'Imagen principal: {str(e)}'
                        print(f"DEBUG - Error de validación: {error_message}")
                        messages.error(request, error_message)
                        # Verificar si es una petición AJAX
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'message': error_message
                            })
                        else:
                            return render(request, 'propiedades/crear_propiedad.html', {
                                'form': form,
                                'titulo_pagina': 'Crear Nueva Propiedad',
                                'amenidades': Amenidad.objects.all()
                            })
                
                if 'imagen_secundaria' in request.FILES:
                    try:
                        validar_imagen(request.FILES['imagen_secundaria'], max_mb=20)
                    except ValidationError as e:
                        error_message = f'Imagen secundaria: {str(e)}'
                        messages.error(request, error_message)
                        # Verificar si es una petición AJAX
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'message': error_message
                            })
                        else:
                            return render(request, 'propiedades/crear_propiedad.html', {
                                'form': form,
                                'titulo_pagina': 'Crear Nueva Propiedad',
                                'amenidades': Amenidad.objects.all()
                            })
                
                propiedad = form.save(commit=False)
                
                # Asignar el administrador actual a la propiedad
                if hasattr(request, 'user') and request.user.is_authenticated:
                    # Buscar el AdminCredentials correspondiente al usuario
                    from login.models import AdminCredentials
                    try:
                        # Primero intentar buscar por usuario relacionado
                        if hasattr(request.user, 'admincredentials'):
                            admin_creds = request.user.admincredentials
                        else:
                            # Si no, buscar por email
                            admin_creds = AdminCredentials.objects.get(email=request.user.email)
                        
                        propiedad.administrador = admin_creds
                    except AdminCredentials.DoesNotExist:
                        # Si no existe AdminCredentials, mostrar mensaje de error
                        error_message = 'Error: No se encontró tu perfil de administrador. Por favor, completa tu perfil antes de crear propiedades.'
                        messages.error(request, error_message)
                        # Verificar si es una petición AJAX
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'message': error_message
                            })
                        else:
                            return render(request, 'propiedades/crear_propiedad.html', {
                                'form': form,
                                'titulo_pagina': 'Crear Nueva Propiedad',
                                'amenidades': Amenidad.objects.all()
                            })
                
                propiedad.save()
                
                # Guardar las amenidades (relación many-to-many)
                form.save_m2m()
                
                # 🔒 VALIDAR Y MANEJAR archivos adicionales (fotos y videos)
                archivos_adicionales = request.FILES.getlist('fotos_adicionales')
                if archivos_adicionales:
                    from .models import FotoPropiedad
                    for i, archivo in enumerate(archivos_adicionales):
                        try:
                            # Validar archivo (imagen o video)
                            archivo_validado, tipo = validar_imagen_o_video(archivo)
                            
                            if tipo == 'video':
                                FotoPropiedad.objects.create(
                                    propiedad=propiedad,
                                    tipo_medio='video',
                                    video=archivo_validado,
                                    orden=i + 1,
                                    descripcion=f"Video {i + 1} de {propiedad.titulo}"
                                )
                            else:  # imagen
                                FotoPropiedad.objects.create(
                                    propiedad=propiedad,
                                    tipo_medio='imagen',
                                    imagen=archivo_validado,
                                    orden=i + 1,
                                    descripcion=f"Foto {i + 1} de {propiedad.titulo}"
                                )
                        except ValidationError as e:
                            # Registrar error pero continuar con otros archivos
                            messages.warning(request, f'Archivo "{archivo.name}" no válido: {str(e)}')
            
            except Exception as e:
                error_message = f'Error al crear la propiedad: {str(e)}'
                messages.error(request, error_message)
                # Verificar si es una petición AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    })
                else:
                    return render(request, 'propiedades/crear_propiedad.html', {
                        'form': form,
                        'titulo_pagina': 'Crear Nueva Propiedad',
                        'amenidades': Amenidad.objects.all()
                    })
            
            # Verificar si es una petición AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Propiedad creada exitosamente.',
                    'propiedad_id': propiedad.id,
                    'redirect_url': reverse('propiedades:detalle', args=[propiedad.slug])
                })
            else:
                messages.success(request, 'Propiedad creada exitosamente.')
                return redirect('propiedades:detalle', slug=propiedad.slug)
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
        form = PropiedadForm()
    
    context = {
        'form': form,
        'titulo_pagina': 'Crear Nueva Propiedad',
        'amenidades': Amenidad.objects.all()
    }
    return render(request, 'propiedades/crear_propiedad.html', context)

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
        
        propiedad = get_object_or_404(Propiedad, id=propiedad_id)
        
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
        return JsonResponse({'success': False, 'error': str(e)})

def crear_resena(request, slug):
    """Vista para crear una nueva reseña de una propiedad"""
    propiedad = get_object_or_404(Propiedad, slug=slug)
    
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
                return redirect('propiedades:detalle', propiedad_id)
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

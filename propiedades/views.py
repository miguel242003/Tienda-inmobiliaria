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
    Vista simplificada para crear una nueva propiedad.
    """
    print(f"DEBUG - Iniciando crear_propiedad")
    print(f"DEBUG - Método: {request.method}")
    print(f"DEBUG - Usuario: {request.user}")
    
    # Verificar rate limit
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        print(f"DEBUG - Rate limit excedido")
        messages.error(request, 'Has excedido el límite de creación de propiedades. Intenta más tarde.')
        return redirect('login:dashboard')
    
    if request.method == 'POST':
        print(f"DEBUG - Procesando POST")
        print(f"DEBUG - Datos POST: {dict(request.POST)}")
        print(f"DEBUG - Archivos: {list(request.FILES.keys())}")
        
        try:
            # Crear formulario
            form = PropiedadForm(request.POST, request.FILES)
            print(f"DEBUG - Formulario creado")
            
            if form.is_valid():
                print(f"DEBUG - Formulario válido")
                
                # Crear propiedad
                propiedad = form.save(commit=False)
                print(f"DEBUG - Propiedad creada en memoria: {propiedad.titulo}")
                
                # Asignar administrador
                if request.user.is_authenticated:
                    try:
                        from login.models import AdminCredentials
                        admin_creds = AdminCredentials.objects.get(email=request.user.email)
                        propiedad.administrador = admin_creds
                        print(f"DEBUG - Administrador asignado: {admin_creds}")
                    except Exception as e:
                        print(f"DEBUG - Error asignando administrador: {e}")
                        return JsonResponse({
                            'success': False,
                            'message': f'Error asignando administrador: {str(e)}'
                        })
                
                # Guardar propiedad
                propiedad.save()
                print(f"DEBUG - Propiedad guardada con ID: {propiedad.id}")
                
                # Guardar amenidades
                form.save_m2m()
                print(f"DEBUG - Amenidades guardadas")
                
                # Respuesta exitosa
                return JsonResponse({
                    'success': True,
                    'message': 'Propiedad creada exitosamente.',
                    'propiedad_id': propiedad.id,
                    'redirect_url': f'/propiedades/{propiedad.slug}/'
                })
            else:
                print(f"DEBUG - Formulario inválido: {form.errors}")
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor corrige los errores en el formulario.',
                    'errors': dict(form.errors)
                })
                
        except Exception as e:
            import traceback
            print(f"DEBUG - ERROR: {str(e)}")
            print(f"DEBUG - TRACEBACK: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}',
                'debug': str(e)
            })
    else:
        form = PropiedadForm()
    
    context = {
        'form': form,
        'titulo_pagina': 'Crear Nueva Propiedad',
        'amenidades': Amenidad.objects.all()
    }
    return render(request, 'propiedades/crear_propiedad.html', context)

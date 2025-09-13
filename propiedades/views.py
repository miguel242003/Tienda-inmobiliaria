from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Propiedad
from .forms import PropiedadForm
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

def detalle_propiedad(request, propiedad_id):
    """Vista para mostrar el detalle de una propiedad"""
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)
    
    # Obtener propiedades relacionadas
    propiedades_relacionadas = Propiedad.objects.filter(
        tipo=propiedad.tipo,
        operacion=propiedad.operacion
    ).exclude(id=propiedad.id)[:3]
    
    context = {
        'propiedad': propiedad,
        'propiedades_relacionadas': propiedades_relacionadas,
        'titulo_pagina': propiedad.titulo
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

def crear_propiedad(request):
    """Vista para crear una nueva propiedad"""
    if request.method == 'POST':
        form = PropiedadForm(request.POST, request.FILES)
        if form.is_valid():
            propiedad = form.save(commit=False)
            
            # Asignar el administrador actual a la propiedad
            if hasattr(request, 'user') and request.user.is_authenticated:
                # Buscar el AdminCredentials correspondiente al usuario
                from login.models import AdminCredentials
                try:
                    admin_creds = AdminCredentials.objects.get(email=request.user.email)
                    propiedad.administrador = admin_creds
                except AdminCredentials.DoesNotExist:
                    # Si no existe AdminCredentials, crear uno básico
                    admin_creds = AdminCredentials.objects.create(
                        nombre=request.user.first_name or 'Administrador',
                        apellido=request.user.last_name or 'del Sistema',
                        email=request.user.email,
                        telefono='+52-1-33-00000000',
                        password='temp_password_123'  # Contraseña temporal
                    )
                    propiedad.administrador = admin_creds
            
            propiedad.save()
            
            # Guardar las amenidades (relación many-to-many)
            form.save_m2m()
            
            # Manejar fotos adicionales si existen
            fotos_adicionales = request.FILES.getlist('fotos_adicionales')
            if fotos_adicionales:
                from .models import FotoPropiedad
                for i, foto in enumerate(fotos_adicionales):
                    FotoPropiedad.objects.create(
                        propiedad=propiedad,
                        imagen=foto,
                        orden=i + 1,
                        descripcion=f"Foto {i + 1} de {propiedad.titulo}"
                    )
            
            messages.success(request, 'Propiedad creada exitosamente.')
            return redirect('propiedades:detalle', propiedad.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PropiedadForm()
    
    context = {
        'form': form,
        'titulo_pagina': 'Crear Nueva Propiedad'
    }
    return render(request, 'propiedades/crear_propiedad.html', context)

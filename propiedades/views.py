from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Propiedad
from .forms import PropiedadForm

# Create your views here.

def lista_propiedades(request):
    """Vista para listar todas las propiedades"""
    propiedades = Propiedad.objects.filter(estado='disponible').order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(propiedades, 9)  # 9 propiedades por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_propiedades': propiedades.count(),
    }
    
    return render(request, 'propiedades/lista_propiedades.html', context)

def detalle_propiedad(request, propiedad_id):
    """Vista para mostrar el detalle de una propiedad"""
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)
    
    # Propiedades relacionadas (mismo tipo)
    propiedades_relacionadas = Propiedad.objects.filter(
        tipo=propiedad.tipo,
        estado='disponible'
    ).exclude(id=propiedad.id)[:3]
    
    context = {
        'propiedad': propiedad,
        'propiedades_relacionadas': propiedades_relacionadas,
    }
    
    return render(request, 'propiedades/detalle_propiedad.html', context)

def buscar_propiedades(request):
    """Vista para buscar propiedades"""
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    
    propiedades = Propiedad.objects.filter(estado='disponible')
    
    if query:
        propiedades = propiedades.filter(titulo__icontains=query)
    
    if tipo:
        propiedades = propiedades.filter(tipo=tipo)
    
    if precio_min:
        propiedades = propiedades.filter(precio__gte=precio_min)
    
    if precio_max:
        propiedades = propiedades.filter(precio__lte=precio_max)
    
    propiedades = propiedades.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(propiedades, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tipo': tipo,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'total_resultados': propiedades.count(),
    }
    
    return render(request, 'propiedades/buscar_propiedades.html', context)

@login_required
def crear_propiedad(request):
    """Vista para crear una nueva propiedad"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para crear propiedades.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = PropiedadForm(request.POST, request.FILES)
        if form.is_valid():
            propiedad = form.save(commit=False)
            propiedad.save()
            messages.success(request, f'Propiedad "{propiedad.titulo}" creada exitosamente.')
            return redirect('propiedades:detalle', propiedad_id=propiedad.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PropiedadForm()
    
    context = {
        'form': form,
        'tipos_propiedad': Propiedad.TIPO_CHOICES,
        'estados_propiedad': Propiedad.ESTADO_CHOICES,
    }
    
    return render(request, 'propiedades/crear_propiedad.html', context)

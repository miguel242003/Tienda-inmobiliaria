from django.shortcuts import render
from propiedades.models import Propiedad

# Crea tus vistas aquí.

def home(request):
    """Vista principal del home"""
    try:
        # Obtener propiedades destacadas con lógica mejorada
        # Priorizar propiedades con imágenes y recientes
        propiedades_destacadas = Propiedad.objects.filter(
            estado='disponible'
        ).order_by('-fecha_creacion')[:8]  # Obtener más para seleccionar las mejores
        
        # Si hay propiedades con imágenes, priorizarlas
        propiedades_con_imagen = [p for p in propiedades_destacadas if p.imagen_principal]
        propiedades_sin_imagen = [p for p in propiedades_destacadas if not p.imagen_principal]
        
        # Combinar: primero las que tienen imagen, luego las que no
        propiedades_destacadas = propiedades_con_imagen + propiedades_sin_imagen
        
        # Tomar solo las primeras 6 para mostrar
        propiedades_destacadas = propiedades_destacadas[:6]
        
        # Estadísticas básicas
        total_propiedades = Propiedad.objects.count()
        propiedades_disponibles = Propiedad.objects.filter(estado='disponible').count()
        propiedades_vendidas = Propiedad.objects.filter(estado='vendida').count()
        
        # Obtener tipos de propiedades disponibles para mostrar diversidad
        tipos_disponibles = Propiedad.objects.filter(
            estado='disponible'
        ).values_list('tipo', flat=True).distinct()
        
        # Si no hay propiedades disponibles, mostrar todas las propiedades para estadísticas
        if propiedades_disponibles == 0:
            # Mostrar propiedades recientes sin importar el estado
            propiedades_destacadas = Propiedad.objects.all().order_by('-fecha_creacion')[:6]
            tipos_disponibles = Propiedad.objects.values_list('tipo', flat=True).distinct()
        
        context = {
            'propiedades_destacadas': propiedades_destacadas,
            'total_propiedades': total_propiedades,
            'propiedades_disponibles': propiedades_disponibles,
            'propiedades_vendidas': propiedades_vendidas,
            'tipos_disponibles': tipos_disponibles,
            'hay_propiedades': len(propiedades_destacadas) > 0,
        }
        
    except Exception as e:
        # En caso de error, crear un contexto básico
        context = {
            'propiedades_destacadas': [],
            'total_propiedades': 0,
            'propiedades_disponibles': 0,
            'propiedades_vendidas': 0,
            'tipos_disponibles': [],
            'hay_propiedades': False,
            'error_message': 'Error al cargar las propiedades'
        }
        print(f"Error en vista home: {e}")
    
    return render(request, 'core/home.html', context)

def about(request):
    """Vista sobre nosotros"""
    return render(request, 'core/about.html')

def contact(request):
    """Vista de contacto"""
    return render(request, 'core/contact.html')

def consorcio(request):
    """Vista para la página de Consorcio"""
    return render(request, 'core/consorcio.html')



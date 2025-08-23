from django.shortcuts import render
from propiedades.models import Propiedad

# Crea tus vistas aquí.

def home(request):
    """Vista principal del home"""
    try:
        # Obtener propiedades destacadas SOLO en venta
        # Priorizar propiedades con imágenes y recientes
        propiedades_destacadas = Propiedad.objects.filter(
            estado='disponible',
            operacion='venta'  # Solo propiedades en venta
        ).order_by('-fecha_creacion')[:8]  # Obtener más para seleccionar las mejores
        
        # Debug: imprimir información sobre las propiedades encontradas
        print(f"DEBUG: Propiedades en venta encontradas: {propiedades_destacadas.count()}")
        for p in propiedades_destacadas:
            print(f"DEBUG: - {p.titulo} (Operación: {p.operacion}, Estado: {p.estado})")
        
        # Si hay propiedades con imágenes, priorizarlas
        propiedades_con_imagen = [p for p in propiedades_destacadas if p.imagen_principal]
        propiedades_sin_imagen = [p for p in propiedades_destacadas if not p.imagen_principal]
        
        # Combinar: primero las que tienen imagen, luego las que no
        propiedades_destacadas = propiedades_con_imagen + propiedades_sin_imagen
        
        # Tomar solo las primeras 2 para mostrar (en lugar de 6)
        propiedades_destacadas = propiedades_destacadas[:2]
        
        # Obtener propiedades en alquiler (alquiler y alquiler temporal)
        propiedades_alquiler = Propiedad.objects.filter(
            estado='disponible',
            operacion__in=['alquiler', 'alquiler_temporal']  # Propiedades de alquiler y alquiler temporal
        ).order_by('-fecha_creacion')[:2]  # Solo 2 propiedades más recientes
        
        # Contar propiedades por tipo de operación
        propiedades_alquiler_count = Propiedad.objects.filter(
            estado='disponible',
            operacion='alquiler'
        ).count()
        
        propiedades_alquiler_temporal_count = Propiedad.objects.filter(
            estado='disponible',
            operacion='alquiler_temporal'
        ).count()
        
        # Debug: imprimir información sobre las propiedades de alquiler encontradas
        print(f"DEBUG: Propiedades en alquiler encontradas: {propiedades_alquiler.count()}")
        print(f"DEBUG: Propiedades de alquiler: {propiedades_alquiler_count}")
        print(f"DEBUG: Propiedades de alquiler temporal: {propiedades_alquiler_temporal_count}")
        for p in propiedades_alquiler:
            print(f"DEBUG: - {p.titulo} (Operación: {p.operacion}, Estado: {p.estado})")
        
        # Estadísticas básicas
        total_propiedades = Propiedad.objects.count()
        propiedades_disponibles = Propiedad.objects.filter(estado='disponible').count()
        propiedades_vendidas = Propiedad.objects.filter(estado='vendida').count()
        
        # Obtener tipos de propiedades disponibles para mostrar diversidad (solo en venta)
        tipos_disponibles = Propiedad.objects.filter(
            estado='disponible',
            operacion='venta'  # Solo propiedades en venta
        ).values_list('tipo', flat=True).distinct()
        
        # Si no hay propiedades en venta disponibles, mostrar todas las propiedades para estadísticas
        if len(propiedades_destacadas) == 0:
            # Mostrar propiedades recientes sin importar el estado
            propiedades_destacadas = Propiedad.objects.all().order_by('-fecha_creacion')[:2]
            tipos_disponibles = Propiedad.objects.values_list('tipo', flat=True).distinct()
        
        context = {
            'propiedades_destacadas': propiedades_destacadas,
            'propiedades_alquiler': propiedades_alquiler,
            'propiedades_alquiler_count': propiedades_alquiler_count,
            'propiedades_alquiler_temporal_count': propiedades_alquiler_temporal_count,
            'total_propiedades': total_propiedades,
            'propiedades_disponibles': propiedades_disponibles,
            'propiedades_vendidas': propiedades_vendidas,
            'tipos_disponibles': tipos_disponibles,
            'hay_propiedades': len(propiedades_destacadas) > 0,
            'hay_propiedades_alquiler': len(propiedades_alquiler) > 0,
        }
        
    except Exception as e:
        # En caso de error, crear un contexto básico
        context = {
            'propiedades_destacadas': [],
            'propiedades_alquiler': [],
            'propiedades_alquiler_count': 0,
            'propiedades_alquiler_temporal_count': 0,
            'total_propiedades': 0,
            'propiedades_disponibles': 0,
            'propiedades_vendidas': 0,
            'tipos_disponibles': [],
            'hay_propiedades': False,
            'hay_propiedades_alquiler': False,
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



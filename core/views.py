from django.shortcuts import render
from propiedades.models import Propiedad

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
    return render(request, 'core/contact.html')

def consorcio(request):
    """Vista para la página de Consorcio"""
    return render(request, 'core/consorcio.html')

def cv(request):
    """Vista para envío de currículum"""
    return render(request, 'core/cv.html')



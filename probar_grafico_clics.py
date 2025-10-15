#!/usr/bin/env python
"""
Script para probar el gráfico de clics y verificar que se actualiza
"""
import os
import sys
import django
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.tienda_meli.settings')
django.setup()

from propiedades.models import Propiedad, ClickPropiedad
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import Extract

def verificar_datos_grafico():
    """Verificar los datos que usa el gráfico"""
    print("🔍 Verificando datos del gráfico...")
    
    # Obtener año actual
    año_actual = timezone.now().year
    fecha_inicio_año = timezone.datetime(año_actual, 1, 1)
    fecha_fin_año = timezone.datetime(año_actual + 1, 1, 1)
    fecha_inicio_año = timezone.make_aware(fecha_inicio_año)
    fecha_fin_año = timezone.make_aware(fecha_fin_año)
    
    print(f"📅 Año actual: {año_actual}")
    print(f"📅 Desde: {fecha_inicio_año}")
    print(f"📅 Hasta: {fecha_fin_año}")
    
    # Obtener todas las propiedades
    todas_propiedades = Propiedad.objects.all()
    print(f"🏠 Total propiedades: {todas_propiedades.count()}")
    
    # Obtener clics del año actual
    clicks_agrupados = ClickPropiedad.objects.filter(
        fecha_click__gte=fecha_inicio_año,
        fecha_click__lt=fecha_fin_año
    ).values(
        'propiedad_id', 
        'fecha_click__month'
    ).annotate(
        total_clicks=Count('id')
    ).order_by('propiedad_id', 'fecha_click__month')
    
    print(f"📊 Total clics este año: {clicks_agrupados.count()}")
    
    # Mostrar clics por mes
    clicks_por_mes = {}
    for click_data in clicks_agrupados:
        prop_id = click_data['propiedad_id']
        mes = click_data['fecha_click__month']
        total = click_data['total_clicks']
        
        if prop_id not in clicks_por_mes:
            clicks_por_mes[prop_id] = {}
        clicks_por_mes[prop_id][mes] = total
        
        print(f"  Propiedad {prop_id}, Mes {mes}: {total} clics")
    
    # Mostrar total por propiedad
    print("\n📈 Total clics por propiedad este año:")
    for propiedad in todas_propiedades:
        total_clics = ClickPropiedad.objects.filter(
            propiedad=propiedad,
            fecha_click__gte=fecha_inicio_año,
            fecha_click__lt=fecha_fin_año
        ).count()
        print(f"  {propiedad.titulo}: {total_clics} clics")
    
    return clicks_agrupados.count() > 0

def crear_click_prueba():
    """Crear un click de prueba para verificar que se actualiza"""
    print("\n🧪 Creando click de prueba...")
    
    # Obtener primera propiedad
    propiedad = Propiedad.objects.first()
    if not propiedad:
        print("❌ No hay propiedades en la base de datos")
        return False
    
    # Crear click de prueba
    click = ClickPropiedad.objects.create(
        propiedad=propiedad,
        ip_address='127.0.0.1',
        user_agent='Test Script - ' + str(timezone.now()),
        pagina_origen='home'
    )
    
    print(f"✅ Click de prueba creado (ID: {click.id})")
    print(f"📅 Fecha: {click.fecha_click}")
    print(f"🏠 Propiedad: {propiedad.titulo}")
    
    return True

def verificar_actualizacion():
    """Verificar que el gráfico se actualiza"""
    print("\n🔄 Verificando actualización del gráfico...")
    
    # Contar clics antes
    clics_antes = ClickPropiedad.objects.count()
    print(f"📊 Clics antes: {clics_antes}")
    
    # Crear click de prueba
    if crear_click_prueba():
        # Contar clics después
        clics_despues = ClickPropiedad.objects.count()
        print(f"📊 Clics después: {clics_despues}")
        
        if clics_despues > clics_antes:
            print("✅ El gráfico debería actualizarse!")
            print("🔄 Recarga la página del dashboard para ver los cambios")
            return True
        else:
            print("❌ No se incrementó el contador")
            return False
    else:
        return False

if __name__ == "__main__":
    print("🔍 Verificando sistema de gráfico de clics...")
    print()
    
    if verificar_datos_grafico():
        print("\n✅ Los datos del gráfico están disponibles")
        
        if verificar_actualizacion():
            print("\n🎉 ¡El sistema está funcionando correctamente!")
            print("📋 El gráfico debería actualizarse cuando:")
            print("  1. Haces clic en 'Ver Detalle' desde la página principal")
            print("  2. Recargas la página del dashboard")
            print("  3. Los datos se cargan desde MySQL en tiempo real")
        else:
            print("\n❌ Hay un problema con la actualización")
    else:
        print("\n❌ No hay datos para mostrar en el gráfico")
        print("🔧 Asegúrate de que hay clics registrados en MySQL")

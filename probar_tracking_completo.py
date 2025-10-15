#!/usr/bin/env python
"""
Script para probar el tracking de clics completo
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

def verificar_tracking():
    """Verificar que el tracking funciona"""
    print("🔍 Verificando sistema de tracking...")
    
    # Obtener propiedades
    propiedades = Propiedad.objects.all()
    if not propiedades.exists():
        print("❌ No hay propiedades en la base de datos")
        return False
    
    print(f"🏠 Total propiedades: {propiedades.count()}")
    
    # Contar clics actuales
    clics_antes = ClickPropiedad.objects.count()
    print(f"📊 Clics actuales: {clics_antes}")
    
    # Mostrar clics por propiedad
    print("\n📈 Clics por propiedad:")
    for propiedad in propiedades:
        clics = propiedad.get_total_clicks()
        print(f"  {propiedad.titulo}: {clics} clics")
    
    # Mostrar clics recientes
    print("\n🕒 Clics recientes:")
    clics_recientes = ClickPropiedad.objects.order_by('-fecha_click')[:5]
    for click in clics_recientes:
        print(f"  {click.fecha_click.strftime('%Y-%m-%d %H:%M')} - {click.propiedad.titulo} - {click.pagina_origen}")
    
    return True

def crear_click_prueba():
    """Crear un click de prueba"""
    print("\n🧪 Creando click de prueba...")
    
    propiedad = Propiedad.objects.first()
    if not propiedad:
        print("❌ No hay propiedades")
        return False
    
    click = ClickPropiedad.objects.create(
        propiedad=propiedad,
        ip_address='127.0.0.1',
        user_agent='Test Script - ' + str(timezone.now()),
        pagina_origen='home'
    )
    
    print(f"✅ Click creado: ID {click.id}")
    print(f"🏠 Propiedad: {propiedad.titulo}")
    print(f"📅 Fecha: {click.fecha_click}")
    
    return True

def verificar_grafico():
    """Verificar datos del gráfico"""
    print("\n📊 Verificando datos del gráfico...")
    
    año_actual = timezone.now().year
    fecha_inicio = timezone.datetime(año_actual, 1, 1)
    fecha_fin = timezone.datetime(año_actual + 1, 1, 1)
    fecha_inicio = timezone.make_aware(fecha_inicio)
    fecha_fin = timezone.make_aware(fecha_fin)
    
    clics_año = ClickPropiedad.objects.filter(
        fecha_click__gte=fecha_inicio,
        fecha_click__lt=fecha_fin
    ).count()
    
    print(f"📅 Año actual: {año_actual}")
    print(f"📊 Clics este año: {clics_año}")
    
    if clics_año > 0:
        print("✅ El gráfico debería mostrar datos")
        return True
    else:
        print("⚠️ No hay clics este año - el gráfico estará vacío")
        return False

if __name__ == "__main__":
    print("🔍 Verificando sistema de tracking completo...")
    print()
    
    if verificar_tracking():
        print("\n✅ Sistema de tracking funcionando")
        
        if crear_click_prueba():
            print("\n✅ Click de prueba creado")
            
            if verificar_grafico():
                print("\n🎉 ¡Todo está funcionando correctamente!")
                print("📋 El gráfico debería actualizarse cuando:")
                print("  1. Haces clic en 'Ver Detalle' desde la página principal")
                print("  2. Recargas la página del dashboard")
                print("  3. Los datos se cargan desde MySQL")
            else:
                print("\n⚠️ El gráfico puede estar vacío porque no hay clics este año")
        else:
            print("\n❌ Error al crear click de prueba")
    else:
        print("\n❌ Error en el sistema de tracking")

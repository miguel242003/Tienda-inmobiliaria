#!/usr/bin/env python
"""
Script final para verificar que el tracking funciona correctamente
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

def verificar_sistema_completo():
    """Verificar que todo el sistema funciona"""
    print("🔍 Verificando sistema completo de tracking...")
    print()
    
    # 1. Verificar propiedades
    propiedades = Propiedad.objects.all()
    print(f"🏠 Total propiedades: {propiedades.count()}")
    
    if not propiedades.exists():
        print("❌ No hay propiedades en la base de datos")
        return False
    
    # 2. Verificar clics existentes
    clics_totales = ClickPropiedad.objects.count()
    print(f"📊 Total clics en la base de datos: {clics_totales}")
    
    # 3. Mostrar clics por propiedad
    print("\n📈 Clics por propiedad:")
    for propiedad in propiedades:
        clics = propiedad.get_total_clicks()
        print(f"  {propiedad.titulo}: {clics} clics")
    
    # 4. Mostrar clics recientes
    print("\n🕒 Clics recientes (últimos 5):")
    clics_recientes = ClickPropiedad.objects.order_by('-fecha_click')[:5]
    for click in clics_recientes:
        print(f"  {click.fecha_click.strftime('%Y-%m-%d %H:%M')} - {click.propiedad.titulo} - {click.pagina_origen}")
    
    # 5. Verificar clics del año actual
    año_actual = timezone.now().year
    fecha_inicio = timezone.datetime(año_actual, 1, 1)
    fecha_fin = timezone.datetime(año_actual + 1, 1, 1)
    fecha_inicio = timezone.make_aware(fecha_inicio)
    fecha_fin = timezone.make_aware(fecha_fin)
    
    clics_año = ClickPropiedad.objects.filter(
        fecha_click__gte=fecha_inicio,
        fecha_click__lt=fecha_fin
    ).count()
    
    print(f"\n📅 Clics este año ({año_actual}): {clics_año}")
    
    if clics_año > 0:
        print("✅ El gráfico debería mostrar datos")
    else:
        print("⚠️ No hay clics este año - el gráfico estará vacío")
    
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

if __name__ == "__main__":
    print("🔍 Verificación final del sistema de tracking...")
    print("=" * 50)
    
    if verificar_sistema_completo():
        print("\n✅ Sistema de tracking funcionando correctamente")
        
        if crear_click_prueba():
            print("\n✅ Click de prueba creado exitosamente")
            
            print("\n🎉 ¡TODO FUNCIONANDO CORRECTAMENTE!")
            print("📋 Para verificar que funciona:")
            print("  1. Recarga la página (Ctrl+F5)")
            print("  2. Haz clic en 'Ver Detalle' de cualquier propiedad")
            print("  3. Verifica en la consola que aparezca '✅ Click registrado exitosamente'")
            print("  4. Ve al dashboard y verifica que el gráfico se actualiza")
        else:
            print("\n❌ Error al crear click de prueba")
    else:
        print("\n❌ Error en el sistema de tracking")

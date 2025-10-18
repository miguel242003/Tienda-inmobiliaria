#!/usr/bin/env python
"""
Script para verificar clics en tiempo real
"""
import os
import sys
import django
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.tienda_meli.settings')
django.setup()

from propiedades.models import ClickPropiedad, Propiedad
from django.utils import timezone

def monitorear_clics():
    """Monitorear clics en tiempo real"""
    print("🔍 MONITOREANDO CLICS EN TIEMPO REAL")
    print("=" * 50)
    print("Presiona Ctrl+C para salir")
    print()
    
    # Obtener conteo inicial
    clics_iniciales = ClickPropiedad.objects.count()
    print(f"📊 Clics iniciales: {clics_iniciales}")
    
    try:
        while True:
            # Obtener conteo actual
            clics_actuales = ClickPropiedad.objects.count()
            
            if clics_actuales > clics_iniciales:
                nuevos_clics = clics_actuales - clics_iniciales
                print(f"🎉 ¡NUEVOS CLICS DETECTADOS! (+{nuevos_clics})")
                print(f"📊 Total actual: {clics_actuales}")
                
                # Mostrar los últimos clics
                ultimos_clics = ClickPropiedad.objects.all()[:3]
                print("📋 Últimos clics:")
                for click in ultimos_clics:
                    print(f"   - {click.propiedad.titulo} - {click.fecha_click.strftime('%H:%M:%S')} - {click.pagina_origen}")
                
                clics_iniciales = clics_actuales
                print()
            
            # Esperar 2 segundos
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoreo detenido")

def verificar_estado_actual():
    """Verificar el estado actual de los clics"""
    print("📊 ESTADO ACTUAL DE LOS CLICS")
    print("=" * 35)
    
    try:
        # Total de clics
        total_clics = ClickPropiedad.objects.count()
        print(f"📊 Total de clics: {total_clics}")
        
        # Clics de hoy
        hoy = timezone.now().date()
        clics_hoy = ClickPropiedad.objects.filter(fecha_click__date=hoy).count()
        print(f"📅 Clics de hoy: {clics_hoy}")
        
        # Últimos 5 clics
        if total_clics > 0:
            print("\n📋 Últimos 5 clics:")
            ultimos = ClickPropiedad.objects.all()[:5]
            for i, click in enumerate(ultimos, 1):
                print(f"   {i}. {click.propiedad.titulo} - {click.fecha_click.strftime('%d/%m/%Y %H:%M:%S')} - {click.pagina_origen}")
        
        # Clics por propiedad
        print("\n🏠 Clics por propiedad:")
        propiedades_con_clics = Propiedad.objects.filter(clicks__isnull=False).distinct()
        for propiedad in propiedades_con_clics:
            total_prop = propiedad.get_total_clicks()
            print(f"   - {propiedad.titulo}: {total_prop} clics")
        
        return total_clics
        
    except Exception as e:
        print(f"❌ Error al verificar estado: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 VERIFICADOR DE CLICS EN TIEMPO REAL")
    print("=" * 50)
    
    # Verificar estado inicial
    clics_iniciales = verificar_estado_actual()
    
    if clics_iniciales > 0:
        print(f"\n✅ Sistema funcionando - {clics_iniciales} clics registrados")
        print("\n🔄 Iniciando monitoreo...")
        print("💡 Ahora haz clic en 'Ver detalles' de cualquier propiedad")
        print("   y verás si se registra el nuevo clic aquí")
        print()
        monitorear_clics()
    else:
        print("\n⚠️ No hay clics registrados aún")
        print("💡 Haz clic en 'Ver detalles' de una propiedad y ejecuta este script nuevamente")

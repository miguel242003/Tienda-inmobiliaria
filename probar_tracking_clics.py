#!/usr/bin/env python
"""
Script para probar el tracking de clics
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

def probar_tracking():
    """Probar el sistema de tracking de clics"""
    print("🧪 Probando sistema de tracking de clics...")
    
    # Obtener una propiedad de prueba
    try:
        propiedad = Propiedad.objects.first()
        if not propiedad:
            print("❌ No hay propiedades en la base de datos")
            return False
        
        print(f"📋 Propiedad de prueba: {propiedad.titulo} (ID: {propiedad.id})")
        
        # Contar clics actuales
        clics_antes = propiedad.get_total_clicks()
        print(f"📊 Clics actuales: {clics_antes}")
        
        # Crear un click de prueba
        click = ClickPropiedad.objects.create(
            propiedad=propiedad,
            ip_address='127.0.0.1',
            user_agent='Test Script',
            pagina_origen='home'
        )
        print(f"✅ Click de prueba creado (ID: {click.id})")
        
        # Verificar que se incrementó
        clics_despues = propiedad.get_total_clicks()
        print(f"📊 Clics después: {clics_despues}")
        
        if clics_despues > clics_antes:
            print("✅ Sistema de tracking funciona correctamente!")
            
            # Probar estadísticas por mes
            clics_este_mes = propiedad.get_clicks_este_mes()
            clics_por_mes = propiedad.get_clicks_por_mes(6)
            
            print(f"📈 Clics este mes: {clics_este_mes}")
            print(f"📊 Clics por mes (últimos 6): {clics_por_mes}")
            
            return True
        else:
            print("❌ El sistema de tracking no está funcionando")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar tracking: {e}")
        return False

def limpiar_datos_prueba():
    """Limpiar los datos de prueba"""
    try:
        # Eliminar clics de prueba (con user_agent = 'Test Script')
        clics_eliminados = ClickPropiedad.objects.filter(user_agent='Test Script').delete()
        print(f"🧹 Eliminados {clics_eliminados[0]} clics de prueba")
    except Exception as e:
        print(f"⚠️ Error al limpiar datos: {e}")

if __name__ == "__main__":
    print("🔍 Verificando sistema de tracking de clics...")
    print()
    
    if probar_tracking():
        print("\n🎉 ¡El sistema de tracking está funcionando correctamente!")
        print("📋 El botón 'Ver Detalle' debería registrar clics en la base de datos")
        print("📊 Los gráficos de clics por mes deberían funcionar")
    else:
        print("\n❌ El sistema de tracking no está funcionando")
        print("🔧 Revisa la configuración de la base de datos")
    
    print("\n🧹 Limpiando datos de prueba...")
    limpiar_datos_prueba()

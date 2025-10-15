#!/usr/bin/env python
"""
Script para verificar la conexión a MySQL y aplicar migraciones
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

from django.core.management import execute_from_command_line
from django.db import connection
from django.conf import settings

def verificar_conexion():
    """Verificar la conexión a la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Conexión a MySQL exitosa!")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def aplicar_migraciones():
    """Aplicar todas las migraciones"""
    try:
        print("🔄 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones aplicadas exitosamente!")
        return True
    except Exception as e:
        print(f"❌ Error al aplicar migraciones: {e}")
        return False

def verificar_tabla_clics():
    """Verificar que la tabla de clics existe"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'tienda_inmobiliaria_prod' 
                AND table_name = 'propiedades_clickpropiedad'
            """)
            result = cursor.fetchone()
            if result[0] > 0:
                print("✅ Tabla de clics existe!")
                return True
            else:
                print("❌ Tabla de clics no existe!")
                return False
    except Exception as e:
        print(f"❌ Error al verificar tabla: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando configuración de MySQL...")
    print(f"Base de datos: {settings.DATABASES['default']['NAME']}")
    print(f"Usuario: {settings.DATABASES['default']['USER']}")
    print(f"Host: {settings.DATABASES['default']['HOST']}")
    print()
    
    if verificar_conexion():
        if aplicar_migraciones():
            verificar_tabla_clics()
        else:
            print("❌ No se pudieron aplicar las migraciones")
    else:
        print("❌ No se pudo conectar a la base de datos")
        print("\n📋 Pasos para solucionar:")
        print("1. Ejecutar el script configurar_mysql_clics.sql en MySQL")
        print("2. Verificar que MySQL esté ejecutándose")
        print("3. Verificar las credenciales en settings.py")

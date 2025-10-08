#!/usr/bin/env python
"""
Script para corregir migraciones en producción de forma segura
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def fix_migrations():
    """Corrige las migraciones de forma segura"""
    print("🔧 Corrigiendo migraciones en producción...")
    
    try:
        # 1. Verificar estado actual
        print("📊 Verificando estado de migraciones...")
        execute_from_command_line(['manage.py', 'showmigrations', 'propiedades'])
        
        # 2. Aplicar migraciones de forma segura
        print("🔄 Aplicando migraciones de forma segura...")
        
        # Intentar aplicar hasta la 0018
        try:
            execute_from_command_line(['manage.py', 'migrate', 'propiedades', '0018'])
            print("✅ Migración 0018 aplicada")
        except Exception as e:
            print(f"⚠️  Migración 0018: {e}")
        
        # Intentar aplicar 0019
        try:
            execute_from_command_line(['manage.py', 'migrate', 'propiedades', '0019'])
            print("✅ Migración 0019 aplicada")
        except Exception as e:
            print(f"⚠️  Migración 0019: {e}")
        
        # Intentar aplicar 0021 (WebP)
        try:
            execute_from_command_line(['manage.py', 'migrate', 'propiedades', '0021'])
            print("✅ Migración 0021 (WebP) aplicada")
        except Exception as e:
            print(f"⚠️  Migración 0021: {e}")
        
        # Intentar aplicar merge
        try:
            execute_from_command_line(['manage.py', 'migrate', 'propiedades', '0022'])
            print("✅ Migración 0022 (merge) aplicada")
        except Exception as e:
            print(f"⚠️  Migración 0022: {e}")
        
        # 3. Aplicar todas las migraciones restantes
        print("✅ Aplicando migraciones restantes...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("🎉 Migraciones corregidas exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_migrations()

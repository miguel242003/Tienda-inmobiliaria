#!/usr/bin/env python
"""
Script para cambiar temporalmente a SQLite y probar el tracking
"""
import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

def cambiar_a_sqlite():
    """Cambiar la configuración a SQLite temporalmente"""
    settings_file = BASE_DIR / 'tienda_meli' / 'tienda_meli' / 'settings.py'
    
    if not settings_file.exists():
        print("❌ No se encontró el archivo settings.py")
        return False
    
    # Leer el archivo actual
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Crear backup
    backup_file = settings_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup creado: {backup_file}")
    
    # Modificar la configuración para usar SQLite
    new_content = content.replace(
        "DB_ENGINE = 'django.db.backends.mysql'",
        "DB_ENGINE = 'django.db.backends.sqlite3'"
    )
    
    # Escribir el archivo modificado
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Configuración cambiada a SQLite")
    return True

def restaurar_mysql():
    """Restaurar la configuración de MySQL"""
    settings_file = BASE_DIR / 'tienda_meli' / 'tienda_meli' / 'settings.py'
    backup_file = settings_file.with_suffix('.py.backup')
    
    if backup_file.exists():
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Configuración restaurada a MySQL")
        return True
    else:
        print("❌ No se encontró el backup")
        return False

if __name__ == "__main__":
    print("🔧 Herramienta para cambiar entre MySQL y SQLite")
    print("1. Cambiar a SQLite (para probar)")
    print("2. Restaurar MySQL")
    print("3. Salir")
    
    opcion = input("\nSelecciona una opción (1-3): ")
    
    if opcion == "1":
        if cambiar_a_sqlite():
            print("\n📋 Ahora puedes ejecutar:")
            print("python manage.py migrate")
            print("python manage.py runserver")
            print("\nY probar el tracking de clics")
    elif opcion == "2":
        restaurar_mysql()
    elif opcion == "3":
        print("👋 ¡Hasta luego!")
    else:
        print("❌ Opción inválida")

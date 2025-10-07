#!/usr/bin/env python
"""
Script para instalar dependencias necesarias para optimización WebP
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

def check_package(package):
    """Verifica si un paquete está instalado"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    print("🚀 Instalando dependencias para optimización WebP...")
    print("=" * 50)
    
    # Lista de paquetes necesarios
    packages = [
        "Pillow>=10.0.0",  # Para manipulación de imágenes
    ]
    
    # Verificar e instalar paquetes
    all_installed = True
    
    for package in packages:
        package_name = package.split(">=")[0].split("==")[0]
        
        if check_package(package_name.lower()):
            print(f"✅ {package_name} ya está instalado")
        else:
            print(f"📦 Instalando {package}...")
            if not install_package(package):
                all_installed = False
    
    print("\n" + "=" * 50)
    
    if all_installed:
        print("🎉 ¡Todas las dependencias se instalaron correctamente!")
        print("\n📋 Próximos pasos:")
        print("1. Ejecuta las migraciones: python manage.py migrate")
        print("2. Optimiza imágenes existentes: python manage.py optimize_images")
        print("3. Reinicia tu servidor Django")
    else:
        print("⚠️  Algunas dependencias no se pudieron instalar.")
        print("Por favor, instálalas manualmente:")
        for package in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()

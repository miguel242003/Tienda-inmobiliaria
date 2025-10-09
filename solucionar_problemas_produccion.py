#!/usr/bin/env python3
"""
Script para solucionar problemas de producción en la tienda inmobiliaria
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n🔧 {step}: {message}")
    print("=" * 50)

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"📋 Ejecutando: {description}")
    print(f"💻 Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - ÉXITO")
            if result.stdout:
                print(f"📤 Salida: {result.stdout}")
        else:
            print(f"❌ {description} - ERROR")
            if result.stderr:
                print(f"📤 Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 SOLUCIONADOR DE PROBLEMAS DE PRODUCCIÓN")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("manage.py"):
        print("❌ Error: No se encontró manage.py. Ejecuta este script desde la raíz del proyecto.")
        sys.exit(1)
    
    # Paso 1: Configurar archivo .env
    print_step(1, "Configurando archivo .env para producción")
    
    if os.path.exists("config_produccion.env"):
        shutil.copy("config_produccion.env", ".env")
        print("✅ Archivo .env creado desde config_produccion.env")
    else:
        print("❌ No se encontró config_produccion.env")
        return False
    
    # Paso 2: Instalar dependencias de MySQL
    print_step(2, "Instalando dependencias de MySQL")
    
    mysql_deps = [
        "pip install pymysql",
        "pip install mysqlclient",
        "pip install django-mysql"
    ]
    
    for dep in mysql_deps:
        if not run_command(dep, f"Instalando {dep}"):
            print(f"⚠️  Advertencia: No se pudo instalar {dep}")
    
    # Paso 3: Verificar configuración de base de datos
    print_step(3, "Verificando configuración de base de datos")
    
    # Verificar que el archivo .env tiene la configuración correcta
    with open(".env", "r", encoding="utf-8") as f:
        env_content = f.read()
        
    if "DB_ENGINE=django.db.backends.mysql" in env_content:
        print("✅ Configuración de MySQL encontrada en .env")
    else:
        print("❌ Error: No se encontró configuración de MySQL en .env")
        return False
    
    # Paso 4: Ejecutar migraciones
    print_step(4, "Ejecutando migraciones de base de datos")
    
    migration_commands = [
        "python manage.py makemigrations",
        "python manage.py migrate",
        "python manage.py collectstatic --noinput"
    ]
    
    for cmd in migration_commands:
        if not run_command(cmd, f"Ejecutando {cmd}"):
            print(f"⚠️  Advertencia: Error en {cmd}")
    
    # Paso 5: Verificar configuración de seguridad
    print_step(5, "Verificando configuración de seguridad")
    
    # Verificar que DEBUG=False en .env
    if "DEBUG=False" in env_content:
        print("✅ DEBUG configurado correctamente para producción")
    else:
        print("⚠️  Advertencia: DEBUG no está configurado como False")
    
    # Verificar ALLOWED_HOSTS
    if "ALLOWED_HOSTS=" in env_content:
        print("✅ ALLOWED_HOSTS configurado")
    else:
        print("⚠️  Advertencia: ALLOWED_HOSTS no configurado")
    
    # Paso 6: Crear script de inicio para producción
    print_step(6, "Creando script de inicio para producción")
    
    start_script = """#!/bin/bash
# Script de inicio para producción

echo "🚀 Iniciando aplicación en modo producción..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Verificar que el archivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ Error: No se encontró el archivo .env"
    exit 1
fi

# Verificar configuración de base de datos
python manage.py check --deploy

# Iniciar servidor
echo "🌐 Iniciando servidor en modo producción..."
python manage.py runserver 0.0.0.0:8000
"""
    
    with open("start_production.sh", "w") as f:
        f.write(start_script)
    
    os.chmod("start_production.sh", 0o755)
    print("✅ Script de inicio creado: start_production.sh")
    
    # Paso 7: Crear script de Windows
    print_step(7, "Creando script de Windows")
    
    start_script_win = """@echo off
REM Script de inicio para producción en Windows

echo 🚀 Iniciando aplicación en modo producción...

REM Verificar que el archivo .env existe
if not exist ".env" (
    echo ❌ Error: No se encontró el archivo .env
    pause
    exit /b 1
)

REM Verificar configuración de base de datos
python manage.py check --deploy

REM Iniciar servidor
echo 🌐 Iniciando servidor en modo producción...
python manage.py runserver 0.0.0.0:8000

pause
"""
    
    with open("start_production.bat", "w") as f:
        f.write(start_script_win)
    
    print("✅ Script de Windows creado: start_production.bat")
    
    # Paso 8: Verificar configuración final
    print_step(8, "Verificación final")
    
    # Verificar que todos los archivos necesarios existen
    required_files = [
        ".env",
        "manage.py",
        "start_production.sh",
        "start_production.bat"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} existe")
        else:
            print(f"❌ {file} no encontrado")
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Configura tu base de datos MySQL:")
    print("   - Crea la base de datos: tienda_inmobiliaria_prod")
    print("   - Crea el usuario: tienda_user")
    print("   - Actualiza la contraseña en .env")
    print("")
    print("2. Para iniciar en Linux/Mac:")
    print("   ./start_production.sh")
    print("")
    print("3. Para iniciar en Windows:")
    print("   start_production.bat")
    print("")
    print("4. Accede a tu aplicación:")
    print("   http://tu-dominio.com:8000")
    print("")
    print("🔧 Si tienes problemas:")
    print("- Revisa los logs en logs/django.log")
    print("- Verifica la configuración de MySQL")
    print("- Asegúrate de que el puerto 8000 esté disponible")

if __name__ == "__main__":
    main()

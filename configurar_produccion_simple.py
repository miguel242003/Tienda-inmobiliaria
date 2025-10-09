#!/usr/bin/env python3
"""
Script simple para configurar producción
"""

import os
import shutil

def main():
    print("Configurando produccion...")
    
    # 1. Copiar archivo .env
    if os.path.exists("config_produccion.env"):
        shutil.copy("config_produccion.env", ".env")
        print("Archivo .env creado")
    else:
        print("Error: No se encontro config_produccion.env")
        return False
    
    # 2. Crear script de inicio simple
    start_script = """@echo off
echo Iniciando aplicacion en modo produccion...

REM Verificar archivo .env
if not exist ".env" (
    echo Error: No se encontro el archivo .env
    pause
    exit /b 1
)

REM Iniciar servidor
python manage.py runserver 0.0.0.0:8000
pause
"""
    
    with open("start_production.bat", "w", encoding="utf-8") as f:
        f.write(start_script)
    
    print("Script de inicio creado: start_production.bat")
    
    print("\nConfiguracion completada!")
    print("Proximos pasos:")
    print("1. Configura MySQL con los datos del archivo .env")
    print("2. Ejecuta: start_production.bat")
    print("3. Accede a: http://localhost:8000")

if __name__ == "__main__":
    main()

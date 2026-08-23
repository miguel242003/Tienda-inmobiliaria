#!/usr/bin/env python3
"""
Script para ejecutar el servidor en producción con Gunicorn
"""
import os
import sys
import subprocess
from pathlib import Path

def run_production_server():
    """Ejecutar el servidor de producción con Gunicorn"""
    print("🚀 Iniciando servidor de producción...")
    print("📝 Configuración: DEBUG=False (producción)")
    print("🔧 Usando Gunicorn como servidor WSGI")
    print("=" * 60)
    
    # Configurar variables de entorno para producción
    os.environ['DEBUG'] = 'False'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tienda_meli.tienda_meli.settings'
    
    try:
        # Verificar si Gunicorn está instalado
        try:
            subprocess.run(['gunicorn', '--version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Gunicorn no está instalado. Instalando...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn'])
        
        # Ejecutar Gunicorn
        subprocess.run([
            'gunicorn',
            '--bind', '0.0.0.0:8000',
            '--workers', '3',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            'tienda_meli.tienda_meli.wsgi:application'
        ], cwd=Path(__file__).parent)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al ejecutar el servidor: {e}")

if __name__ == "__main__":
    run_production_server()

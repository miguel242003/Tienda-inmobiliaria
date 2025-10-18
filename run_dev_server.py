#!/usr/bin/env python
"""
Script para ejecutar el servidor de desarrollo con la configuración correcta
"""
import os
import sys
import subprocess
from pathlib import Path

def run_dev_server():
    """Ejecutar el servidor de desarrollo con DEBUG=True"""
    print("🚀 Iniciando servidor de desarrollo...")
    print("📝 Configuración: DEBUG=True (desarrollo)")
    print("🔧 Esto evita las redirecciones HTTPS y permite acceso local")
    print("=" * 60)
    
    # Configurar variables de entorno para desarrollo
    os.environ['DEBUG'] = 'True'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tienda_meli.tienda_meli.settings'
    
    try:
        # Ejecutar el servidor de desarrollo
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '8000'
        ], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al ejecutar el servidor: {e}")

if __name__ == "__main__":
    run_dev_server()

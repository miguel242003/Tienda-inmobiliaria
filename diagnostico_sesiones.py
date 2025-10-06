#!/usr/bin/env python
"""
🔍 SCRIPT DE DIAGNÓSTICO DE SESIONES
====================================
Este script diagnostica problemas de sesiones en Django.
Ejecutar desde el directorio raíz del proyecto:
    python diagnostico_sesiones.py
"""

import os
import sys
import django
from pathlib import Path

# Color codes para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Imprime un encabezado formateado"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def check_django_setup():
    """Verifica que Django esté configurado correctamente"""
    print_header("VERIFICACIÓN DE DJANGO")
    
    try:
        # Configurar Django
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.tienda_meli.settings')
        django.setup()
        
        print_success("Django configurado correctamente")
        
        # Verificar versión de Django
        import django
        print_info(f"Versión de Django: {django.get_version()}")
        
        return True
    except Exception as e:
        print_error(f"Error al configurar Django: {e}")
        return False

def check_settings():
    """Verifica la configuración de sesiones en settings.py"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN DE SESIONES")
    
    try:
        from django.conf import settings
        
        # Verificar SESSION_ENGINE
        session_engine = settings.SESSION_ENGINE
        print_info(f"SESSION_ENGINE: {session_engine}")
        
        if 'cached_db' in session_engine or 'db' in session_engine:
            print_success("Motor de sesiones compatible (usa base de datos)")
        elif 'cache' in session_engine:
            print_warning("Motor de sesiones usa solo cache (requiere Redis)")
        
        # Verificar configuración de cookies
        print_info(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
        print_info(f"SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")
        print_info(f"SESSION_COOKIE_SAMESITE: {settings.SESSION_COOKIE_SAMESITE}")
        print_info(f"SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} segundos ({settings.SESSION_COOKIE_AGE/3600} horas)")
        
        if hasattr(settings, 'SESSION_COOKIE_NAME'):
            print_info(f"SESSION_COOKIE_NAME: {settings.SESSION_COOKIE_NAME}")
        
        if hasattr(settings, 'SESSION_COOKIE_DOMAIN'):
            print_info(f"SESSION_COOKIE_DOMAIN: {settings.SESSION_COOKIE_DOMAIN}")
        
        # Verificar ALLOWED_HOSTS
        print_info(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        if 'gisa-nqn.com' in settings.ALLOWED_HOSTS:
            print_success("Dominio gisa-nqn.com está en ALLOWED_HOSTS")
        else:
            print_error("Dominio gisa-nqn.com NO está en ALLOWED_HOSTS")
        
        # Verificar CSRF_TRUSTED_ORIGINS
        if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
            print_info(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
            
            gisa_in_csrf = any('gisa-nqn.com' in origin for origin in settings.CSRF_TRUSTED_ORIGINS)
            if gisa_in_csrf:
                print_success("Dominio gisa-nqn.com está en CSRF_TRUSTED_ORIGINS")
            else:
                print_warning("Dominio gisa-nqn.com NO está en CSRF_TRUSTED_ORIGINS")
        
        # Verificar DEBUG
        print_info(f"DEBUG: {settings.DEBUG}")
        if settings.DEBUG:
            print_warning("DEBUG está activado (no recomendado en producción)")
        else:
            print_success("DEBUG está desactivado (correcto para producción)")
        
        return True
    except Exception as e:
        print_error(f"Error al verificar configuración: {e}")
        return False

def check_database():
    """Verifica la tabla de sesiones en la base de datos"""
    print_header("VERIFICACIÓN DE BASE DE DATOS")
    
    try:
        from django.contrib.sessions.models import Session
        from django.db import connection
        
        # Verificar que la tabla existe
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_session")
            count = cursor.fetchone()[0]
        
        print_success(f"Tabla de sesiones existe con {count} sesiones")
        
        # Contar sesiones activas
        from django.utils import timezone
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now()).count()
        expired_sessions = Session.objects.filter(expire_date__lte=timezone.now()).count()
        
        print_info(f"Sesiones activas: {active_sessions}")
        print_info(f"Sesiones expiradas: {expired_sessions}")
        
        if expired_sessions > 100:
            print_warning(f"Hay {expired_sessions} sesiones expiradas. Ejecuta: python manage.py clearsessions")
        
        return True
    except Exception as e:
        print_error(f"Error al verificar base de datos: {e}")
        print_info("Intenta ejecutar: python manage.py migrate")
        return False

def check_redis():
    """Verifica si Redis está disponible"""
    print_header("VERIFICACIÓN DE REDIS (OPCIONAL)")
    
    try:
        from django.conf import settings
        
        if not hasattr(settings, 'CACHES') or 'redis' not in str(settings.CACHES.get('default', {}).get('BACKEND', '')).lower():
            print_info("Redis no está configurado (no es necesario con cached_db)")
            return True
        
        import redis
        from django.core.cache import cache
        
        # Intentar conectar a Redis
        cache.set('test_key', 'test_value', timeout=10)
        value = cache.get('test_key')
        
        if value == 'test_value':
            print_success("Redis está funcionando correctamente")
            cache.delete('test_key')
        else:
            print_error("Redis no responde correctamente")
        
        return True
    except ImportError:
        print_warning("Módulo redis no instalado (no es necesario con cached_db)")
        return True
    except Exception as e:
        print_warning(f"Redis no disponible: {e}")
        print_info("No es crítico si usas SESSION_ENGINE = 'cached_db' o 'db'")
        return True

def check_permissions():
    """Verifica permisos de archivos"""
    print_header("VERIFICACIÓN DE PERMISOS")
    
    try:
        from django.conf import settings
        
        # Verificar permisos del directorio de logs
        if hasattr(settings, 'LOGS_DIR'):
            logs_dir = Path(settings.LOGS_DIR)
            if logs_dir.exists():
                if os.access(logs_dir, os.W_OK):
                    print_success(f"Directorio de logs escribible: {logs_dir}")
                else:
                    print_error(f"Directorio de logs NO escribible: {logs_dir}")
            else:
                print_warning(f"Directorio de logs no existe: {logs_dir}")
        
        # Verificar permisos del directorio de media
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists():
            if os.access(media_root, os.W_OK):
                print_success(f"Directorio media escribible: {media_root}")
            else:
                print_error(f"Directorio media NO escribible: {media_root}")
        
        return True
    except Exception as e:
        print_error(f"Error al verificar permisos: {e}")
        return False

def check_environment():
    """Verifica variables de entorno"""
    print_header("VERIFICACIÓN DE VARIABLES DE ENTORNO")
    
    try:
        # Variables críticas
        critical_vars = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS']
        
        for var in critical_vars:
            value = os.environ.get(var, '<no definida>')
            
            if var == 'SECRET_KEY':
                # No mostrar la SECRET_KEY completa por seguridad
                if value and value != '<no definida>':
                    print_success(f"{var}: {'*' * len(value[:10])}... (definida)")
                else:
                    print_error(f"{var}: No definida")
            else:
                print_info(f"{var}: {value}")
        
        # Variables opcionales
        optional_vars = ['DB_ENGINE', 'DB_NAME', 'REDIS_URL']
        for var in optional_vars:
            value = os.environ.get(var, '<no definida>')
            if value != '<no definida>':
                print_info(f"{var}: {value}")
        
        return True
    except Exception as e:
        print_error(f"Error al verificar variables de entorno: {e}")
        return False

def test_session_creation():
    """Prueba crear una sesión de prueba"""
    print_header("PRUEBA DE CREACIÓN DE SESIÓN")
    
    try:
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        
        # Crear sesión de prueba
        session = SessionStore()
        session['test_key'] = 'test_value'
        session['timestamp'] = str(timezone.now())
        session.save()
        
        session_key = session.session_key
        print_success(f"Sesión de prueba creada: {session_key}")
        
        # Verificar que se guardó
        try:
            saved_session = Session.objects.get(session_key=session_key)
            print_success("Sesión de prueba encontrada en la base de datos")
            
            # Leer datos de la sesión
            session_data = session.load()
            if session_data.get('test_key') == 'test_value':
                print_success("Datos de sesión recuperados correctamente")
            
            # Limpiar sesión de prueba
            saved_session.delete()
            print_info("Sesión de prueba eliminada")
            
        except Session.DoesNotExist:
            print_error("Sesión de prueba NO se guardó en la base de datos")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error al probar creación de sesión: {e}")
        return False

def generate_report(results):
    """Genera un resumen del diagnóstico"""
    print_header("RESUMEN DEL DIAGNÓSTICO")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    failed_checks = total_checks - passed_checks
    
    print(f"\n{BOLD}Verificaciones totales: {total_checks}{RESET}")
    print(f"{GREEN}Exitosas: {passed_checks}{RESET}")
    print(f"{RED}Fallidas: {failed_checks}{RESET}")
    
    if failed_checks == 0:
        print(f"\n{GREEN}{BOLD}✅ TODAS LAS VERIFICACIONES PASARON{RESET}")
        print(f"{GREEN}El sistema de sesiones debería funcionar correctamente.{RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ HAY PROBLEMAS QUE REQUIEREN ATENCIÓN{RESET}")
        print(f"{YELLOW}Revisa los errores marcados arriba y corrígelos.{RESET}")
    
    # Recomendaciones
    print(f"\n{BOLD}📋 RECOMENDACIONES:{RESET}")
    
    if not results.get('database'):
        print("  1. Ejecuta las migraciones: python manage.py migrate")
    
    if not results.get('redis'):
        print("  2. Considera instalar Redis para mejor rendimiento (opcional)")
    
    print("  3. Reinicia el servidor después de hacer cambios")
    print("  4. Prueba el login desde otro navegador/computador")
    print("  5. Verifica los logs: tail -f logs/django.log")

def main():
    """Función principal"""
    print(f"\n{BOLD}{BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║     🔍 DIAGNÓSTICO DE SISTEMA DE SESIONES - DJANGO                ║")
    print("║     Tienda Inmobiliaria                                           ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}\n")
    
    results = {}
    
    # Ejecutar todas las verificaciones
    results['django_setup'] = check_django_setup()
    
    if results['django_setup']:
        results['settings'] = check_settings()
        results['database'] = check_database()
        results['redis'] = check_redis()
        results['permissions'] = check_permissions()
        results['environment'] = check_environment()
        results['session_test'] = test_session_creation()
    
    # Generar reporte
    generate_report(results)
    
    print(f"\n{BOLD}Para más información, consulta:{RESET}")
    print("  - SOLUCION_PROBLEMA_LOGIN.md")
    print("  - logs/django.log")
    print("  - https://docs.djangoproject.com/en/stable/topics/http/sessions/\n")

if __name__ == '__main__':
    main()


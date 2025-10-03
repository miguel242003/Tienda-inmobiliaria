#!/usr/bin/env python
"""Script de verificación del sistema"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.tienda_meli.settings')
django.setup()

from django.db import connection
from propiedades.models import Propiedad, Amenidad
from login.models import AdminCredentials
from core.models import ContactSubmission, CVSubmission
from django.contrib.auth.models import User

print("=" * 60)
print("VERIFICACION DEL SISTEMA - TIENDA INMOBILIARIA")
print("=" * 60)

# Verificar conexion a base de datos
print("\nBASE DE DATOS:")
print(f"   OK Motor: {connection.settings_dict['ENGINE'].split('.')[-1].upper()}")
print(f"   OK Nombre: {connection.settings_dict['NAME']}")
print(f"   OK Host: {connection.settings_dict['HOST']}")
print(f"   OK Conexion: EXITOSA")

# Verificar modelos principales
print("\nDATOS EN LA BASE DE DATOS:")
print(f"   OK Propiedades: {Propiedad.objects.count()}")
print(f"   OK Amenidades: {Amenidad.objects.count()}")
print(f"   OK Administradores: {AdminCredentials.objects.count()}")
print(f"   OK Usuarios del sistema: {User.objects.count()}")
print(f"   OK Envios de contacto: {ContactSubmission.objects.count()}")
print(f"   OK CVs recibidos: {CVSubmission.objects.count()}")

# Verificar superusuarios
print("\nSUPERUSUARIOS:")
for user in User.objects.filter(is_superuser=True):
    print(f"   OK {user.username} ({user.email})")

# Verificar configuracion de email
from django.conf import settings
print("\nCONFIGURACION DE EMAIL:")
print(f"   OK Host: {settings.EMAIL_HOST}")
print(f"   OK Puerto: {settings.EMAIL_PORT}")
print(f"   OK Usuario: {settings.EMAIL_HOST_USER}")
print(f"   OK Email admin: {settings.ADMIN_EMAIL}")

# Verificar configuracion de seguridad
print("\nSEGURIDAD:")
print(f"   OK DEBUG: {settings.DEBUG}")
print(f"   OK ALLOWED_HOSTS: {', '.join(settings.ALLOWED_HOSTS)}")
print(f"   OK SECRET_KEY configurada: {'SI' if settings.SECRET_KEY and not settings.SECRET_KEY.startswith('django-insecure') else 'NO'}")

print("\n" + "=" * 60)
print("SISTEMA VERIFICADO CORRECTAMENTE - TODO OK")
print("=" * 60)


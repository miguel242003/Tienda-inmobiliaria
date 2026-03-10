#!/usr/bin/env python
"""
Script simple para eliminar todas las propiedades de MySQL
Ejecutar: python eliminar_propiedades.py
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.tienda_meli.settings')
django.setup()

from propiedades.models import Propiedad, FotoPropiedad, ClickPropiedad, Resena
from core.utils import eliminar_imagenes_static_propiedad

# Contar antes
total = Propiedad.objects.count()
print(f"📊 Propiedades encontradas: {total}")

if total > 0:
    # Eliminar imágenes estáticas
    print("🗑️  Eliminando imágenes estáticas...")
    for p in Propiedad.objects.all():
        if p.slug:
            eliminar_imagenes_static_propiedad(p.slug)
    
    # Eliminar todas las propiedades
    print("🗑️  Eliminando propiedades de MySQL...")
    deleted = Propiedad.objects.all().delete()
    print(f"✅ Eliminadas: {deleted[0]} propiedades")
else:
    print("✅ No hay propiedades para eliminar")

# Verificar
print(f"\n📊 Estado final:")
print(f"   Propiedades: {Propiedad.objects.count()}")
print(f"   Fotos: {FotoPropiedad.objects.count()}")
print(f"   Clics: {ClickPropiedad.objects.count()}")
print(f"   Reseñas: {Resena.objects.count()}")



#!/usr/bin/env python
"""
Script para eliminar todas las propiedades de la base de datos MySQL
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.tienda_meli.settings')
django.setup()

from propiedades.models import Propiedad, FotoPropiedad, ClickPropiedad, Resena
from core.utils import eliminar_imagenes_static_propiedad

def eliminar_todas_propiedades():
    """Elimina todas las propiedades de la base de datos"""
    try:
        # Contar propiedades antes de eliminar
        total_propiedades = Propiedad.objects.count()
        print(f"📊 Propiedades encontradas: {total_propiedades}")
        
        if total_propiedades == 0:
            print("✅ No hay propiedades para eliminar")
            return
        
        # Obtener todas las propiedades con sus slugs para eliminar imágenes estáticas
        propiedades = Propiedad.objects.all()
        
        print(f"\n🗑️  Iniciando eliminación de {total_propiedades} propiedades...")
        
        # Eliminar imágenes estáticas de cada propiedad
        for propiedad in propiedades:
            try:
                if propiedad.slug:
                    resultado = eliminar_imagenes_static_propiedad(propiedad.slug)
                    if resultado['success']:
                        print(f"  ✅ Imágenes estáticas eliminadas: {propiedad.titulo}")
                    else:
                        print(f"  ⚠️  Advertencia al eliminar imágenes estáticas de {propiedad.titulo}: {resultado['message']}")
            except Exception as e:
                print(f"  ⚠️  Error al eliminar imágenes estáticas de {propiedad.titulo}: {e}")
        
        # Eliminar todas las propiedades (esto también eliminará en cascada: fotos, clics, reseñas)
        deleted = Propiedad.objects.all().delete()
        
        print(f"\n✅ Eliminación completada:")
        print(f"   - Propiedades eliminadas: {deleted[0]}")
        
        # Verificar que se eliminaron correctamente
        propiedades_restantes = Propiedad.objects.count()
        fotos_restantes = FotoPropiedad.objects.count()
        clics_restantes = ClickPropiedad.objects.count()
        reseñas_restantes = Resena.objects.count()
        
        print(f"\n📊 Estado final:")
        print(f"   - Propiedades restantes: {propiedades_restantes}")
        print(f"   - Fotos restantes: {fotos_restantes}")
        print(f"   - Clics restantes: {clics_restantes}")
        print(f"   - Reseñas restantes: {reseñas_restantes}")
        
        if propiedades_restantes == 0:
            print("\n✅ ¡Todas las propiedades han sido eliminadas exitosamente de MySQL!")
        else:
            print(f"\n⚠️  Advertencia: Aún quedan {propiedades_restantes} propiedades")
            
    except Exception as e:
        print(f"\n❌ Error al eliminar propiedades: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("ELIMINACIÓN DE TODAS LAS PROPIEDADES")
    print("=" * 60)
    
    respuesta = input("\n⚠️  ¿Estás seguro de que quieres eliminar TODAS las propiedades? (escribe 'SI' para confirmar): ")
    
    if respuesta.upper() == 'SI':
        eliminar_todas_propiedades()
    else:
        print("\n❌ Operación cancelada")


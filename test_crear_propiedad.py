#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de creación de propiedades.
Este script simula la creación de una propiedad para verificar que no hay errores.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.settings')
django.setup()

from propiedades.models import Propiedad, Amenidad
from propiedades.forms import PropiedadForm
from propiedades.validators import validar_imagen, validar_imagen_o_video
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

def test_amenidades():
    """Verificar que las amenidades estén disponibles"""
    print("🔍 Verificando amenidades...")
    amenidades = Amenidad.objects.all()
    print(f"✅ Amenidades encontradas: {amenidades.count()}")
    for amenidad in amenidades:
        print(f"   - {amenidad.nombre}")
    return amenidades.count() > 0

def test_validadores():
    """Probar los validadores de archivos"""
    print("\n🔍 Probando validadores de archivos...")
    
    # Crear un archivo de prueba vacío (simulando el error)
    archivo_vacio = SimpleUploadedFile(
        "test_empty.jpg",
        b"",  # Archivo vacío
        content_type="image/jpeg"
    )
    
    try:
        validar_imagen(archivo_vacio)
        print("❌ ERROR: El validador debería rechazar archivos vacíos")
        return False
    except ValidationError as e:
        print(f"✅ Validación correcta para archivo vacío: {e}")
    
    # Crear un archivo de prueba válido
    archivo_valido = SimpleUploadedFile(
        "test_valid.jpg",
        b"fake image content",  # Contenido simulado
        content_type="image/jpeg"
    )
    
    try:
        # Este debería fallar porque no es una imagen real
        validar_imagen(archivo_valido)
        print("❌ ERROR: El validador debería rechazar contenido falso")
        return False
    except ValidationError as e:
        print(f"✅ Validación correcta para contenido falso: {e}")
    
    return True

def test_formulario():
    """Probar el formulario de creación de propiedades"""
    print("\n🔍 Probando formulario de creación...")
    
    # Datos de prueba
    datos_prueba = {
        'titulo': 'Casa de prueba para validación',
        'descripcion': 'Esta es una descripción de prueba para verificar que el formulario funciona correctamente.',
        'precio': 100000,
        'tipo': 'casa',
        'operacion': 'venta',
        'estado': 'disponible',
        'ubicacion': 'Dirección de prueba 123, Ciudad de Prueba',
        'ciudad': 'Ciudad de Prueba',
        'lugares_cercanos': 'Centro comercial, supermercado, farmacia, restaurantes',
        'metros_cuadrados': 100,
        'habitaciones': 3,
        'banos': 2,
        'ambientes': 5,
        'balcon': True,
        'latitud': -33.6914783645518,
        'longitud': -65.45524318970048,
    }
    
    form = PropiedadForm(data=datos_prueba)
    
    if form.is_valid():
        print("✅ Formulario válido con datos de prueba")
        return True
    else:
        print("❌ Errores en el formulario:")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"   - {field}: {error}")
        return False

def test_importaciones():
    """Verificar que todas las importaciones funcionen correctamente"""
    print("\n🔍 Verificando importaciones...")
    
    try:
        from propiedades.views import crear_propiedad
        print("✅ Vista crear_propiedad importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando crear_propiedad: {e}")
        return False
    
    try:
        from propiedades.models import Amenidad
        print("✅ Modelo Amenidad importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Amenidad: {e}")
        return False
    
    return True

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de creación de propiedades...")
    print("=" * 60)
    
    tests = [
        ("Importaciones", test_importaciones),
        ("Amenidades", test_amenidades),
        ("Validadores", test_validadores),
        ("Formulario", test_formulario),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    exitos = 0
    for nombre, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status} {nombre}")
        if resultado:
            exitos += 1
    
    print(f"\n🎯 Resultado: {exitos}/{len(resultados)} pruebas exitosas")
    
    if exitos == len(resultados):
        print("🎉 ¡Todas las pruebas pasaron! La funcionalidad debería estar funcionando.")
        return True
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

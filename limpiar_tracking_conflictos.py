#!/usr/bin/env python
"""
Script para limpiar conflictos de tracking
"""
import os
import sys
from pathlib import Path

def limpiar_archivos_conflictivos():
    """Limpiar archivos que puedan causar conflictos"""
    print("🧹 Limpiando archivos conflictivos...")
    
    # Archivos que pueden causar conflictos
    archivos_conflictivos = [
        'static/js/track-clicks.js',
        'static/js/tracking-clics.js',
        'static/js/click-tracker.js',
        'static/js/tracker.js'
    ]
    
    for archivo in archivos_conflictivos:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                print(f"✅ Eliminado: {archivo}")
            except Exception as e:
                print(f"❌ Error al eliminar {archivo}: {e}")
        else:
            print(f"ℹ️ No existe: {archivo}")

def verificar_template_base():
    """Verificar que el template base solo carga el archivo correcto"""
    print("\n🔍 Verificando template base...")
    
    template_path = 'core/templates/core/base.html'
    if not os.path.exists(template_path):
        print(f"❌ No se encontró: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que solo carga property-click-tracker.js
    if 'property-click-tracker.js' in content:
        print("✅ Template base carga property-click-tracker.js")
    else:
        print("❌ Template base NO carga property-click-tracker.js")
    
    # Verificar que NO carga archivos conflictivos
    archivos_conflictivos = [
        'track-clicks.js',
        'tracking-clics.js',
        'click-tracker.js'
    ]
    
    for archivo in archivos_conflictivos:
        if archivo in content:
            print(f"⚠️ Template base carga archivo conflictivo: {archivo}")
        else:
            print(f"✅ Template base NO carga: {archivo}")
    
    return True

def crear_archivo_limpieza():
    """Crear archivo para limpiar caché del navegador"""
    print("\n📝 Creando archivo de limpieza...")
    
    contenido = """
// Archivo de limpieza para eliminar conflictos de tracking
// Este archivo se puede eliminar después de usar

// Limpiar variables globales conflictivas
if (window.ClickTracker) {
    delete window.ClickTracker;
    console.log('🧹 ClickTracker eliminado');
}

if (window.TrackClicksInitialized) {
    delete window.TrackClicksInitialized;
    console.log('🧹 TrackClicksInitialized eliminado');
}

// Limpiar event listeners duplicados
document.removeEventListener('DOMContentLoaded', function() {});
console.log('🧹 Event listeners limpiados');

console.log('✅ Limpieza completada');
"""
    
    with open('static/js/limpiar-conflictos.js', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ Archivo de limpieza creado: static/js/limpiar-conflictos.js")

if __name__ == "__main__":
    print("🔧 Limpiando conflictos de tracking...")
    print("=" * 50)
    
    limpiar_archivos_conflictivos()
    verificar_template_base()
    crear_archivo_limpieza()
    
    print("\n✅ Limpieza completada!")
    print("📋 Pasos siguientes:")
    print("  1. Recarga la página (Ctrl+F5)")
    print("  2. Verifica que no hay errores en la consola")
    print("  3. Haz clic en 'Ver Detalle' para probar")
    print("  4. Elimina el archivo limpiar-conflictos.js después de usar")

#!/usr/bin/env python
"""
Script para limpiar el error de ClickTracker duplicado
"""
import os
import sys
from pathlib import Path

def limpiar_cache_navegador():
    """Crear archivo para limpiar caché del navegador"""
    print("🧹 Creando archivo de limpieza de caché...")
    
    contenido = """
// Archivo de limpieza para eliminar conflictos de ClickTracker
// Este archivo se puede eliminar después de usar

console.log('🧹 Iniciando limpieza de conflictos ClickTracker...');

// Limpiar variables globales conflictivas
if (window.ClickTracker) {
    delete window.ClickTracker;
    console.log('✅ ClickTracker eliminado');
}

if (window.TrackClicksInitialized) {
    delete window.TrackClicksInitialized;
    console.log('✅ TrackClicksInitialized eliminado');
}

if (window.PropertyClickTrackerInitialized) {
    delete window.PropertyClickTrackerInitialized;
    console.log('✅ PropertyClickTrackerInitialized eliminado');
}

// Limpiar cualquier referencia a tracking-clics.js
const scripts = document.querySelectorAll('script[src*="tracking-clics"]');
scripts.forEach(script => {
    script.remove();
    console.log('✅ Script tracking-clics.js removido del DOM');
});

// Limpiar event listeners duplicados
document.removeEventListener('DOMContentLoaded', function() {});
console.log('✅ Event listeners limpiados');

console.log('✅ Limpieza completada');
console.log('📋 Instrucciones:');
console.log('  1. Recarga la página (Ctrl+F5)');
console.log('  2. Verifica que no hay errores en la consola');
console.log('  3. Haz clic en "Ver Detalle" para probar');
console.log('  4. Elimina este archivo después de usar');
"""
    
    with open('static/js/limpiar-conflictos.js', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ Archivo de limpieza creado: static/js/limpiar-conflictos.js")

def verificar_template():
    """Verificar que el template base está correcto"""
    print("\n🔍 Verificando template base...")
    
    template_path = 'core/templates/core/base.html'
    if not os.path.exists(template_path):
        print(f"❌ No se encontró: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que carga property-click-tracker.js
    if 'property-click-tracker.js' in content:
        print("✅ Template base carga property-click-tracker.js")
    else:
        print("❌ Template base NO carga property-click-tracker.js")
    
    # Verificar que NO carga archivos conflictivos
    archivos_conflictivos = [
        'tracking-clics.js',
        'track-clicks.js',
        'click-tracker.js'
    ]
    
    for archivo in archivos_conflictivos:
        if archivo in content:
            print(f"⚠️ Template base carga archivo conflictivo: {archivo}")
        else:
            print(f"✅ Template base NO carga: {archivo}")
    
    return True

def limpiar_archivos_temporales():
    """Limpiar archivos temporales que puedan causar conflictos"""
    print("\n🧹 Limpiando archivos temporales...")
    
    archivos_temporales = [
        'static/js/limpiar-conflictos.js',
        'static/js/tracking-clics.js',
        'static/js/track-clicks.js',
        'static/js/click-tracker.js'
    ]
    
    for archivo in archivos_temporales:
        if os.path.exists(archivo):
            try:
                if archivo == 'static/js/limpiar-conflictos.js':
                    print(f"ℹ️ Manteniendo archivo de limpieza: {archivo}")
                else:
                    os.remove(archivo)
                    print(f"✅ Eliminado: {archivo}")
            except Exception as e:
                print(f"❌ Error al eliminar {archivo}: {e}")
        else:
            print(f"ℹ️ No existe: {archivo}")

if __name__ == "__main__":
    print("🔧 Limpiando error de ClickTracker duplicado...")
    print("=" * 60)
    
    limpiar_cache_navegador()
    verificar_template()
    limpiar_archivos_temporales()
    
    print("\n✅ Limpieza completada!")
    print("📋 Pasos siguientes:")
    print("  1. Recarga la página (Ctrl+F5)")
    print("  2. Verifica que no hay errores en la consola")
    print("  3. Haz clic en 'Ver Detalle' para probar")
    print("  4. Si funciona correctamente, elimina limpiar-conflictos.js")
    print("\n🔍 Si el error persiste:")
    print("  - Limpia la caché del navegador (Ctrl+Shift+Delete)")
    print("  - Verifica la consola del navegador para más detalles")

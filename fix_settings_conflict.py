#!/usr/bin/env python
"""
Script para arreglar el conflicto de merge en settings.py
"""
import os
import re

def arreglar_conflicto_settings():
    """Arreglar el conflicto de merge en settings.py"""
    
    settings_path = 'tienda_meli/tienda_meli/settings.py'
    
    if not os.path.exists(settings_path):
        print(f"❌ No se encontró el archivo: {settings_path}")
        return False
    
    # Leer el archivo
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar marcadores de conflicto
    if '<<<<<<< HEAD' in content or '=======' in content or '>>>>>>>' in content:
        print("🔍 Se encontraron marcadores de conflicto en settings.py")
        
        # Eliminar marcadores de conflicto y mantener solo la versión HEAD
        lines = content.split('\n')
        new_lines = []
        skip_until_end = False
        
        for line in lines:
            if line.strip().startswith('<<<<<<< HEAD'):
                skip_until_end = False
                continue
            elif line.strip().startswith('======='):
                skip_until_end = True
                continue
            elif line.strip().startswith('>>>>>>>'):
                skip_until_end = False
                continue
            elif not skip_until_end:
                new_lines.append(line)
        
        # Escribir el archivo arreglado
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Conflicto de merge arreglado en settings.py")
        return True
    else:
        print("✅ No se encontraron conflictos en settings.py")
        return True

if __name__ == "__main__":
    print("🔧 Arreglando conflicto de merge en settings.py...")
    if arreglar_conflicto_settings():
        print("✅ settings.py arreglado correctamente")
    else:
        print("❌ Error al arreglar settings.py")

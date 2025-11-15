#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir imágenes a WebP y optimizar imágenes existentes
Requiere: pip install pillow
"""

import os
from PIL import Image
import sys

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def convert_to_webp(input_path, output_path, quality=85):
    """Convierte una imagen a WebP"""
    try:
        img = Image.open(input_path)
        
        # Si la imagen tiene transparencia, mantenerla
        if img.mode in ('RGBA', 'LA', 'P'):
            img.save(output_path, 'WEBP', quality=quality, method=6)
        else:
            # Convertir a RGB si no tiene canal alpha
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, 'WEBP', quality=quality, method=6)
        
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        new_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"[OK] Convertido: {os.path.basename(input_path)}")
        print(f"  Tamaño original: {original_size:.2f} MB")
        print(f"  Tamaño nuevo: {new_size:.2f} MB")
        print(f"  Reducción: {reduction:.1f}%")
        return True
    except Exception as e:
        print(f"[ERROR] Error al convertir {input_path}: {e}")
        return False

def optimize_webp(input_path, output_path, quality=80):
    """Optimiza una imagen WebP existente"""
    try:
        img = Image.open(input_path)
        
        # Si la imagen tiene transparencia, mantenerla
        if img.mode in ('RGBA', 'LA', 'P'):
            img.save(output_path, 'WEBP', quality=quality, method=6)
        else:
            # Convertir a RGB si no tiene canal alpha
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, 'WEBP', quality=quality, method=6)
        
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        new_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"[OK] Optimizado: {os.path.basename(input_path)}")
        print(f"  Tamaño original: {original_size:.2f} MB")
        print(f"  Tamaño nuevo: {new_size:.2f} MB")
        print(f"  Reducción: {reduction:.1f}%")
        return True
    except Exception as e:
        print(f"[ERROR] Error al optimizar {input_path}: {e}")
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base_dir, 'static', 'images')
    logo_dir = os.path.join(images_dir, 'logo')
    
    print("=" * 60)
    print("Conversión y optimización de imágenes")
    print("=" * 60)
    print()
    
    # 1. Convertir logo-gisa.jpeg a WebP
    logo_jpeg = os.path.join(logo_dir, 'logo-gisa.jpeg')
    logo_webp = os.path.join(logo_dir, 'logo-gisa.webp')
    
    if os.path.exists(logo_jpeg):
        print("1. Convirtiendo logo-gisa.jpeg a WebP...")
        convert_to_webp(logo_jpeg, logo_webp, quality=85)
        print()
    else:
        print(f"[AVISO] No se encontro: {logo_jpeg}")
        print()
    
    # 2. Optimizar FondoLogin.webp
    fondo_login = os.path.join(images_dir, 'FondoLogin.webp')
    fondo_login_optimized = os.path.join(images_dir, 'FondoLogin_optimized.webp')
    
    if os.path.exists(fondo_login):
        print("2. Optimizando FondoLogin.webp...")
        # Intentar con diferentes calidades para reducir el tamaño
        optimize_webp(fondo_login, fondo_login_optimized, quality=75)
        
        # Si la optimización fue exitosa, reemplazar el original
        if os.path.exists(fondo_login_optimized):
            original_size = os.path.getsize(fondo_login) / (1024 * 1024)
            optimized_size = os.path.getsize(fondo_login_optimized) / (1024 * 1024)
            
            if optimized_size < original_size:
                # Hacer backup del original
                backup_path = os.path.join(images_dir, 'FondoLogin_backup.webp')
                if not os.path.exists(backup_path):
                    import shutil
                    shutil.copy2(fondo_login, backup_path)
                    print(f"  Backup creado: FondoLogin_backup.webp")
                
                # Reemplazar el original
                os.replace(fondo_login_optimized, fondo_login)
                print(f"  [OK] Archivo original reemplazado con version optimizada")
            else:
                os.remove(fondo_login_optimized)
                print(f"  [AVISO] La optimizacion no redujo el tamano, se mantiene el original")
        print()
    else:
        print(f"[AVISO] No se encontro: {fondo_login}")
        print()
    
    print("=" * 60)
    print("!Proceso completado!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("Error: Se requiere la biblioteca Pillow (PIL)")
        print("Instálala con: pip install pillow")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario")
        sys.exit(1)


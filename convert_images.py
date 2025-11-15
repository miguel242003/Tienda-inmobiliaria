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

def optimize_webp(input_path, output_path, quality=70, max_width=None):
    """Optimiza una imagen WebP existente"""
    try:
        img = Image.open(input_path)
        original_width, original_height = img.size
        
        # Redimensionar si es muy grande (más de 1920px de ancho)
        if max_width and original_width > max_width:
            ratio = max_width / original_width
            new_height = int(original_height * ratio)
            # Compatibilidad con versiones antiguas de Pillow
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            img = img.resize((max_width, new_height), resample)
            print(f"  Redimensionado: {original_width}x{original_height} -> {max_width}x{new_height}")
        
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
    
    # 2. Optimizar imágenes grandes de fondo
    images_to_optimize = [
        ('FondoLogin.webp', 70, 1920),
        ('Fondodecontacto.webp', 70, 1920),
        ('fondo_consorcio.webp', 70, 1920),
    ]
    
    import shutil
    for image_name, quality, max_width in images_to_optimize:
        image_path = os.path.join(images_dir, image_name)
        image_optimized = os.path.join(images_dir, image_name.replace('.webp', '_optimized.webp'))
        
        if os.path.exists(image_path):
            print(f"Optimizando {image_name}...")
            optimize_webp(image_path, image_optimized, quality=quality, max_width=max_width)
            
            # Si la optimización fue exitosa, reemplazar el original
            if os.path.exists(image_optimized):
                original_size = os.path.getsize(image_path) / (1024 * 1024)
                optimized_size = os.path.getsize(image_optimized) / (1024 * 1024)
                
                if optimized_size < original_size:
                    # Hacer backup del original si no existe
                    backup_path = os.path.join(images_dir, image_name.replace('.webp', '_backup.webp'))
                    if not os.path.exists(backup_path):
                        shutil.copy2(image_path, backup_path)
                        print(f"  Backup creado: {os.path.basename(backup_path)}")
                    
                    # Reemplazar el original
                    os.replace(image_optimized, image_path)
                    print(f"  [OK] Archivo original reemplazado con version optimizada")
                else:
                    os.remove(image_optimized)
                    print(f"  [AVISO] La optimizacion no redujo el tamano, se mantiene el original")
            print()
        else:
            print(f"[AVISO] No se encontro: {image_name}")
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


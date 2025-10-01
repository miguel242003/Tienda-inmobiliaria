#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔒 SCRIPT DE BACKUP AUTOMÁTICO DE BASE DE DATOS
Crea backups de la base de datos MySQL con compresión y rotación automática.

Uso:
    python backup_database.py
    
Configuración en crontab (Linux) o Task Scheduler (Windows) para backups automáticos.
"""

import os
import subprocess
import datetime
from pathlib import Path
from decouple import config
import gzip
import shutil

# Configuración
BACKUP_DIR = Path(__file__).resolve().parent / 'backups' / 'database'
DB_NAME = config('DB_NAME', default='tienda_inmobiliaria_prod')
DB_USER = config('DB_USER', default='tienda_user')
DB_PASSWORD = config('DB_PASSWORD', default='')
DB_HOST = config('DB_HOST', default='localhost')
DB_PORT = config('DB_PORT', default='3306')

# Configuración de retención
KEEP_DAILY = 7      # Mantener backups diarios por 7 días
KEEP_WEEKLY = 4     # Mantener backups semanales por 4 semanas
KEEP_MONTHLY = 6    # Mantener backups mensuales por 6 meses

def crear_directorio_backup():
    """Crea el directorio de backups si no existe"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directorio de backups: {BACKUP_DIR}")

def generar_nombre_backup():
    """Genera nombre de archivo con timestamp"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{DB_NAME}_backup_{timestamp}.sql"

def crear_backup():
    """Crea un backup de la base de datos MySQL"""
    print("🔄 Iniciando backup de base de datos...")
    
    nombre_archivo = generar_nombre_backup()
    ruta_sql = BACKUP_DIR / nombre_archivo
    ruta_gz = BACKUP_DIR / f"{nombre_archivo}.gz"
    
    try:
        # Comando mysqldump
        cmd = [
            'mysqldump',
            f'--host={DB_HOST}',
            f'--port={DB_PORT}',
            f'--user={DB_USER}',
            f'--password={DB_PASSWORD}',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--events',
            DB_NAME
        ]
        
        # Ejecutar mysqldump y guardar
        with open(ruta_sql, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
        if result.returncode != 0:
            print(f"❌ Error en mysqldump: {result.stderr}")
            return False
        
        print(f"✅ Backup SQL creado: {ruta_sql}")
        
        # Comprimir backup
        print("🔄 Comprimiendo backup...")
        with open(ruta_sql, 'rb') as f_in:
            with gzip.open(ruta_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Eliminar archivo SQL sin comprimir
        ruta_sql.unlink()
        
        # Tamaño del archivo
        tamaño_mb = ruta_gz.stat().st_size / (1024 * 1024)
        print(f"✅ Backup comprimido: {ruta_gz}")
        print(f"📦 Tamaño: {tamaño_mb:.2f} MB")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: mysqldump no encontrado. Asegúrate de que MySQL esté instalado.")
        print("   En Windows: Agrega MySQL\\bin a las variables de entorno PATH")
        return False
    except Exception as e:
        print(f"❌ Error al crear backup: {str(e)}")
        return False

def limpiar_backups_antiguos():
    """Elimina backups antiguos según política de retención"""
    print("\n🔄 Limpiando backups antiguos...")
    
    ahora = datetime.datetime.now()
    archivos_backup = sorted(BACKUP_DIR.glob('*.sql.gz'))
    
    eliminados = 0
    for archivo in archivos_backup:
        # Obtener fecha del archivo
        fecha_archivo = datetime.datetime.fromtimestamp(archivo.stat().st_mtime)
        dias_antiguedad = (ahora - fecha_archivo).days
        
        # Determinar si debe eliminarse
        debe_eliminar = False
        
        if dias_antiguedad > KEEP_DAILY * 30:  # Más de 6 meses (KEEP_MONTHLY)
            debe_eliminar = True
        elif dias_antiguedad > KEEP_DAILY * 7:  # Más de 1 mes (KEEP_WEEKLY)
            # Mantener solo backups semanales
            if fecha_archivo.weekday() != 0:  # No es lunes
                debe_eliminar = True
        elif dias_antiguedad > KEEP_DAILY:  # Más de 7 días
            # Mantener solo backups diarios
            debe_eliminar = True
        
        if debe_eliminar:
            archivo.unlink()
            eliminados += 1
            print(f"  🗑️  Eliminado: {archivo.name} (antigüedad: {dias_antiguedad} días)")
    
    if eliminados == 0:
        print("  ✅ No hay backups para eliminar")
    else:
        print(f"  ✅ {eliminados} backup(s) eliminado(s)")

def listar_backups():
    """Lista todos los backups disponibles"""
    print("\n📋 Backups disponibles:")
    archivos_backup = sorted(BACKUP_DIR.glob('*.sql.gz'), reverse=True)
    
    if not archivos_backup:
        print("  ⚠️  No hay backups disponibles")
        return
    
    total_tamaño = 0
    for archivo in archivos_backup:
        fecha = datetime.datetime.fromtimestamp(archivo.stat().st_mtime)
        tamaño_mb = archivo.stat().st_size / (1024 * 1024)
        total_tamaño += tamaño_mb
        print(f"  📦 {archivo.name}")
        print(f"     Fecha: {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"     Tamaño: {tamaño_mb:.2f} MB")
    
    print(f"\n  📊 Total: {len(archivos_backup)} backup(s) - {total_tamaño:.2f} MB")

def restaurar_backup(archivo_backup):
    """
    Restaura un backup específico
    
    Args:
        archivo_backup: Ruta al archivo .sql.gz
    """
    print(f"\n🔄 Restaurando backup: {archivo_backup}")
    
    # Confirmar
    respuesta = input("⚠️  ADVERTENCIA: Esto sobrescribirá la base de datos actual. ¿Continuar? (si/no): ")
    if respuesta.lower() not in ['si', 's', 'yes', 'y']:
        print("❌ Restauración cancelada")
        return False
    
    try:
        # Descomprimir
        archivo_sql = archivo_backup.replace('.gz', '')
        print("🔄 Descomprimiendo backup...")
        with gzip.open(archivo_backup, 'rb') as f_in:
            with open(archivo_sql, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Restaurar
        print("🔄 Restaurando base de datos...")
        cmd = [
            'mysql',
            f'--host={DB_HOST}',
            f'--port={DB_PORT}',
            f'--user={DB_USER}',
            f'--password={DB_PASSWORD}',
            DB_NAME
        ]
        
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
        
        # Eliminar archivo SQL temporal
        os.unlink(archivo_sql)
        
        if result.returncode != 0:
            print(f"❌ Error al restaurar: {result.stderr}")
            return False
        
        print("✅ Base de datos restaurada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al restaurar backup: {str(e)}")
        return False

def main():
    """Función principal"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║     🔒 BACKUP AUTOMÁTICO DE BASE DE DATOS - MySQL          ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Crear directorio
    crear_directorio_backup()
    
    # Crear backup
    if crear_backup():
        # Limpiar backups antiguos
        limpiar_backups_antiguos()
        
        # Listar backups
        listar_backups()
        
        print("\n✅ ¡Backup completado exitosamente!")
        return 0
    else:
        print("\n❌ Error al crear backup")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())


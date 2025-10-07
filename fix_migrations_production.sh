#!/bin/bash

# Script para solucionar problemas de migraciones en producción
# Ejecutar en el servidor de producción

echo "🔧 SOLUCIONANDO PROBLEMAS DE MIGRACIONES EN PRODUCCIÓN"
echo "=================================================="

# Paso 1: Verificar estado actual
echo "📊 Verificando estado de migraciones..."
python manage.py showmigrations propiedades

# Paso 2: Eliminar migraciones problemáticas si existen
echo "🗑️ Eliminando migraciones problemáticas..."
rm -f propiedades/migrations/0019_auto_20251007_0057.py
rm -f propiedades/migrations/0020_propiedad_ambientes_propiedad_balcon.py

# Paso 3: Crear nueva migración limpia
echo "🆕 Creando nueva migración..."
python manage.py makemigrations propiedades

# Paso 4: Aplicar migraciones
echo "📦 Aplicando migraciones..."
python manage.py migrate

# Paso 5: Crear amenidad Estacionamiento
echo "🚗 Creando amenidad Estacionamiento..."
python manage.py crear_amenidades

# Paso 6: Verificar que todo esté bien
echo "✅ Verificando sistema..."
python manage.py check

echo "🎉 ¡Problema de migraciones solucionado!"
echo "El sistema está listo para funcionar con los nuevos campos."

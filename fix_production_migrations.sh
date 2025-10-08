#!/bin/bash

# Script para corregir migraciones en producción
echo "🔧 Corrigiendo migraciones en producción..."

# 1. Verificar estado actual de migraciones
echo "📊 Verificando estado de migraciones..."
python manage.py showmigrations propiedades

# 2. Si hay conflictos, aplicar migraciones una por una
echo "🔄 Aplicando migraciones de forma segura..."

# Aplicar migraciones hasta la 0018
python manage.py migrate propiedades 0018

# Aplicar migración 0019 si existe
python manage.py migrate propiedades 0019 --fake-if-no-migration

# Aplicar migración 0021 (WebP)
python manage.py migrate propiedades 0021 --fake-if-no-migration

# Aplicar merge si es necesario
python manage.py migrate propiedades 0022 --fake-if-no-migration

# 3. Aplicar todas las migraciones restantes
echo "✅ Aplicando migraciones restantes..."
python manage.py migrate

echo "🎉 Migraciones corregidas exitosamente!"

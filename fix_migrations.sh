#!/bin/bash

# Script para resolver conflictos de migraciones
echo "🔧 Resolviendo conflictos de migraciones..."

# Navegar al directorio del proyecto
cd /home/deploy/Tienda-inmobiliaria

# Activar entorno virtual
source venv/bin/activate

# Verificar estado actual de migraciones
echo "📊 Estado actual de migraciones:"
python manage.py showmigrations propiedades

# Intentar merge de migraciones
echo "🔄 Ejecutando merge de migraciones..."
python manage.py makemigrations --merge

# Si el merge no funciona, vamos a resolver manualmente
if [ $? -ne 0 ]; then
    echo "⚠️  Merge automático falló. Resolviendo manualmente..."
    
    # Crear una migración de merge manual
    python manage.py makemigrations propiedades --empty --name merge_conflicts
    
    # Aplicar migraciones
    echo "📥 Aplicando migraciones..."
    python manage.py migrate --fake-initial
fi

# Verificar que todo esté bien
echo "✅ Verificando estado final:"
python manage.py check
python manage.py showmigrations propiedades

echo "🎉 ¡Migraciones resueltas!"

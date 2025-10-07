#!/bin/bash

echo "🔧 Resolviendo conflictos de migraciones en el servidor..."

# Navegar al directorio del proyecto
cd /home/deploy/Tienda-inmobiliaria

# Activar entorno virtual
source venv/bin/activate

echo "📊 Estado actual de migraciones:"
python manage.py showmigrations propiedades

echo "🔄 Eliminando migraciones conflictivas..."

# Hacer backup de las migraciones actuales
cp -r propiedades/migrations propiedades/migrations_backup

# Eliminar las migraciones problemáticas
rm propiedades/migrations/0017_propiedad_slug_alter_propiedad_precio.py
rm propiedades/migrations/0018_auto_20251007_0057.py  
rm propiedades/migrations/0019_auto_20251007_0057.py

echo "📝 Creando nueva migración limpia..."

# Crear una nueva migración que incluya el campo slug
python manage.py makemigrations propiedades --name add_slug_field

echo "📥 Aplicando migraciones..."
python manage.py migrate

echo "✅ Verificando estado final:"
python manage.py check

echo "🎉 ¡Conflictos de migraciones resueltos!"

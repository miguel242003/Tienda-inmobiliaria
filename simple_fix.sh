#!/bin/bash

echo "🔧 Solución simple para conflictos de migraciones"

cd /home/deploy/Tienda-inmobiliaria
source venv/bin/activate

# Paso 1: Hacer fake de las migraciones problemáticas
echo "📝 Marcando migraciones como aplicadas..."
python manage.py migrate propiedades 0016 --fake
python manage.py migrate propiedades 0017 --fake
python manage.py migrate propiedades 0018 --fake  
python manage.py migrate propiedades 0019 --fake

# Paso 2: Aplicar todas las migraciones
echo "📥 Aplicando todas las migraciones..."
python manage.py migrate

# Paso 3: Verificar que todo esté bien
echo "✅ Verificando estado:"
python manage.py check

echo "🎉 ¡Listo! El servidor debería funcionar ahora."

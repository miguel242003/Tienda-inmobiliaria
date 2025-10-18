# Solución Error 500 en Dashboard

## Problema Identificado

El error 500 en la ruta `/dashboard/` se debía a dos problemas principales:

### 1. Error de Tipo en Procesamiento de Clics
**Error:** `TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'`

**Ubicación:** `login/views.py` línea 412

**Causa:** El campo `fecha_click__month` podía ser `None` y se intentaba hacer una operación matemática.

**Solución:** Agregar validación para verificar que el valor no sea `None`:

```python
# Antes (causaba error)
mes = click_data['fecha_click__month'] - 1

# Después (corregido)
mes_raw = click_data['fecha_click__month']
if mes_raw is not None:
    mes = mes_raw - 1
```

### 2. Error de Archivo No Encontrado en CVs
**Error:** `FileNotFoundError: [WinError 2] El sistema no puede encontrar el archivo especificado`

**Ubicación:** `core/models.py` método `get_file_size()`

**Causa:** El método intentaba acceder al tamaño de archivos CV que no existían físicamente.

**Solución:** Agregar manejo de excepciones:

```python
def get_file_size(self):
    """Retorna el tamaño del archivo en formato legible"""
    if self.cv_file:
        try:
            size = self.cv_file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        except (FileNotFoundError, OSError):
            return "Archivo no encontrado"
    return "N/A"
```

## Archivos Modificados

1. **`login/views.py`** - Línea 412: Agregada validación para `fecha_click__month`
2. **`core/models.py`** - Método `get_file_size()`: Agregado manejo de excepciones

## Resultado

✅ **El dashboard ahora funciona correctamente**
- Status Code: 200
- Sin errores de tipo
- Manejo robusto de archivos faltantes
- Dashboard completamente funcional

## Comandos para Probar

```bash
# En el VPS (con entorno virtual activado)
DEBUG=True python3 manage.py runserver 0.0.0.0:8000
```

Luego acceder a: `http://tu-ip-vps:8000/login/dashboard/`

## Notas Importantes

- Los errores se solucionaron manteniendo la funcionalidad completa del dashboard
- Se agregó manejo robusto de errores para casos edge
- La solución es compatible con el entorno de producción

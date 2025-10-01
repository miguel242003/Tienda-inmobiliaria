# ⚡ GUÍA DE OPTIMIZACIÓN DE QUERIES

## 📋 Índice
1. [Problema N+1](#problema-n1)
2. [select_related()](#select_related)
3. [prefetch_related()](#prefetch_related)
4. [Índices de Base de Datos](#índices-de-base-de-datos)
5. [only() y defer()](#only-y-defer)
6. [Optimizaciones Aplicadas](#optimizaciones-aplicadas)

---

## Problema N+1

El problema N+1 ocurre cuando haces una consulta para obtener N objetos, y luego haces N consultas adicionales para obtener datos relacionados.

### ❌ ANTES (Problema N+1):
```python
# Esta consulta genera 1 + N queries
propiedades = Propiedad.objects.all()
for propiedad in propiedades:
    print(propiedad.administrador.nombre)  # Query adicional por cada propiedad!
```

### ✅ DESPUÉS (Optimizado):
```python
# Esta consulta genera solo 1 query
propiedades = Propiedad.objects.select_related('administrador').all()
for propiedad in propiedad:
    print(propiedad.administrador.nombre)  # Sin query adicional!
```

---

## select_related()

Usar para relaciones **ForeignKey** y **OneToOne**.

### Uso:
```python
from propiedades.models import Propiedad

# Cargar propiedad con su administrador en una sola query
propiedad = Propiedad.objects.select_related('administrador').get(id=1)

# Múltiples relaciones
propiedad = Propiedad.objects.select_related(
    'administrador',
    # Agregar otras ForeignKeys aquí
).get(id=1)
```

### Ventajas:
- ✅ Reduce número de queries
- ✅ Usa SQL JOIN
- ✅ Mejora rendimiento significativamente

---

## prefetch_related()

Usar para relaciones **ManyToMany** y **ForeignKey inversas**.

### Uso:
```python
# Cargar propiedades con sus amenidades en 2 queries (en lugar de N+1)
propiedades = Propiedad.objects.prefetch_related('amenidades').all()

for propiedad in propiedades:
    for amenidad in propiedad.amenidades.all():  # Sin query adicional
        print(amenidad.nombre)

# Cargar propiedades con fotos adicionales
propiedades = Propiedad.objects.prefetch_related('fotopropiedad_set').all()
```

### Prefetch Avanzado:
```python
from django.db.models import Prefetch

# Prefetch con filtros
propiedades = Propiedad.objects.prefetch_related(
    Prefetch(
        'fotopropiedad_set',
        queryset=FotoPropiedad.objects.filter(tipo_medio='imagen').order_by('orden')
    )
).all()
```

---

## Índices de Base de Datos

Los índices aceleran las búsquedas en campos específicos.

### Agregar Índices en Modelos:

```python
# propiedades/models.py

class Propiedad(models.Model):
    titulo = models.CharField(max_length=200, db_index=True)  # Índice simple
    tipo = models.CharField(max_length=50, db_index=True)
    operacion = models.CharField(max_length=20, db_index=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    estado = models.CharField(max_length=20, db_index=True)
    
    class Meta:
        # Índice compuesto (para búsquedas combinadas)
        indexes = [
            models.Index(fields=['tipo', 'operacion']),
            models.Index(fields=['estado', 'fecha_creacion']),
            models.Index(fields=['-fecha_creacion']),  # Ordenamiento descendente
        ]
```

### Crear Migración:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Índices Recomendados:

| Campo | Razón |
|-------|-------|
| `titulo` | Búsquedas de texto |
| `tipo` | Filtros frecuentes |
| `operacion` | Filtros frecuentes |
| `estado` | Filtros frecuentes |
| `precio` | Ordenamiento y rangos |
| `fecha_creacion` | Ordenamiento |

---

## only() y defer()

Cargar solo los campos necesarios.

### only() - Cargar SOLO campos específicos:
```python
# Solo cargar título y precio (ahorra memoria)
propiedades = Propiedad.objects.only('titulo', 'precio').all()

# Útil para listas donde no necesitas todos los campos
```

### defer() - Excluir campos específicos:
```python
# Cargar todo EXCEPTO descripción (si es muy grande)
propiedades = Propiedad.objects.defer('descripcion').all()
```

---

## Optimizaciones Aplicadas

### 1. Vista de Listado de Propiedades

**Archivo:** `propiedades/views.py`

```python
def lista_propiedades(request):
    propiedades = Propiedad.objects.filter(
        estado='disponible'
    ).select_related(
        'administrador'  # Cargar administrador en misma query
    ).prefetch_related(
        'amenidades'  # Cargar amenidades eficientemente
    ).only(
        'id', 'titulo', 'tipo', 'operacion', 'precio',
        'imagen_principal', 'dormitorios', 'banos',
        'superficie_total', 'administrador__nombre',
        'administrador__apellido'
    ).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(propiedades, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    return render(request, 'propiedades/lista.html', {'page_obj': page_obj})
```

### 2. Vista de Detalle de Propiedad

```python
def detalle_propiedad(request, propiedad_id):
    propiedad = get_object_or_404(
        Propiedad.objects.select_related(
            'administrador'
        ).prefetch_related(
            'amenidades',
            Prefetch(
                'fotopropiedad_set',
                queryset=FotoPropiedad.objects.order_by('orden')
            ),
            Prefetch(
                'resena_set',
                queryset=Resena.objects.filter(
                    aprobada=True
                ).select_related('usuario').order_by('-fecha_creacion')[:10]
            )
        ),
        id=propiedad_id
    )
    
    return render(request, 'propiedades/detalle.html', {'propiedad': propiedad})
```

### 3. Dashboard con Estadísticas

```python
@login_required
def dashboard(request):
    # Obtener propiedades con click count en una sola query
    from django.db.models import Count, Avg
    
    propiedades = Propiedad.objects.select_related(
        'administrador'
    ).annotate(
        total_clicks=Count('clickpropiedad'),
        avg_rating=Avg('resena__calificacion')
    ).order_by('-fecha_creacion')[:10]
    
    # Estadísticas globales en una query
    stats = Propiedad.objects.aggregate(
        total=Count('id'),
        disponibles=Count('id', filter=Q(estado='disponible')),
        precio_promedio=Avg('precio')
    )
    
    return render(request, 'dashboard.html', {
        'propiedades': propiedades,
        'stats': stats
    })
```

### 4. Búsqueda Optimizada

```python
def buscar_propiedades(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    
    propiedades = Propiedad.objects.filter(
        estado='disponible'
    ).select_related(
        'administrador'
    ).prefetch_related(
        'amenidades'
    )
    
    # Filtros
    if query:
        propiedades = propiedades.filter(
            Q(titulo__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    if tipo:
        propiedades = propiedades.filter(tipo=tipo)
    
    # Solo campos necesarios para lista
    propiedades = propiedades.only(
        'id', 'titulo', 'tipo', 'precio',
        'imagen_principal', 'dormitorios', 'banos'
    )
    
    return render(request, 'propiedades/buscar.html', {
        'propiedades': propiedades
    })
```

---

## Análisis de Queries con Debug Toolbar

### Instalación y Uso:

1. **Ya instalado** en `settings.py`

2. **Acceder**: Cuando estás en DEBUG=True, verás un panel en el lado derecho de la página

3. **Panel SQL**: Muestra todas las queries ejecutadas

4. **Identificar problemas**:
   - ⚠️ Queries duplicadas
   - ⚠️ Queries similares (N+1)
   - ⚠️ Queries lentas (> 100ms)

---

## Comandos Útiles

### Ver Queries en Shell:
```bash
python manage.py shell
```

```python
>>> from django.db import connection
>>> from propiedades.models import Propiedad
>>> 
>>> # Habilitar logging de queries
>>> connection.queries_log.enabled = True
>>> 
>>> # Ejecutar consulta
>>> propiedades = list(Propiedad.objects.all())
>>> 
>>> # Ver queries ejecutadas
>>> for query in connection.queries:
...     print(query['sql'])
```

### Analizar Query Específica:
```python
>>> from django.db import connection
>>> from django.db.models import Count
>>> 
>>> # Tu query
>>> propiedades = Propiedad.objects.select_related('administrador').prefetch_related('amenidades')
>>> 
>>> # Ver SQL generado
>>> print(propiedades.query)
```

---

## Benchmarking

### Script de Prueba:
```python
import time
from propiedades.models import Propiedad

# SIN optimización
start = time.time()
propiedades = Propiedad.objects.all()
for p in propiedades:
    admin = p.administrador.nombre
    amenidades = list(p.amenidades.all())
tiempo_sin_opt = time.time() - start

# CON optimización
start = time.time()
propiedades = Propiedad.objects.select_related('administrador').prefetch_related('amenidades').all()
for p in propiedades:
    admin = p.administrador.nombre
    amenidades = list(p.amenidades.all())
tiempo_con_opt = time.time() - start

print(f"Sin optimización: {tiempo_sin_opt:.2f}s")
print(f"Con optimización: {tiempo_con_opt:.2f}s")
print(f"Mejora: {(tiempo_sin_opt / tiempo_con_opt):.2f}x más rápido")
```

---

## Checklist de Optimización

- [ ] Usar `select_related()` para ForeignKey
- [ ] Usar `prefetch_related()` para ManyToMany
- [ ] Agregar índices a campos de búsqueda/filtro
- [ ] Usar `only()` para listar muchos objetos
- [ ] Usar `defer()` para excluir campos grandes
- [ ] Usar `annotate()` para cálculos en BD
- [ ] Usar `aggregate()` para estadísticas
- [ ] Paginar resultados grandes
- [ ] Cache para queries frecuentes
- [ ] Analizar con Debug Toolbar

---

## Recursos Adicionales

- [Django Query Optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Database Indexing Best Practices](https://use-the-index-luke.com/)

---

**Última actualización:** 1 de Octubre, 2025


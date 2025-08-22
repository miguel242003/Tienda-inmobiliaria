# Carrusel de Imágenes - Instrucciones

## Imágenes Requeridas

Guarda las siguientes imágenes en esta carpeta:

1. **interior-1.jpg** - Primera imagen del carrusel (sala moderna con ventanales)
2. **interior-2.jpg** - Segunda imagen del carrusel (sala contemporánea con alfombra roja)

## Especificaciones Técnicas

- **Formato:** JPG, JPEG o PNG
- **Resolución recomendada:** 1920x1080 o similar (ratio 16:9)
- **Tamaño máximo:** 2MB por imagen
- **Optimización:** Las imágenes se ajustarán automáticamente usando `object-fit: cover`

## Funcionamiento del Carrusel

- ✅ **Altura fija:** 500px en desktop, 400px en tablet, 350px en móvil
- ✅ **Rotación automática:** Cada 4 segundos
- ✅ **Efecto fade:** Transición suave entre imágenes
- ✅ **Indicadores:** Puntos clickeables en la parte inferior
- ✅ **Pausa en hover:** Se detiene al pasar el mouse
- ✅ **Controles de teclado:** Flechas izquierda/derecha
- ✅ **Responsive:** Se adapta a todos los dispositivos

## Reemplazar Imágenes

Para cambiar las imágenes del carrusel:

1. Reemplaza los archivos `interior-1.jpg` e `interior-2.jpg`
2. O edita `core/templates/core/home.html` y cambia las rutas:
   ```html
   <img src="{% static 'images/carousel/nueva-imagen-1.jpg' %}" alt="...">
   <img src="{% static 'images/carousel/nueva-imagen-2.jpg' %}" alt="...">
   ```
3. Ejecuta `python manage.py collectstatic --noinput` para actualizar

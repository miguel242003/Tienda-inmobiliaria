# Conversión de Imágenes a WebP

Este documento explica cómo convertir las imágenes a formato WebP para mejorar el rendimiento del sitio.

## Imágenes que necesitan conversión

1. **logo-gisa.jpeg** → `logo-gisa.webp`
2. **FondoLogin.webp** → Optimizar (reducir de 2.9 MB)

## Método 1: Usando el script Python (Recomendado)

### Requisitos
- Python 3.6 o superior
- Biblioteca Pillow (PIL)

### Instalación de Pillow
```bash
pip install pillow
```

### Ejecutar el script
```bash
python convert_images.py
```

El script:
- Convertirá `logo-gisa.jpeg` a `logo-gisa.webp`
- Optimizará `FondoLogin.webp` reduciendo su tamaño
- Creará un backup de `FondoLogin.webp` antes de optimizarlo

## Método 2: Usando herramientas online

### Para convertir logo-gisa.jpeg:
1. Visita https://convertio.co/jpeg-webp/ o https://cloudconvert.com/jpeg-to-webp
2. Sube `static/images/logo/logo-gisa.jpeg`
3. Descarga el archivo convertido como `logo-gisa.webp`
4. Colócalo en `static/images/logo/`

### Para optimizar FondoLogin.webp:
1. Visita https://squoosh.app/ o https://imagemagick.org/script/download.php
2. Sube `static/images/FondoLogin.webp`
3. Ajusta la calidad a 75-80%
4. Descarga y reemplaza el archivo original

## Método 3: Usando ImageMagick (Windows)

### Instalación
1. Descarga ImageMagick desde: https://imagemagick.org/script/download.php
2. Instala el programa

### Comandos
```powershell
# Convertir logo
magick static\images\logo\logo-gisa.jpeg -quality 85 static\images\logo\logo-gisa.webp

# Optimizar FondoLogin
magick static\images\FondoLogin.webp -quality 75 static\images\FondoLogin_optimized.webp
```

## Notas

- Las referencias en el código ya han sido actualizadas para usar las versiones WebP
- Los favicons pueden mantenerse en JPEG (WebP no es ideal para favicons)
- Después de convertir, verifica que las imágenes se vean correctamente en el navegador


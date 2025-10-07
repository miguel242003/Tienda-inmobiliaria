# 🔧 Solución al Error 413: Payload Too Large

## ❌ Problema Identificado
El error `413 Failed to load resource: the server responded with a status of 413` indica que **Nginx está rechazando archivos grandes** antes de que lleguen a Django.

## ✅ Solución Completa

### 1. **Configuración de Django (Ya aplicada)**
- ✅ Límites en formularios: 20MB para imágenes
- ✅ Límites en validadores: 20MB/200MB
- ✅ Límites en vistas: 20MB/200MB
- ✅ JavaScript actualizado: 20MB/200MB
- ✅ Configuración de Django settings agregada

### 2. **Configuración de Nginx (Pendiente)**

#### Opción A: Usar el script automático
```bash
# Ejecutar como root
sudo bash actualizar_nginx_archivos_grandes.sh
```

#### Opción B: Configuración manual

1. **Editar configuración de Nginx:**
```bash
sudo nano /etc/nginx/sites-available/tienda_inmobiliaria
```

2. **Agregar estas líneas en el bloque `server` (después de `server_name`):**
```nginx
# 🔥 CONFIGURACIÓN PARA ARCHIVOS GRANDES
# Permitir archivos hasta 200MB (para videos)
client_max_body_size 200M;

# Timeout para subidas grandes
client_body_timeout 300s;
client_header_timeout 300s;

# Buffer para archivos grandes
client_body_buffer_size 128k;
client_header_buffer_size 1k;
large_client_header_buffers 4 4k;
```

3. **En el bloque `location /` (proxy a Gunicorn), agregar:**
```nginx
# 🔥 CONFIGURACIÓN PARA ARCHIVOS GRANDES
# Timeouts extendidos para subidas grandes
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;

# Buffer para archivos grandes
proxy_request_buffering off;
proxy_buffering off;
```

4. **Verificar y recargar:**
```bash
# Verificar configuración
sudo nginx -t

# Si es válida, recargar
sudo systemctl reload nginx
```

### 3. **Verificación**

#### Probar subida de archivo grande:
1. Ir a `/propiedades/crear/`
2. Intentar subir tu imagen de 16.345 KB
3. Debería funcionar sin error 413

#### Verificar logs si hay problemas:
```bash
# Logs de Nginx
sudo tail -f /var/log/nginx/tienda_inmobiliaria_error.log

# Logs de Gunicorn
sudo tail -f /home/usuario/Tienda-inmobiliaria/logs/gunicorn.log
```

## 📋 Configuración Final

### Límites del Sistema:
- 🖼️ **Imágenes principales/secundarias**: 20MB máximo
- 🎥 **Videos adicionales**: 200MB máximo
- 📄 **Documentos (CV)**: 10MB máximo

### Configuración de Nginx:
- `client_max_body_size`: 200M
- `client_body_timeout`: 300s
- `proxy_connect_timeout`: 300s
- `proxy_send_timeout`: 300s
- `proxy_read_timeout`: 300s

### Configuración de Django:
- `DATA_UPLOAD_MAX_MEMORY_SIZE`: 20MB
- `FILE_UPLOAD_MAX_MEMORY_SIZE`: 20MB

## 🎉 Resultado Esperado

Después de aplicar estos cambios:
- ✅ Tu imagen de 16.345 KB se podrá subir sin problemas
- ✅ Videos hasta 200MB se podrán subir en archivos adicionales
- ✅ No más errores 413
- ✅ Sistema completamente funcional

## 🔄 Si Necesitas Revertir

```bash
# Restaurar configuración anterior
sudo cp /etc/nginx/sites-available/tienda_inmobiliaria.backup.* /etc/nginx/sites-available/tienda_inmobiliaria
sudo systemctl reload nginx
```

#!/bin/bash

# ========================================
# SCRIPT DE APLICACIÓN DE SOLUCIÓN LOGIN
# ========================================
# Este script aplica automáticamente la solución al problema de login
# 
# USO:
#   chmod +x aplicar_solucion_login.sh
#   ./aplicar_solucion_login.sh

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Función para imprimir encabezados
print_header() {
    echo -e "\n${BOLD}${BLUE}========================================${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}========================================${NC}\n"
}

# Función para imprimir éxito
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para imprimir error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para imprimir advertencia
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para imprimir información
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║          APLICAR SOLUCIÓN AL PROBLEMA DE LOGIN                    ║"
echo "║          Tienda Inmobiliaria - gisa-nqn.com                       ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Verificar que se está ejecutando desde el directorio correcto
if [ ! -f "manage.py" ]; then
    print_error "Este script debe ejecutarse desde el directorio raíz del proyecto"
    print_info "Cambia al directorio correcto: cd /ruta/a/Tienda-inmobiliaria"
    exit 1
fi

print_success "Directorio correcto detectado"

# ========================================
# 1. ACTUALIZAR CÓDIGO DESDE REPOSITORIO
# ========================================
print_header "1. ACTUALIZAR CÓDIGO DESDE GIT"

if [ -d ".git" ]; then
    print_info "Guardando cambios locales (si existen)..."
    git stash
    
    print_info "Actualizando desde repositorio remoto..."
    if git pull origin main; then
        print_success "Código actualizado correctamente"
    else
        print_error "Error al actualizar desde Git"
        print_warning "Continúa manualmente: git pull origin main"
    fi
else
    print_warning "No se detectó repositorio Git"
    print_info "Si descargaste el código manualmente, asegúrate de tener la última versión"
fi

# ========================================
# 2. VERIFICAR ENTORNO VIRTUAL
# ========================================
print_header "2. VERIFICAR ENTORNO VIRTUAL"

if [ -d "venv" ] || [ -d "env" ] || [ -d ".venv" ]; then
    print_success "Entorno virtual encontrado"
    
    # Activar entorno virtual
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_info "Entorno virtual activado: venv"
    elif [ -f "env/bin/activate" ]; then
        source env/bin/activate
        print_info "Entorno virtual activado: env"
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        print_info "Entorno virtual activado: .venv"
    fi
else
    print_warning "No se encontró entorno virtual"
    print_info "Continuando sin entorno virtual (no recomendado)"
fi

# ========================================
# 3. VERIFICAR ARCHIVO .env
# ========================================
print_header "3. VERIFICAR CONFIGURACIÓN .env"

if [ ! -f ".env" ]; then
    print_error "Archivo .env no encontrado"
    print_info "Creando .env desde .env.production.example..."
    
    if [ -f ".env.production.example" ]; then
        cp .env.production.example .env
        print_warning "Archivo .env creado. DEBES editarlo con tus credenciales:"
        print_info "  - Genera SECRET_KEY nueva"
        print_info "  - Configura credenciales de base de datos"
        print_info "  - Configura credenciales de email"
        print_info "\nEdita el archivo: nano .env"
        
        read -p "Presiona ENTER después de editar .env..."
    else
        print_error "No se encontró .env.production.example"
        exit 1
    fi
else
    print_success "Archivo .env encontrado"
fi

# Verificar variables críticas en .env
print_info "Verificando variables críticas en .env..."

if ! grep -q "^SECRET_KEY=" .env || grep -q "^SECRET_KEY=$" .env; then
    print_error "SECRET_KEY no configurada en .env"
    exit 1
else
    print_success "SECRET_KEY configurada"
fi

if ! grep -q "^DEBUG=" .env; then
    print_warning "DEBUG no definida en .env (se usará el valor por defecto)"
else
    DEBUG_VALUE=$(grep "^DEBUG=" .env | cut -d '=' -f2)
    if [ "$DEBUG_VALUE" = "False" ] || [ "$DEBUG_VALUE" = "false" ]; then
        print_success "DEBUG=False (correcto para producción)"
    else
        print_warning "DEBUG=True (NO recomendado para producción)"
    fi
fi

if ! grep -q "gisa-nqn.com" .env; then
    print_warning "Dominio gisa-nqn.com no está en ALLOWED_HOSTS en .env"
    print_info "Asegúrate de que .env tenga:"
    print_info "ALLOWED_HOSTS=gisa-nqn.com,www.gisa-nqn.com,localhost,127.0.0.1"
else
    print_success "Dominio gisa-nqn.com configurado en ALLOWED_HOSTS"
fi

# ========================================
# 4. INSTALAR/ACTUALIZAR DEPENDENCIAS
# ========================================
print_header "4. INSTALAR/ACTUALIZAR DEPENDENCIAS"

if command -v pip &> /dev/null; then
    print_info "Actualizando pip..."
    pip install --upgrade pip
    
    print_info "Instalando/actualizando dependencias..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencias instaladas"
    else
        print_warning "No se encontró requirements.txt"
    fi
else
    print_error "pip no está instalado"
    exit 1
fi

# ========================================
# 5. EJECUTAR MIGRACIONES
# ========================================
print_header "5. EJECUTAR MIGRACIONES DE BASE DE DATOS"

print_info "Verificando migraciones pendientes..."
python manage.py showmigrations --plan

print_info "Ejecutando migraciones..."
if python manage.py migrate; then
    print_success "Migraciones ejecutadas correctamente"
    print_info "Tabla de sesiones (django_session) creada/actualizada"
else
    print_error "Error al ejecutar migraciones"
    print_info "Verifica la configuración de base de datos en .env"
    exit 1
fi

# ========================================
# 6. LIMPIAR SESIONES ANTIGUAS
# ========================================
print_header "6. LIMPIAR SESIONES EXPIRADAS"

print_info "Eliminando sesiones expiradas..."
if python manage.py clearsessions; then
    print_success "Sesiones expiradas eliminadas"
else
    print_warning "Error al limpiar sesiones (no crítico)"
fi

# ========================================
# 7. RECOPILAR ARCHIVOS ESTÁTICOS
# ========================================
print_header "7. RECOPILAR ARCHIVOS ESTÁTICOS"

print_info "Recopilando archivos estáticos..."
if python manage.py collectstatic --noinput; then
    print_success "Archivos estáticos recopilados"
else
    print_warning "Error al recopilar archivos estáticos"
fi

# ========================================
# 8. EJECUTAR DIAGNÓSTICO
# ========================================
print_header "8. EJECUTAR DIAGNÓSTICO DE SESIONES"

if [ -f "diagnostico_sesiones.py" ]; then
    print_info "Ejecutando script de diagnóstico..."
    python diagnostico_sesiones.py
else
    print_warning "Script de diagnóstico no encontrado"
fi

# ========================================
# 9. REINICIAR SERVICIOS
# ========================================
print_header "9. REINICIAR SERVICIOS DEL SERVIDOR"

print_info "Detectando servicio web..."

# Detectar qué servicio se está usando
if systemctl is-active --quiet gunicorn; then
    print_info "Servicio Gunicorn detectado"
    
    read -p "¿Reiniciar Gunicorn? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        if sudo systemctl restart gunicorn; then
            print_success "Gunicorn reiniciado"
        else
            print_error "Error al reiniciar Gunicorn"
            print_info "Reinicia manualmente: sudo systemctl restart gunicorn"
        fi
    fi
elif systemctl is-active --quiet uwsgi; then
    print_info "Servicio uWSGI detectado"
    
    read -p "¿Reiniciar uWSGI? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        if sudo systemctl restart uwsgi; then
            print_success "uWSGI reiniciado"
        else
            print_error "Error al reiniciar uWSGI"
            print_info "Reinicia manualmente: sudo systemctl restart uwsgi"
        fi
    fi
else
    print_warning "No se detectó servicio Gunicorn o uWSGI"
    print_info "Reinicia tu servidor web manualmente"
fi

# Nginx
if systemctl is-active --quiet nginx; then
    print_info "Servicio Nginx detectado"
    
    read -p "¿Reiniciar Nginx? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        # Primero verificar configuración
        if sudo nginx -t; then
            if sudo systemctl reload nginx; then
                print_success "Nginx recargado"
            else
                print_error "Error al recargar Nginx"
            fi
        else
            print_error "Configuración de Nginx inválida"
        fi
    fi
fi

# ========================================
# 10. VERIFICACIÓN FINAL
# ========================================
print_header "10. VERIFICACIÓN FINAL"

print_info "Verificando que el servidor responde..."

# Esperar un poco para que el servidor se inicie
sleep 3

# Verificar HTTPS
if curl -Is https://gisa-nqn.com/login/admin-login/ | grep -q "200 OK"; then
    print_success "Servidor HTTPS respondiendo correctamente"
elif curl -Is http://gisa-nqn.com/login/admin-login/ | grep -q "200 OK"; then
    print_warning "Servidor HTTP respondiendo (deberías configurar HTTPS)"
else
    print_warning "No se pudo verificar el servidor automáticamente"
    print_info "Verifica manualmente: curl -I https://gisa-nqn.com/login/admin-login/"
fi

# ========================================
# RESUMEN FINAL
# ========================================
print_header "RESUMEN Y PRÓXIMOS PASOS"

echo -e "${BOLD}✅ INSTALACIÓN COMPLETADA${NC}\n"

echo -e "${BOLD}Próximos pasos:${NC}"
echo "1. Prueba el login desde otro navegador/computador"
echo "2. Ve a: https://gisa-nqn.com/login/admin-login/"
echo "3. Ingresa tu email y contraseña"
echo "4. Verifica que te lleve al dashboard"
echo "5. Recarga la página (F5) - deberías seguir en el dashboard"

echo -e "\n${BOLD}Si el problema persiste:${NC}"
echo "1. Revisa los logs: tail -f logs/django.log"
echo "2. Revisa logs de Nginx: sudo tail -f /var/log/nginx/error.log"
echo "3. Ejecuta el diagnóstico: python diagnostico_sesiones.py"
echo "4. Consulta: SOLUCION_PROBLEMA_LOGIN.md"

echo -e "\n${BOLD}Archivos importantes:${NC}"
echo "- SOLUCION_PROBLEMA_LOGIN.md (Documentación completa)"
echo "- diagnostico_sesiones.py (Script de diagnóstico)"
echo "- .env (Configuración del servidor)"

echo -e "\n${GREEN}${BOLD}¡Solución aplicada exitosamente!${NC}\n"

# Preguntar si quiere ver los logs
read -p "¿Ver logs en tiempo real? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    if [ -f "logs/django.log" ]; then
        echo -e "\n${BLUE}Mostrando logs (Ctrl+C para salir)...${NC}\n"
        tail -f logs/django.log
    else
        print_warning "No se encontró logs/django.log"
    fi
fi

exit 0


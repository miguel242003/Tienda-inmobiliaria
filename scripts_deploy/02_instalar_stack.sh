#!/bin/bash
# ============================================================================
# SCRIPT 2: INSTALAR STACK COMPLETO (Python, MySQL, Redis, Nginx)
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 INSTALANDO PYTHON 3.11+"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo apt install -y python3 python3-pip python3-venv python3-dev

echo "✅ Python instalado: $(python3 --version)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐬 INSTALANDO MYSQL 8.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo apt install -y mysql-server libmysqlclient-dev pkg-config

echo "✅ MySQL instalado"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 INSTALANDO REDIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo apt install -y redis-server

# Configurar Redis para iniciar automáticamente
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo "✅ Redis instalado y ejecutándose"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 INSTALANDO NGINX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo apt install -y nginx

# Habilitar Nginx para iniciar automáticamente
sudo systemctl enable nginx
sudo systemctl start nginx

echo "✅ Nginx instalado y ejecutándose"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 INSTALANDO SUPERVISOR (Gestión de Procesos)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo apt install -y supervisor

sudo systemctl enable supervisor
sudo systemctl start supervisor

echo "✅ Supervisor instalado"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 INSTALANDO CERTBOT (Let's Encrypt SSL)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo apt install -y certbot python3-certbot-nginx

echo "✅ Certbot instalado"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ¡STACK COMPLETO INSTALADO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Resumen de servicios instalados:"
echo "  🐍 Python:      $(python3 --version)"
echo "  🐬 MySQL:       $(mysql --version | cut -d' ' -f6)"
echo "  📦 Redis:       $(redis-server --version | cut -d'=' -f2 | cut -d' ' -f1)"
echo "  🌐 Nginx:       $(nginx -v 2>&1 | cut -d'/' -f2)"
echo "  🔧 Supervisor:  Instalado"
echo "  🔒 Certbot:     Instalado"
echo ""


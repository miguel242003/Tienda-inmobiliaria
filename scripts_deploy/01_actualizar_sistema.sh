#!/bin/bash
# ============================================================================
# SCRIPT 1: ACTUALIZAR SISTEMA Y CONFIGURACIÓN INICIAL
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 ACTUALIZANDO SISTEMA UBUNTU..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Actualizar lista de paquetes
apt update

# Actualizar todos los paquetes instalados
apt upgrade -y

# Instalar herramientas básicas
apt install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    unzip \
    software-properties-common \
    build-essential \
    ufw \
    fail2ban

echo "✅ Sistema actualizado correctamente"


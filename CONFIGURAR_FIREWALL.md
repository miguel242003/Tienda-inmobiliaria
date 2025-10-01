# 🛡️ GUÍA DE CONFIGURACIÓN DE FIREWALL

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Firewall en Linux (UFW)](#firewall-en-linux-ufw)
3. [Firewall en Linux (iptables)](#firewall-en-linux-iptables)
4. [Firewall en Windows](#firewall-en-windows)
5. [Configuración para Producción](#configuración-para-producción)
6. [Monitoreo y Logs](#monitoreo-y-logs)

---

## Introducción

### Puertos Necesarios para la Aplicación:

| Puerto | Servicio | Descripción | Acceso |
|--------|----------|-------------|--------|
| **22** | SSH | Acceso remoto | Restringido por IP |
| **80** | HTTP | Tráfico web (redirige a 443) | Público |
| **443** | HTTPS | Tráfico web seguro | Público |
| **3306** | MySQL | Base de datos | Solo localhost |
| **8000** | Django/Gunicorn | Servidor de aplicación | Solo localhost |

---

## Firewall en Linux (UFW)

UFW (Uncomplicated Firewall) es la forma más sencilla de configurar firewall en Ubuntu/Debian.

### 1. Instalación

```bash
# Instalar UFW
sudo apt update
sudo apt install ufw
```

### 2. Configuración Básica

```bash
# Verificar estado
sudo ufw status

# Establecer políticas por defecto
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (IMPORTANTE: hacerlo ANTES de habilitar UFW)
sudo ufw allow 22/tcp

# O restringir SSH a una IP específica
sudo ufw allow from TU_IP_OFICINA to any port 22

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# DENEGAR acceso externo a MySQL
sudo ufw deny 3306/tcp

# DENEGAR acceso externo a Django/Gunicorn
sudo ufw deny 8000/tcp

# Habilitar firewall
sudo ufw enable

# Verificar reglas
sudo ufw status numbered
```

### 3. Configuración Avanzada

```bash
# Limitar conexiones SSH (protección contra fuerza bruta)
sudo ufw limit 22/tcp

# Permitir rangos de IP
sudo ufw allow from 192.168.1.0/24

# Permitir puerto específico desde IP específica
sudo ufw allow from 203.0.113.10 to any port 22

# Eliminar regla
sudo ufw status numbered  # Ver número de regla
sudo ufw delete 5         # Eliminar regla #5

# Deshabilitar temporalmente
sudo ufw disable

# Reiniciar reglas
sudo ufw reload

# Resetear todas las reglas
sudo ufw reset
```

### 4. Logs de UFW

```bash
# Habilitar logging
sudo ufw logging on

# Ver logs
sudo tail -f /var/log/ufw.log

# Filtrar intentos bloqueados
sudo grep "BLOCK" /var/log/ufw.log
```

---

## Firewall en Linux (iptables)

Para configuraciones más avanzadas, puedes usar iptables directamente.

### 1. Reglas Básicas

```bash
# Ver reglas actuales
sudo iptables -L -n -v

# Limpiar todas las reglas
sudo iptables -F

# Establecer políticas por defecto
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Permitir tráfico localhost
sudo iptables -A INPUT -i lo -j ACCEPT

# Permitir conexiones establecidas
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Permitir SSH (con rate limiting)
sudo iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
sudo iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Permitir HTTP y HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# DENEGAR MySQL desde exterior (solo localhost)
sudo iptables -A INPUT -p tcp -s 127.0.0.1 --dport 3306 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3306 -j DROP

# DENEGAR Django/Gunicorn desde exterior
sudo iptables -A INPUT -p tcp -s 127.0.0.1 --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j DROP

# Protección contra flood SYN
sudo iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT

# Bloquear ping externo (opcional)
sudo iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
```

### 2. Guardar Reglas iptables

```bash
# En Ubuntu/Debian
sudo apt install iptables-persistent
sudo netfilter-persistent save

# En CentOS/RHEL
sudo service iptables save

# Manualmente
sudo iptables-save > /etc/iptables/rules.v4
```

### 3. Restaurar Reglas al Inicio

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/iptables-restore.service
```

Contenido:
```ini
[Unit]
Description=Restaurar reglas iptables
Before=network-pre.target

[Service]
Type=oneshot
ExecStart=/sbin/iptables-restore /etc/iptables/rules.v4

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar servicio
sudo systemctl enable iptables-restore.service
```

---

## Firewall en Windows

### 1. Firewall de Windows (GUI)

#### Abrir Firewall:
1. Panel de Control → Sistema y Seguridad → Firewall de Windows Defender
2. Click en "Configuración avanzada"

#### Crear Regla de Entrada (HTTP/HTTPS):
1. Click derecho en "Reglas de entrada" → Nueva regla
2. Tipo de regla: **Puerto**
3. TCP / Puertos específicos: **80, 443**
4. Acción: **Permitir la conexión**
5. Perfiles: Todos
6. Nombre: "Django - HTTP/HTTPS"

#### Bloquear Puerto MySQL:
1. Reglas de entrada → Nueva regla
2. Tipo: **Puerto**
3. TCP / Puerto: **3306**
4. Acción: **Bloquear la conexión**
5. Nombre: "MySQL - Bloquear Externo"

### 2. Firewall de Windows (PowerShell)

```powershell
# Ejecutar PowerShell como Administrador

# Ver reglas actuales
Get-NetFirewallRule | Where-Object {$_.Enabled -eq 'True'}

# Permitir HTTP (puerto 80)
New-NetFirewallRule -DisplayName "Django HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# Permitir HTTPS (puerto 443)
New-NetFirewallRule -DisplayName "Django HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Bloquear MySQL desde exterior
New-NetFirewallRule -DisplayName "MySQL Block External" -Direction Inbound -Protocol TCP -LocalPort 3306 -Action Block

# Bloquear Django/Gunicorn desde exterior
New-NetFirewallRule -DisplayName "Django Block External" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Block

# Permitir solo desde localhost a MySQL
New-NetFirewallRule -DisplayName "MySQL Localhost Only" -Direction Inbound -Protocol TCP -LocalPort 3306 -RemoteAddress 127.0.0.1 -Action Allow

# Eliminar regla
Remove-NetFirewallRule -DisplayName "Nombre de Regla"

# Deshabilitar regla
Disable-NetFirewallRule -DisplayName "Nombre de Regla"

# Habilitar regla
Enable-NetFirewallRule -DisplayName "Nombre de Regla"
```

### 3. Verificar Puertos Abiertos en Windows

```powershell
# Ver conexiones y puertos en escucha
netstat -ano | findstr "LISTENING"

# Ver puerto específico
netstat -ano | findstr ":3306"

# Ver con nombres de proceso
Get-NetTCPConnection | Where-Object {$_.State -eq "Listen"} | Select-Object LocalAddress, LocalPort, OwningProcess
```

---

## Configuración para Producción

### Script Completo de Configuración (Linux - UFW)

Crear archivo: `configurar_firewall.sh`

```bash
#!/bin/bash
# 🛡️ Script de Configuración de Firewall para Producción

echo "🛡️ Configurando Firewall de Producción..."

# Resetear reglas (CUIDADO: puede desconectarte si estás en SSH)
# sudo ufw --force reset

# Políticas por defecto
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH con limitación de intentos
sudo ufw limit 22/tcp comment 'SSH con rate limiting'

# Si tienes IP fija de oficina, úsala:
# sudo ufw allow from TU_IP_OFICINA to any port 22

# HTTP y HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# MySQL - SOLO localhost
sudo ufw deny 3306/tcp comment 'MySQL - Bloqueado desde exterior'

# Django/Gunicorn - SOLO localhost
sudo ufw deny 8000/tcp comment 'Django - Bloqueado desde exterior'

# Protección adicional contra flood
sudo ufw limit 80/tcp
sudo ufw limit 443/tcp

# Habilitar firewall
sudo ufw --force enable

# Mostrar estado
sudo ufw status verbose

echo "✅ Firewall configurado exitosamente"
```

```bash
# Dar permisos y ejecutar
chmod +x configurar_firewall.sh
sudo ./configurar_firewall.sh
```

### Verificar Configuración

```bash
# Verificar puertos abiertos externamente
sudo netstat -tulpn

# Verificar que MySQL solo escuche en localhost
sudo netstat -tulpn | grep 3306
# Debe mostrar: 127.0.0.1:3306

# Verificar que Django solo escuche en localhost
sudo netstat -tulpn | grep 8000
# Debe mostrar: 127.0.0.1:8000

# Test de conectividad desde otra máquina
# (Desde otra máquina)
telnet TU_IP_SERVIDOR 3306  # Debe fallar
telnet TU_IP_SERVIDOR 443    # Debe conectar
```

---

## Monitoreo y Logs

### 1. Monitorear Intentos de Conexión

```bash
# Ver logs de UFW en tiempo real
sudo tail -f /var/log/ufw.log

# Filtrar intentos bloqueados
sudo grep "BLOCK" /var/log/ufw.log | tail -20

# Ver intentos de conexión SSH fallidos
sudo grep "Failed password" /var/log/auth.log

# Ver IPs con más intentos bloqueados
sudo grep "BLOCK" /var/log/ufw.log | awk '{print $12}' | sort | uniq -c | sort -nr | head -10
```

### 2. Instalar Fail2Ban (Protección adicional)

```bash
# Instalar
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Configuración recomendada:
```ini
[DEFAULT]
bantime  = 3600      # 1 hora
findtime = 600       # 10 minutos
maxretry = 3         # 3 intentos

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
```

```bash
# Iniciar Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Ver IPs bloqueadas
sudo fail2ban-client status sshd

# Desbloquear IP
sudo fail2ban-client set sshd unbanip IP_ADDRESS
```

### 3. Alertas por Email (Opcional)

```bash
# Instalar mailutils
sudo apt install mailutils

# Crear script de alerta
sudo nano /usr/local/bin/firewall_alert.sh
```

Contenido:
```bash
#!/bin/bash
# Enviar alerta si hay muchos intentos bloqueados

BLOQUEADOS=$(grep "BLOCK" /var/log/ufw.log | tail -100 | wc -l)

if [ $BLOQUEADOS -gt 50 ]; then
    echo "ALERTA: $BLOQUEADOS intentos de conexión bloqueados en la última hora" | \
    mail -s "Alerta de Firewall - Tienda Inmobiliaria" admin@tudominio.com
fi
```

```bash
# Configurar cron job (cada hora)
sudo crontab -e
0 * * * * /usr/local/bin/firewall_alert.sh
```

---

## Checklist de Seguridad

- [ ] Firewall instalado y habilitado
- [ ] SSH limitado por tasa de conexión
- [ ] SSH restringido a IPs conocidas (opcional pero recomendado)
- [ ] HTTP (80) y HTTPS (443) abiertos
- [ ] MySQL (3306) bloqueado desde exterior
- [ ] Django/Gunicorn (8000) bloqueado desde exterior
- [ ] Fail2Ban instalado y configurado
- [ ] Logs monitoreados regularmente
- [ ] Alertas configuradas
- [ ] Backup de configuración realizado
- [ ] Documentación actualizada

---

## Comandos Útiles de Diagnóstico

```bash
# Ver todas las conexiones activas
sudo netstat -tupn

# Ver intentos de conexión rechazados
sudo dmesg | grep -i "firewall"

# Ver estadísticas de iptables
sudo iptables -L -n -v

# Verificar puertos en escucha
sudo ss -tulpn

# Test de conectividad desde el servidor
nc -zv localhost 3306    # Debe conectar
nc -zv tudominio.com 3306 # Debe fallar (timeout)

# Verificar que Nginx/Apache sirve correctamente
curl -I https://tudominio.com
```

---

## Troubleshooting

### Problema: Me bloqueé a mí mismo por SSH

**Solución:** Acceder por consola física o panel de control del hosting y ejecutar:
```bash
sudo ufw disable
sudo ufw allow 22/tcp
sudo ufw enable
```

### Problema: MySQL no es accesible ni desde localhost

```bash
# Verificar que MySQL escuche en 127.0.0.1
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Buscar línea:
bind-address = 127.0.0.1

# Reiniciar MySQL
sudo systemctl restart mysql
```

### Problema: Nginx no puede conectar a Gunicorn

```bash
# Verificar que Gunicorn escuche en localhost
ps aux | grep gunicorn

# Debe mostrar algo como:
# gunicorn --bind 127.0.0.1:8000 ...
```

---

## Recursos Adicionales

- [UFW Documentation](https://help.ubuntu.com/community/UFW)
- [iptables Tutorial](https://www.netfilter.org/documentation/)
- [Fail2Ban Manual](https://www.fail2ban.org/)
- [NIST Firewall Guidelines](https://csrc.nist.gov/publications/detail/sp/800-41/rev-1/final)

---

**Última actualización:** 30 de Septiembre, 2025  
**Importante:** Siempre prueba las reglas de firewall en un entorno de desarrollo antes de aplicarlas en producción.


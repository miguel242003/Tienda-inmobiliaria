# 🚀 GUÍA: Deploy Automático desde GitHub

## 📋 RESUMEN

Has configurado un script de deploy automático que te permite actualizar tu sitio web https://gisa-nqn.com con un solo comando.

---

## 🔄 FLUJO DE TRABAJO

```
┌────────────────────────────────────────────────────────────────┐
│ 1. TU COMPUTADORA (Windows)                                    │
├────────────────────────────────────────────────────────────────┤
│  • Haces cambios en el código                                  │
│  • git add .                                                   │
│  • git commit -m "Descripción"                                 │
│  • git push origin main                                        │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 2. GITHUB                                                       │
├────────────────────────────────────────────────────────────────┤
│  • Recibe y guarda los cambios                                 │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 3. SERVIDOR VPS (PuTTY)                                        │
├────────────────────────────────────────────────────────────────┤
│  • Ejecutas: ~/deploy.sh                                       │
│  • El script automáticamente:                                  │
│    ✓ Descarga cambios de GitHub                               │
│    ✓ Instala dependencias nuevas                              │
│    ✓ Ejecuta migraciones DB                                   │
│    ✓ Recolecta archivos estáticos                             │
│    ✓ Reinicia Gunicorn                                        │
└────────────────────────────────────────────────────────────────┘
                            ↓
                  ✅ Sitio actualizado
              https://gisa-nqn.com
```

---

## 🛠️ COMANDOS RÁPIDOS

### En tu computadora (Git Bash o PowerShell):

```bash
# Actualizar sitio con cambios
git add .
git commit -m "Mensaje descriptivo de cambios"
git push origin main
```

### En el servidor (PuTTY):

```bash
# Desplegar cambios
~/deploy.sh
```

---

## 📝 EJEMPLOS PRÁCTICOS

### Ejemplo 1: Cambiar el color del navbar

**En tu computadora:**
```bash
cd C:\Users\MiguelAstorga\Desktop\Tienda-inmobiliaria

# Editas static/css/style.css
# Cambias el color del navbar

git add static/css/style.css
git commit -m "Cambiar color del navbar a azul"
git push origin main
```

**En PuTTY:**
```bash
~/deploy.sh
```

**Resultado:** En 30 segundos el navbar tendrá el nuevo color en https://gisa-nqn.com

---

### Ejemplo 2: Agregar nueva funcionalidad (modelo, vista, template)

**En tu computadora:**
```bash
# Editas models.py, views.py, urls.py, templates, etc.

git add .
git commit -m "Agregar sistema de valoraciones de propiedades"
git push origin main
```

**En PuTTY:**
```bash
~/deploy.sh
```

**El script automáticamente:**
- Descarga el código nuevo
- Ejecuta las migraciones si creaste modelos nuevos
- Recolecta los templates y archivos estáticos
- Reinicia para que los cambios surtan efecto

---

### Ejemplo 3: Actualizar dependencias (agregar nueva librería)

**En tu computadora:**
```bash
# Instalas nueva librería localmente
pip install nueva-libreria

# Actualizas requirements.txt
pip freeze > requirements.txt

git add requirements.txt
git commit -m "Agregar nueva-libreria para funcionalidad X"
git push origin main
```

**En PuTTY:**
```bash
~/deploy.sh
```

**El script instalará automáticamente la nueva librería en el servidor.**

---

## ⚠️ SITUACIONES ESPECIALES

### Si el script falla en algún paso:

El script mostrará en qué paso falló:
```
❌ Error al obtener cambios de GitHub
```

**Soluciones comunes:**

1. **Error en git pull:**
   ```bash
   cd ~/Tienda-inmobiliaria
   git status
   git pull origin main
   ```

2. **Error en migraciones:**
   ```bash
   cd ~/Tienda-inmobiliaria
   source venv/bin/activate
   python manage.py migrate
   ```

3. **Error al reiniciar Gunicorn:**
   ```bash
   sudo supervisorctl status tienda_inmobiliaria
   sudo supervisorctl restart tienda_inmobiliaria
   ```

---

### Si necesitas revertir cambios:

**En el servidor:**
```bash
cd ~/Tienda-inmobiliaria
git log --oneline  # Ver últimos commits
git reset --hard COMMIT_ID  # Volver a un commit específico
sudo supervisorctl restart tienda_inmobiliaria
```

---

## 🔍 VER LOGS

### Logs de deploy:

Durante el deploy verás el output en pantalla.

### Logs de la aplicación:

```bash
# Logs de Gunicorn
tail -f ~/Tienda-inmobiliaria/logs/gunicorn.log

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 VERIFICAR ESTADO

### Después de cada deploy:

```bash
# Estado de Gunicorn
sudo supervisorctl status tienda_inmobiliaria

# Debe decir: RUNNING

# Verificar en navegador
# https://gisa-nqn.com
```

---

## 🎯 MEJORES PRÁCTICAS

### 1. Commits descriptivos:
```bash
✅ git commit -m "Agregar filtro de búsqueda por precio en propiedades"
❌ git commit -m "cambios"
```

### 2. Probar localmente antes de subir:
```bash
# En tu computadora, siempre prueba:
python manage.py runserver
# Verifica que todo funcione antes de hacer push
```

### 3. Hacer backups antes de cambios grandes:
```bash
# En el servidor, backup de BD:
mysqldump -u tienda_user -p tienda_inmobiliaria_prod > backup_$(date +%Y%m%d).sql
```

### 4. Deploy en horarios de bajo tráfico:
- Preferiblemente de madrugada
- El reinicio de Gunicorn toma solo 2-3 segundos

---

## 🚨 COMANDOS DE EMERGENCIA

### Si el sitio no responde después del deploy:

```bash
# 1. Ver logs
tail -50 ~/Tienda-inmobiliaria/logs/gunicorn.log

# 2. Reiniciar todo
sudo supervisorctl restart tienda_inmobiliaria
sudo systemctl restart nginx

# 3. Verificar estado
sudo supervisorctl status
sudo systemctl status nginx

# 4. Si sigue fallando, volver a commit anterior
cd ~/Tienda-inmobiliaria
git log --oneline
git reset --hard COMMIT_ANTERIOR
~/deploy.sh
```

---

## 📚 RECURSOS ADICIONALES

### Archivos importantes:

- **Script de deploy:** `~/deploy.sh`
- **Proyecto:** `~/Tienda-inmobiliaria/`
- **Logs:** `~/Tienda-inmobiliaria/logs/gunicorn.log`
- **Configuración Nginx:** `/etc/nginx/sites-available/tienda_inmobiliaria`
- **Configuración Supervisor:** `/etc/supervisor/conf.d/tienda_inmobiliaria.conf`

### Comandos útiles:

```bash
# Ver rama actual de Git
cd ~/Tienda-inmobiliaria && git branch

# Ver último commit
cd ~/Tienda-inmobiliaria && git log -1

# Ver archivos modificados
cd ~/Tienda-inmobiliaria && git status

# Descartar cambios locales (CUIDADO)
cd ~/Tienda-inmobiliaria && git reset --hard origin/main
```

---

## ✅ CHECKLIST POST-DEPLOY

Después de cada deploy, verifica:

```
□ ~/deploy.sh ejecutó sin errores
□ Gunicorn está RUNNING (supervisorctl status)
□ Sitio carga en https://gisa-nqn.com
□ No hay errores en logs (gunicorn.log)
□ Funcionalidad nueva funciona correctamente
□ No se rompió nada existente
```

---

## 🎉 ¡FELICIDADES!

Ahora tienes un sistema de deploy profesional que te permite actualizar tu sitio en segundos, sin downtime y de forma segura.

**Cada vez que quieras actualizar tu sitio:**
1. Haces cambios localmente
2. `git push`
3. `~/deploy.sh` en el servidor
4. ¡Listo! 🚀

---

**Sitio web:** https://gisa-nqn.com  
**Última actualización:** 4 de Octubre, 2025


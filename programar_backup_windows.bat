@echo off
REM 🔒 Script para programar backup automático en Windows Task Scheduler
REM Este script crea una tarea programada para ejecutar backups diarios

echo ========================================
echo   PROGRAMAR BACKUP AUTOMATICO
echo ========================================
echo.

REM Obtener ruta del proyecto
set PROJECT_PATH=%cd%
set PYTHON_PATH=python

echo Ruta del proyecto: %PROJECT_PATH%
echo.

echo Creando tarea programada...
echo.

REM Crear tarea programada (ejecutar como Administrador)
schtasks /Create /SC DAILY /TN "TiendaInmobiliaria_Backup_Diario" ^
  /TR "%PYTHON_PATH% %PROJECT_PATH%\backup_database.py" ^
  /ST 03:00 ^
  /F

if %ERRORLEVEL% EQU 0 (
    echo ✅ Tarea programada creada exitosamente!
    echo.
    echo Configuración:
    echo   - Nombre: TiendaInmobiliaria_Backup_Diario
    echo   - Frecuencia: Diaria
    echo   - Hora: 03:00 AM
    echo   - Script: %PROJECT_PATH%\backup_database.py
    echo.
    echo Para ver la tarea:
    echo   schtasks /Query /TN "TiendaInmobiliaria_Backup_Diario"
    echo.
    echo Para ejecutar manualmente:
    echo   schtasks /Run /TN "TiendaInmobiliaria_Backup_Diario"
    echo.
    echo Para eliminar la tarea:
    echo   schtasks /Delete /TN "TiendaInmobiliaria_Backup_Diario" /F
) else (
    echo ❌ Error al crear tarea programada
    echo    Asegúrate de ejecutar este script como Administrador
)

pause


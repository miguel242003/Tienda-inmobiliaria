@echo off
echo Iniciando aplicacion en modo produccion...

REM Verificar archivo .env
if not exist ".env" (
    echo Error: No se encontro el archivo .env
    pause
    exit /b 1
)

REM Iniciar servidor
python manage.py runserver 0.0.0.0:8000
pause

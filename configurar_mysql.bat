@echo off
echo ========================================
echo    CONFIGURAR MYSQL PARA TRACKING
echo ========================================
echo.

echo 1. Conectando a MySQL como root...
mysql -u root -p < configurar_mysql_clics.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ MySQL configurado correctamente!
    echo.
    echo 2. Verificando conexion...
    python verificar_conexion_mysql.py
    
    echo.
    echo 3. Probando sistema de tracking...
    python probar_tracking_clics.py
    
    echo.
    echo 🎉 ¡Configuracion completada!
    echo El boton "Ver Detalle" ahora deberia registrar clics en MySQL
) else (
    echo.
    echo ❌ Error al configurar MySQL
    echo Verifica que MySQL este ejecutandose y las credenciales sean correctas
)

pause

@echo off
title Instalador Proyecto EPP
cd /d "%~dp0"

echo ==========================================
echo   INSTALANDO PROYECTO EPP
echo ==========================================
echo.

py --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python no esta instalado o no esta agregado al PATH.
    echo.
    echo Solucion:
    echo 1. Instala Python.
    echo 2. Marca la opcion Add Python to PATH.
    echo 3. Vuelve a ejecutar este archivo.
    echo.
    pause
    exit /b
)

echo Python detectado correctamente.
echo.

echo Actualizando pip...
py -m pip install --upgrade pip

echo.
echo Instalando librerias del proyecto...
py -m pip install -r requirements.txt

echo.
echo Creando carpetas necesarias...

if not exist "imagenes_registro" mkdir "imagenes_registro"
if not exist "imagenes_incidentes" mkdir "imagenes_incidentes"

echo.
echo Creando archivos JSON si no existen...

if not exist "trabajadores.json" echo {} > trabajadores.json
if not exist "datos_empleados.json" echo {} > datos_empleados.json
if not exist "incidencias.json" echo [] > incidencias.json
if not exist "alertas_pendientes.json" echo [] > alertas_pendientes.json
if not exist "procesadas.json" echo [] > procesadas.json

echo.
echo ==========================================
echo   INSTALACION FINALIZADA CORRECTAMENTE
echo ==========================================
echo.
echo Ahora ejecuta configurar_aws.bat
echo.
pause
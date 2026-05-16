@echo off
title Proyecto EPP - Sistema Principal
cd /d "%~dp0"

echo ==========================================
echo      PROYECTO EPP - AWS REKOGNITION
echo ==========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo ERROR: El entorno virtual venv no existe.
    echo.
    echo Primero ejecuta instalar_todo.bat
    echo.
    pause
    exit /b
)

if not exist ".env" (
    echo ERROR: No existe el archivo .env
    echo.
    echo Primero ejecuta configurar_aws.bat
    echo.
    pause
    exit /b
)

if not exist "imagenes_registro" mkdir "imagenes_registro"
if not exist "imagenes_incidentes" mkdir "imagenes_incidentes"

if not exist "trabajadores.json" echo {} > trabajadores.json
if not exist "datos_trabajadores.json" echo {} > datos_trabajadores.json
if not exist "incidencias.json" echo [] > incidencias.json
if not exist "alertas_pendientes.json" echo [] > alertas_pendientes.json
if not exist "procesadas.json" echo [] > procesadas.json

echo Iniciando sistema con el entorno virtual...
echo.

venv\Scripts\python.exe menu_principal.py

echo.
echo Sistema cerrado.
pause

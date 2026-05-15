@echo off
title Proyecto EPP - Sistema Principal
cd /d "%~dp0"

echo ==========================================
echo      PROYECTO EPP - AWS REKOGNITION
echo ==========================================
echo.

if not exist ".env" (
    echo ERROR: No existe el archivo .env
    echo.
    echo Primero ejecuta configurar_aws.bat
    echo.
    pause
    exit /b
)

echo Cargando credenciales AWS...

for /f "tokens=1,* delims==" %%A in (.env) do (
    set "%%A=%%B"
)

if "%AWS_ACCESS_KEY_ID%"=="" (
    echo ERROR: AWS_ACCESS_KEY_ID no esta configurado.
    pause
    exit /b
)

if "%AWS_SECRET_ACCESS_KEY%"=="" (
    echo ERROR: AWS_SECRET_ACCESS_KEY no esta configurado.
    pause
    exit /b
)

if "%AWS_DEFAULT_REGION%"=="" (
    set AWS_DEFAULT_REGION=us-east-1
)

echo Credenciales cargadas correctamente.
echo Region AWS: %AWS_DEFAULT_REGION%
echo.

if not exist "imagenes_registro" mkdir "imagenes_registro"
if not exist "imagenes_incidentes" mkdir "imagenes_incidentes"

if not exist "trabajadores.json" echo {} > trabajadores.json
if not exist "datos_empleados.json" echo {} > datos_empleados.json
if not exist "incidencias.json" echo [] > incidencias.json
if not exist "alertas_pendientes.json" echo [] > alertas_pendientes.json
if not exist "procesadas.json" echo [] > procesadas.json

echo Verificando coleccion de AWS Rekognition...
py crear_coleccion.py

echo.
echo Abriendo menu principal del sistema...
echo.

py menu_principal.py

echo.
echo Sistema cerrado.
pause
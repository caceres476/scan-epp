@echo off
title Configuracion AWS Proyecto EPP
cd /d "%~dp0"

echo ==========================================
echo   CONFIGURACION DE AWS REKOGNITION
echo ==========================================
echo.
echo Pega las credenciales AWS que te compartieron.
echo Estas credenciales NO se deben subir a GitHub.
echo.

set /p ACCESS_KEY=Ingresa AWS_ACCESS_KEY_ID: 
set /p SECRET_KEY=Ingresa AWS_SECRET_ACCESS_KEY: 
set /p REGION=Ingresa AWS_DEFAULT_REGION (presiona enter para us-east-1): 
set /p COLECION=Ingresa NOMBRE_COLECCION (presiona enter para trabajadores_epp): 

if "%REGION%"=="" set REGION=us-east-1
if "%COLECION%"=="" set COLECION=trabajadores_epp

if "%ACCESS_KEY%"=="" (
    echo.
    echo ERROR: AWS_ACCESS_KEY_ID no puede estar vacio.
    pause
    exit /b
)

if "%SECRET_KEY%"=="" (
    echo.
    echo ERROR: AWS_SECRET_ACCESS_KEY no puede estar vacio.
    pause
    exit /b
)

echo.
echo Guardando configuracion en archivo .env...

(
echo AWS_ACCESS_KEY_ID=%ACCESS_KEY%
echo AWS_SECRET_ACCESS_KEY=%SECRET_KEY%
echo AWS_DEFAULT_REGION=%REGION%
echo NOMBRE_COLECCION=%COLECION%
) > .env

echo.
echo ==========================================
echo   CONFIGURACION GUARDADA CORRECTAMENTE
echo ==========================================
echo.
echo Archivo creado: .env
echo IMPORTANTE: No subas el archivo .env a GitHub.
echo.
echo Ahora ejecuta verificar_configuracion.bat
echo.
pause
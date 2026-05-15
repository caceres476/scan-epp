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
set /p REGION=Ingresa AWS_DEFAULT_REGION, ejemplo us-east-1: 

if "%REGION%"=="" set REGION=us-east-1

echo.
echo Guardando configuracion en archivo .env...

(
echo AWS_ACCESS_KEY_ID=%ACCESS_KEY%
echo AWS_SECRET_ACCESS_KEY=%SECRET_KEY%
echo AWS_DEFAULT_REGION=%REGION%
) > .env

echo.
echo ==========================================
echo   CONFIGURACION GUARDADA CORRECTAMENTE
echo ==========================================
echo.
echo Archivo creado: .env
echo IMPORTANTE: No subas el archivo .env a GitHub.
echo.
echo Ahora ejecuta ejecutar_proyecto.bat
echo.
pause
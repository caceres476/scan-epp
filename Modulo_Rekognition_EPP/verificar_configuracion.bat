@echo off
title Verificar Configuracion Proyecto EPP
cd /d "%~dp0"

echo ==========================================
echo   VERIFICANDO CONFIGURACION DEL SISTEMA
echo ==========================================
echo.

set ERROR_ENCONTRADO=0

echo Verificando Python...
py --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python no esta instalado o en el PATH.
    set ERROR_ENCONTRADO=1
) ELSE (
    echo [OK] Python instalado.
)

echo Verificando venv...
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] El entorno virtual venv no existe. Ejecuta instalar_todo.bat primero.
    set ERROR_ENCONTRADO=1
) ELSE (
    echo [OK] Entorno virtual venv encontrado.
)

echo Verificando dependencias en requirements.txt...
if not exist "requirements.txt" (
    echo [ERROR] No existe requirements.txt.
    set ERROR_ENCONTRADO=1
) ELSE (
    echo [OK] requirements.txt existe.
)

echo Verificando .env...
if not exist ".env" (
    echo [ERROR] No existe .env. Ejecuta configurar_aws.bat primero.
    set ERROR_ENCONTRADO=1
) ELSE (
    echo [OK] .env configurado.
)

echo Verificando carpetas...
if not exist "imagenes_registro" (
    echo [ERROR] Falta carpeta imagenes_registro.
    set ERROR_ENCONTRADO=1
) ELSE (
    echo [OK] Carpeta imagenes_registro existe.
)
if not exist "imagenes_incidentes" (
    echo [ERROR] Falta carpeta imagenes_incidentes.
    set ERROR_ENCONTRADO=1
) ELSE (
    echo [OK] Carpeta imagenes_incidentes existe.
)

echo Verificando archivos JSON...
for %%F in (trabajadores.json datos_trabajadores.json incidencias.json alertas_pendientes.json procesadas.json) do (
    if not exist "%%F" (
        echo [ERROR] Falta archivo %%F.
        set ERROR_ENCONTRADO=1
    ) ELSE (
        echo [OK] Archivo %%F existe.
    )
)

echo.
if %ERROR_ENCONTRADO%==1 (
    echo ==========================================
    echo   SE ENCONTRARON ERRORES
    echo ==========================================
    echo Revisa los mensajes de arriba y soluciona los problemas.
    echo.
    pause
    exit /b
)

echo ==========================================
echo   ARCHIVOS LOCALES OK. VERIFICANDO AWS...
echo ==========================================
echo.
venv\Scripts\python.exe verificar_aws.py

echo.
echo Presiona cualquier tecla para cerrar...
pause

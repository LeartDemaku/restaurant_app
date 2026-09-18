@echo off
title STRICT LOUNGE ^& BAR
cd /d "%~dp0"

echo ========================================================
echo        STRICT LOUNGE ^& BAR - Sistemi i Restaurantit
echo ========================================================
echo Duke nisur aplikacionin... Ju lutem prisni 10-20 sekonda...
echo.

:: Kontrollo nese Python eshte i instaluar
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ GABIM: Python nuk u gjet!
    echo    Instaloni Python nga: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Nis aplikacionin
python -c "from desktop.launcher import launch_desktop; launch_desktop()"

if errorlevel 1 (
    echo.
    echo ========================================================
    echo  ❌ Ndodhi nje problem. Kontrolloni:
    echo     1. A jane instaluar paketat: pip install -r requirements.txt
    echo     2. A eshte porta 8000 e lire?
    echo ========================================================
    pause
)

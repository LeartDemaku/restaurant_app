@echo off
title STRICT LOUNGE & BAR
cd /d "%~dp0"

echo ========================================================
echo        STRICT LOUNGE & BAR - Sistemi i Restaurantit
echo ========================================================
echo Duke nisur aplikacionin... Ju lutem prisni pak...

python -c "from desktop.launcher import launch_desktop; launch_desktop()"

if errorlevel 1 (
    echo.
    echo Ndodhi nje problem gjate hapjes se sistemit.
    pause
)

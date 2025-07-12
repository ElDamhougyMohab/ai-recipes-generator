@echo off
title AI Recipe Generator - Quick Stop
echo.
echo ========================================
echo    🛑 AI Recipe Generator - Stopping...
echo ========================================
echo.

REM Stop all containers
echo [1/2] Stopping containers...
docker-compose down --remove-orphans

if %errorlevel% neq 0 (
    echo ❌ Failed to stop some containers!
    echo You may need to stop them manually with: docker-compose down --remove-orphans
) else (
    echo ✅ All containers stopped successfully
)

echo.
echo [2/2] Cleanup completed
echo.
echo ========================================
echo    🎉 AI Recipe Generator stopped!
echo ========================================
echo.
echo To start again, run: start.bat
echo.
echo Press any key to exit...
pause >nul

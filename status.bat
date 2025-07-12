@echo off
title AI Recipe Generator - Status Check
echo.
echo ========================================
echo    📊 AI Recipe Generator - Status
echo ========================================
echo.

REM Check Docker status
echo [1/3] Docker Status:
docker --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not available
    echo.
    echo To fix this:
    echo 1. Install Docker Desktop from: https://docker.com/products/docker-desktop
    echo 2. Start Docker Desktop
    echo 3. Run this script again
    goto end
) else (
    echo ✅ Docker is running
)

echo.
echo [2/3] Container Status:
docker-compose ps 2>nul
if %errorlevel% neq 0 (
    echo ❌ No containers found or docker-compose not available
    echo Run start.bat to start the application
) else (
    echo.
    echo [3/3] Service Health:
    echo 🔍 Checking if services are responding...
    
    REM Check frontend
    curl -s http://localhost:3000 >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Frontend: http://localhost:3000 - HEALTHY
    ) else (
        echo ❌ Frontend: http://localhost:3000 - NOT RESPONDING
    )
    
    REM Check backend
    curl -s http://localhost:8000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Backend: http://localhost:8000 - HEALTHY
    ) else (
        echo ❌ Backend: http://localhost:8000 - NOT RESPONDING
    )
    
    REM Check database
    docker-compose exec -T db pg_isready -U recipe_user -d recipes_db >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Database: PostgreSQL - HEALTHY
    ) else (
        echo ❌ Database: PostgreSQL - NOT RESPONDING
    )
)

:end
echo.
echo ========================================
echo    Quick Actions:
echo    • start.bat  - Start the application
echo    • stop.bat   - Stop the application
echo    • status.bat - Check status (this script)
echo ========================================
echo.
echo Press any key to exit...
pause >nul

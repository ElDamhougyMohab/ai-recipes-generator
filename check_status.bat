@echo off
title AI Recipe Generator - Status
echo.
echo ========================================
echo    AI Recipe Generator - Status Check
echo ========================================
echo.

REM Check Docker status
echo [1/3] Docker Status:
docker --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not available
) else (
    echo ✅ Docker is running
)

echo.
echo [2/3] Container Status:
docker-compose ps 2>nul
if %errorlevel% neq 0 (
    echo ❌ No containers found or Docker Compose not available
)

echo.
echo [3/3] Service Health Check:
echo.
echo 🌐 Testing Frontend (http://localhost:3000)...
curl -s -o nul -w "Status: %%{http_code}" http://localhost:3000 2>nul
if %errorlevel% neq 0 (
    echo ❌ Frontend not accessible
) else (
    echo ✅ Frontend accessible
)

echo.
echo 🔧 Testing Backend API (http://localhost:8000/health)...
curl -s -o nul -w "Status: %%{http_code}" http://localhost:8000/health 2>nul
if %errorlevel% neq 0 (
    echo ❌ Backend API not accessible
) else (
    echo ✅ Backend API accessible
)

echo.
echo ========================================
echo    Status Check Complete
echo ========================================
echo.
echo Press any key to exit...
pause >nul

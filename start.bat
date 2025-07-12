@echo off
title AI Recipe Generator - Quick Start
echo.
echo ========================================
echo    🍳 AI Recipe Generator - Starting...
echo ========================================
echo.

REM Check if Docker is running
echo [1/4] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running!
    echo Please install Docker Desktop and make sure it's running.
    pause
    exit /b 1
)
echo ✅ Docker is ready

REM Stop any existing containers first
echo.
echo [2/4] Stopping any existing containers...
docker-compose down --remove-orphans >nul 2>&1
echo ✅ Existing containers stopped

REM Start the application
echo.
echo [3/4] Starting AI Recipe Generator...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo ❌ Failed to start the application!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo ✅ Application started successfully!
echo.
echo [4/4] Application URLs:
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 API Documentation: http://localhost:8000/docs
echo 🗄️ Database: postgresql://localhost:5432/recipes_db
echo.
echo ========================================
echo    🎉 AI Recipe Generator is running!
echo ========================================
echo.
echo Press any key to exit...
pause >nul

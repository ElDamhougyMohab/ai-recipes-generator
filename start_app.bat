@echo off
title AI Recipe Generator - Startup
echo.
echo ========================================
echo    AI Recipe Generator - Starting...
echo ========================================
echo.

REM Check if Docker is running
echo [1/4] Checking Docker status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running!
    echo Please install Docker Desktop and make sure it's running.
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Load environment variables from .env file
echo.
echo [2/4] Loading environment variables from .env file...
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a"=="DATABASE_URL" (
            set "%%a=%%b"
        )
    )
    echo ✅ Environment variables loaded from .env file
) else (
    echo ❌ .env file not found! Please copy .env.example to .env
    pause
    exit /b 1
)

REM Check if GEMINI_API_KEY is set
if "%GEMINI_API_KEY%"=="" (
    echo ❌ GEMINI_API_KEY not found in .env file!
    echo Please check your .env file and make sure GEMINI_API_KEY is set.
    pause
    exit /b 1
)
echo ✅ GEMINI_API_KEY is set

REM Stop any existing containers
echo.
echo [3/4] Stopping existing containers...
docker-compose down --remove-orphans >nul 2>&1
echo ✅ Stopped existing containers

REM Start the application
echo.
echo [4/4] Starting AI Recipe Generator...
echo This may take a few minutes on first run...
echo.
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start the application!
    echo Please check the error messages above.
    pause
    exit /b 1
)

REM Wait for services to be ready
echo.
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo.
echo 🔍 Checking service status...
docker-compose ps

echo.
echo ========================================
echo    🎉 AI Recipe Generator Started!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 Database: localhost:5432
echo.
echo 📋 To stop the application, run: docker-compose down
echo 📋 To view logs, run: docker-compose logs -f
echo.
echo Opening the application in your browser...
echo.

REM Try to open the browser
start http://localhost:3000

echo Press any key to exit...
pause >nul

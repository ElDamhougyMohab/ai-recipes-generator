@echo off
title AI Recipe Generator - Shutdown
echo.
echo ========================================
echo    AI Recipe Generator - Stopping...
echo ========================================
echo.

REM Stop all containers
echo [1/2] Stopping containers...
docker-compose down --remove-orphans

if %errorlevel% neq 0 (
    echo ❌ Failed to stop some containers!
    echo You may need to stop them manually.
) else (
    echo ✅ All containers stopped successfully
)

REM Clean up (optional)
echo.
echo [2/2] Cleaning up...
docker system prune -f >nul 2>&1
echo ✅ Cleaned up unused Docker resources

echo.
echo ========================================
echo    🛑 AI Recipe Generator Stopped!
echo ========================================
echo.
echo All services have been stopped and cleaned up.
echo.
echo Press any key to exit...
pause >nul

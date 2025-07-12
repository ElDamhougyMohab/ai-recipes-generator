@echo off
title AI Recipe Generator - Environment Setup
echo.
echo 🍳 AI Recipe Generator - Environment Setup
echo ==========================================
echo.

REM Check if .env already exists
if exist ".env" (
    echo ⚠️  .env file already exists!
    set /p "overwrite=Do you want to overwrite it? (y/N): "
    if /i not "%overwrite%"=="y" (
        echo Setup cancelled.
        pause
        exit /b 0
    )
)

REM Check if .env.example exists
if not exist ".env.example" (
    echo ❌ .env.example file not found!
    pause
    exit /b 1
)

REM Copy the example file
copy ".env.example" ".env" >nul
echo ✅ Created .env file from .env.example
echo.

echo 📝 Please edit the .env file and add your actual values:
echo    1. GEMINI_API_KEY - Get from: https://makersuite.google.com/app/apikey
echo    2. Update database passwords if needed
echo    3. Set other environment-specific values
echo.

echo 🚀 After updating .env, you can start the application with:
echo    • start.bat
echo.

echo 📂 Opening .env file for editing...
if exist "%PROGRAMFILES%\Microsoft VS Code\Code.exe" (
    "%PROGRAMFILES%\Microsoft VS Code\Code.exe" .env
) else if exist "%USERPROFILE%\AppData\Local\Programs\Microsoft VS Code\Code.exe" (
    "%USERPROFILE%\AppData\Local\Programs\Microsoft VS Code\Code.exe" .env
) else (
    notepad .env
)

echo.
echo Press any key to continue...
pause >nul

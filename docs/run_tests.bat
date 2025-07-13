@echo off
REM ===============================================================
REM AI Recipe Generator - Test Automation Script for Windows
REM ===============================================================

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║          🧪 AI Recipe Generator Test Automation              ║
echo ║                Windows Batch Version                         ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if we're in the right directory
if not exist "run_comprehensive_tests.py" (
    echo ❌ run_comprehensive_tests.py not found in current directory
    echo 💡 Make sure you're running this from the project root
    pause
    exit /b 1
)

echo ✅ Test script found

REM Install required dependencies
echo.
echo 📦 Installing/checking dependencies...
pip install pytest pytest-cov pytest-html pytest-asyncio httpx requests

REM Optional dependencies for enhanced features
echo.
echo 📦 Installing optional dependencies for enhanced reports...
pip install pytest-xdist reportlab matplotlib plotly

echo.
echo 🚀 Starting comprehensive test execution...
echo.

REM Run the main test script with coverage and HTML reports
python run_comprehensive_tests.py --coverage --html --verbose

REM Check the exit code
if %errorlevel% equ 0 (
    echo.
    echo ✅ All tests completed successfully!
    echo 📊 Check the test_reports directory for detailed results
) else (
    echo.
    echo ⚠️  Some tests failed or encountered issues
    echo 📋 Check the failure analysis for details
)

echo.
echo 📁 Opening reports directory...
start "" "test_reports"

echo.
echo Press any key to exit...
pause >nul

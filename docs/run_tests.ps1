# ===============================================================
# AI Recipe Generator - Test Automation Script (PowerShell)
# ===============================================================

param(
    [switch]$Quick,
    [switch]$Coverage,
    [switch]$PDF,
    [switch]$HTML,
    [switch]$Parallel,
    [switch]$FailuresOnly,
    [switch]$Verbose,
    [switch]$Help
)

function Show-Help {
    Write-Host @"
🧪 AI Recipe Generator - Test Automation Suite

DESCRIPTION:
    Comprehensive test runner for the AI Recipe Generator application.
    Runs all tests, generates reports, and provides detailed analysis.

USAGE:
    .\run_tests.ps1 [OPTIONS]

OPTIONS:
    -Quick          Run only fast tests (exclude performance tests)
    -Coverage       Generate detailed coverage reports
    -PDF            Generate PDF report (requires reportlab)
    -HTML           Generate interactive HTML dashboard
    -Parallel       Run tests in parallel (faster execution)
    -FailuresOnly   Show only failed tests in output
    -Verbose        Show detailed output during execution
    -Help           Show this help message

EXAMPLES:
    .\run_tests.ps1                          # Full test suite
    .\run_tests.ps1 -Quick                   # Quick test run
    .\run_tests.ps1 -Coverage -HTML          # With coverage and dashboard
    .\run_tests.ps1 -Parallel -Verbose       # Parallel with detailed output

OUTPUTS:
    - test_reports/                          # All generated reports
    - test_reports/test_summary_*.json       # Test results summary
    - test_reports/basic_test_report_*.html  # HTML test report
    - test_reports/coverage/index.html       # Coverage report (if -Coverage)
    - test_reports/dashboard_*.html          # Interactive dashboard (if -HTML)

"@ -ForegroundColor Cyan
}

function Write-Banner {
    Write-Host @"

╔═══════════════════════════════════════════════════════════════════════════════╗
║                   🧪 AI Recipe Generator Test Suite                           ║
║                     PowerShell Automation Script                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

    Write-Host "📊 Configuration:" -ForegroundColor Yellow
    Write-Host "├── Mode: $(if ($Quick) { 'Quick' } else { 'Comprehensive' })"
    Write-Host "├── Coverage: $(if ($Coverage) { 'Enabled' } else { 'Disabled' })"
    Write-Host "├── Parallel: $(if ($Parallel) { 'Enabled' } else { 'Disabled' })"
    Write-Host "├── Reports: test_reports/"
    Write-Host "└── Timestamp: $(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "📦 Checking prerequisites..." -ForegroundColor Blue
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Python: $pythonVersion"
        } else {
            throw "Python not found"
        }
    }
    catch {
        Write-Host "  ❌ Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "  💡 Please install Python 3.8+ and add it to your PATH" -ForegroundColor Yellow
        return $false
    }
    
    # Check if we're in the right directory
    if (-not (Test-Path "run_comprehensive_tests.py")) {
        Write-Host "  ❌ run_comprehensive_tests.py not found" -ForegroundColor Red
        Write-Host "  💡 Make sure you're running this from the project root" -ForegroundColor Yellow
        return $false
    }
    Write-Host "  ✅ Test script found"
    
    # Check backend directory
    if (-not (Test-Path "backend")) {
        Write-Host "  ❌ backend directory not found" -ForegroundColor Red
        return $false
    }
    Write-Host "  ✅ Backend directory found"
    
    return $true
}

function Install-Dependencies {
    Write-Host "📦 Installing/checking dependencies..." -ForegroundColor Blue
    
    # Required dependencies
    $requiredPackages = @(
        "pytest",
        "pytest-cov", 
        "pytest-html",
        "pytest-asyncio",
        "httpx",
        "requests"
    )
    
    Write-Host "  Installing required packages..."
    pip install $requiredPackages -q
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Required packages installed"
    } else {
        Write-Host "  ⚠️ Some required packages may have failed to install" -ForegroundColor Yellow
    }
    
    # Optional dependencies for enhanced features
    $optionalPackages = @(
        "pytest-xdist",  # For parallel testing
        "reportlab",     # For PDF generation
        "matplotlib",    # For charts
        "plotly"         # For interactive charts
    )
    
    Write-Host "  Installing optional packages for enhanced features..."
    pip install $optionalPackages -q
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Optional packages installed"
    } else {
        Write-Host "  ⚠️ Some optional packages failed to install (features may be limited)" -ForegroundColor Yellow
    }
}

function Invoke-TestSuite {
    Write-Host "🚀 Starting comprehensive test execution..." -ForegroundColor Green
    Write-Host ""
    
    # Build command arguments
    $testArgs = @()
    
    if ($Quick) { $testArgs += "--quick" }
    if ($Coverage) { $testArgs += "--coverage" }
    if ($PDF) { $testArgs += "--pdf" }
    if ($HTML) { $testArgs += "--html" }
    if ($Parallel) { $testArgs += "--parallel" }
    if ($FailuresOnly) { $testArgs += "--failures-only" }
    if ($Verbose) { $testArgs += "--verbose" }
    
    # Run the test suite
    $startTime = Get-Date
    python run_comprehensive_tests.py @testArgs
    $exitCode = $LASTEXITCODE
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "⏱️ Total execution time: $($duration.ToString('mm\:ss'))" -ForegroundColor Cyan
    
    return $exitCode
}

function Show-Results {
    param($exitCode)
    
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Gray
    
    if ($exitCode -eq 0) {
        Write-Host "🎉 TEST SUITE COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host ""
        Write-Host "✅ All tests passed"
        Write-Host "📊 Check the test_reports directory for detailed results"
        Write-Host "🚀 Ready for deployment!"
    }
    elseif ($exitCode -eq 1) {
        Write-Host "⚠️ TEST SUITE COMPLETED WITH FAILURES" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "🔍 Some tests failed - check the reports for details"
        Write-Host "📋 Review DETAILED_TEST_FAILURE_ANALYSIS.md for solutions"
        Write-Host "🔧 Fix high-priority issues and re-run tests"
    }
    else {
        Write-Host "❌ TEST SUITE ENCOUNTERED ERRORS" -ForegroundColor Red
        Write-Host ""
        Write-Host "💥 Unexpected error occurred during test execution"
        Write-Host "📝 Check the log files for detailed error information"
    }
    
    Write-Host ""
    Write-Host "📁 Generated Reports:" -ForegroundColor Cyan
    
    if (Test-Path "test_reports") {
        $reportFiles = Get-ChildItem "test_reports" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10
        foreach ($file in $reportFiles) {
            $icon = switch ($file.Extension) {
                ".html" { "🌐" }
                ".pdf" { "📄" }
                ".json" { "📊" }
                ".xml" { "📋" }
                ".log" { "📝" }
                default { "📁" }
            }
            Write-Host "├── $icon $($file.Name)"
        }
        
        Write-Host ""
        Write-Host "🔗 Opening reports directory..." -ForegroundColor Blue
        Start-Process "test_reports"
    }
    
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Gray
}

# Main execution
function Main {
    # Show help if requested
    if ($Help) {
        Show-Help
        return 0
    }
    
    # Show banner
    Write-Banner
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Host "❌ Prerequisites check failed" -ForegroundColor Red
        return 1
    }
    
    # Install dependencies
    Install-Dependencies
    
    # Run test suite
    $exitCode = Invoke-TestSuite
    
    # Show results
    Show-Results $exitCode
    
    return $exitCode
}

# Handle Ctrl+C gracefully
$null = Register-EngineEvent PowerShell.Exiting -Action {
    Write-Host ""
    Write-Host "⚠️ Test execution interrupted by user" -ForegroundColor Yellow
}

# Execute main function
try {
    $exitCode = Main
    exit $exitCode
}
catch {
    Write-Host ""
    Write-Host "❌ Fatal error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "📝 Check the error details above for troubleshooting" -ForegroundColor Yellow
    exit 1
}

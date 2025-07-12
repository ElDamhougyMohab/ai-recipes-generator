# PowerShell script for external access
Write-Host "====================================" -ForegroundColor Green
Write-Host "  AI Recipe Generator - External Access" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Get local IP address
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*"}).IPAddress | Select-Object -First 1

if ($ip) {
    Write-Host "Your IP address: $ip" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "External users can access:" -ForegroundColor Cyan
    Write-Host "Frontend: http://$ip:3000" -ForegroundColor White
    Write-Host "Backend API: http://$ip:8000" -ForegroundColor White
    Write-Host "API Docs: http://$ip:8000/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Could not detect IP address. Run 'ipconfig' to find it manually." -ForegroundColor Red
}

Write-Host "Make sure to:" -ForegroundColor Yellow
Write-Host "1. Allow apps through Windows Firewall (ports 3000 and 8000)" -ForegroundColor White
Write-Host "2. Share your IP address with external users" -ForegroundColor White
Write-Host "3. Ensure you're on the same network (for local network access)" -ForegroundColor White
Write-Host ""

Write-Host "Starting backend server..." -ForegroundColor Green
Set-Location "backend"
& "venv\Scripts\Activate.ps1"
Start-Process powershell -ArgumentList "-Command", "& 'venv\Scripts\Activate.ps1'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host "Starting frontend server..." -ForegroundColor Green
Set-Location "..\frontend"
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
$env:HOST = "0.0.0.0"
Start-Process powershell -ArgumentList "-Command", "`$env:PATH = 'C:\Program Files\nodejs;' + `$env:PATH; `$env:HOST = '0.0.0.0'; npm start"

Write-Host ""
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "Backend will be available at: http://0.0.0.0:8000" -ForegroundColor White
Write-Host "Frontend will be available at: http://0.0.0.0:3000" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"

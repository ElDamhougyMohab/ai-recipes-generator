# PowerShell Script to rebuild and redeploy frontend with fixed API configuration

Write-Host "🚀 Rebuilding Frontend with Fixed API Configuration" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "frontend/package.json")) {
    Write-Host "❌ Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Set-Location frontend

Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install failed!" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Building frontend for production..." -ForegroundColor Yellow
$env:NODE_ENV = "production"
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend build successful!" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Build Summary:" -ForegroundColor White
Write-Host "- API Base URL: Using relative URLs for production" -ForegroundColor White
Write-Host "- Environment: production" -ForegroundColor White
Write-Host "- Output directory: frontend/build/" -ForegroundColor White

Write-Host ""
Write-Host "🔍 Checking build output..." -ForegroundColor Yellow

if (Test-Path "build/index.html") {
    Write-Host "✅ index.html created" -ForegroundColor Green
} else {
    Write-Host "❌ index.html not found" -ForegroundColor Red
}

if (Test-Path "build/static") {
    Write-Host "✅ Static assets created" -ForegroundColor Green
    $jsFiles = (Get-ChildItem "build/static/js" -Filter "*.js").Count
    $cssFiles = (Get-ChildItem "build/static/css" -Filter "*.css").Count
    Write-Host "   JS files: $jsFiles" -ForegroundColor White
    Write-Host "   CSS files: $cssFiles" -ForegroundColor White
} else {
    Write-Host "❌ Static assets not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Upload the build/ directory contents to your S3 bucket" -ForegroundColor White
Write-Host "2. Invalidate CloudFront cache for /*" -ForegroundColor White
Write-Host "3. Test the deployed application" -ForegroundColor White

Write-Host ""
Write-Host "🛠️  Manual deployment commands:" -ForegroundColor Yellow
Write-Host "aws s3 sync build/ s3://your-frontend-bucket --delete" -ForegroundColor Gray
Write-Host "aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths '/*'" -ForegroundColor Gray

Set-Location ..
Write-Host ""
Write-Host "✅ Frontend rebuild complete!" -ForegroundColor Green

Write-Host ""
Write-Host "💡 Quick Test:" -ForegroundColor Cyan
Write-Host "After deployment, open browser console on https://d173g01t5c4w0h.cloudfront.net" -ForegroundColor White
Write-Host "Look for API Base URL logs to confirm relative URLs are being used" -ForegroundColor White

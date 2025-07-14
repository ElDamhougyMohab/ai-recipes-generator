#!/bin/bash
# Script to rebuild and redeploy frontend with fixed API configuration

echo "🚀 Rebuilding Frontend with Fixed API Configuration"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo "📦 Installing dependencies..."
npm install

echo "🔧 Building frontend for production..."
NODE_ENV=production npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful!"
else
    echo "❌ Frontend build failed!"
    exit 1
fi

echo ""
echo "📋 Build Summary:"
echo "- API Base URL: Using relative URLs for production"
echo "- Environment: production"
echo "- Output directory: frontend/build/"

echo ""
echo "🔍 Checking build output..."
if [ -f "build/index.html" ]; then
    echo "✅ index.html created"
else
    echo "❌ index.html not found"
fi

if [ -d "build/static" ]; then
    echo "✅ Static assets created"
    echo "   JS files: $(find build/static/js -name "*.js" | wc -l)"
    echo "   CSS files: $(find build/static/css -name "*.css" | wc -l)"
else
    echo "❌ Static assets not found"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Upload the build/ directory contents to your S3 bucket"
echo "2. Invalidate CloudFront cache for /*"
echo "3. Test the deployed application"

echo ""
echo "🛠️  Manual deployment commands:"
echo "aws s3 sync build/ s3://your-frontend-bucket --delete"
echo "aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths '/*'"

cd ..
echo ""
echo "✅ Frontend rebuild complete!"

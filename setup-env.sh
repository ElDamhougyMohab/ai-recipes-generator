#!/bin/bash
# Setup script for AI Recipe Generator

echo "🍳 AI Recipe Generator - Environment Setup"
echo "=========================================="
echo

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Copy the example file
if [ ! -f ".env.example" ]; then
    echo "❌ .env.example file not found!"
    exit 1
fi

cp .env.example .env
echo "✅ Created .env file from .env.example"
echo

echo "📝 Please edit the .env file and add your actual values:"
echo "   1. GEMINI_API_KEY - Get from: https://makersuite.google.com/app/apikey"
echo "   2. Update database passwords if needed"
echo "   3. Set other environment-specific values"
echo

echo "🚀 After updating .env, you can start the application with:"
echo "   • Windows: start.bat"
echo "   • Linux/Mac: docker-compose up -d"
echo

read -p "Press Enter to continue..."

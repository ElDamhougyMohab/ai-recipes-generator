# 🔧 Environment Setup Guide

## Quick Setup

### For Windows Users:
```bash
# Run the automatic setup script
setup-env.bat
```

### For Linux/Mac Users:
```bash
# Run the automatic setup script
chmod +x setup-env.sh
./setup-env.sh
```

### Manual Setup:
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual values
# Windows: notepad .env
# Linux/Mac: nano .env
```

## Required Environment Variables

### 🔑 **GEMINI_API_KEY** (Required)
- Get your API key from: https://makersuite.google.com/app/apikey
- This is required for AI recipe generation

### 🗄️ **Database Configuration** (Optional)
- The default PostgreSQL settings work with the included Docker setup
- Only change if you're using a different database

### 🌐 **API URLs** (Optional)
- `REACT_APP_API_URL`: Frontend will use this to connect to the backend
- Default: `http://localhost:8000`

## Security Notes

⚠️ **Important**: 
- Never commit your actual `.env` file to git
- The `.env.example` file is safe to commit (contains no real secrets)
- Keep your Gemini API key secure and don't share it

## Troubleshooting

### Missing API Key Error:
```
Error: GEMINI_API_KEY environment variable is not set
```
**Solution**: Make sure you've created a `.env` file and added your Gemini API key.

### Database Connection Error:
```
Error: Could not connect to database
```
**Solution**: 
1. Make sure Docker is running
2. Run `docker-compose up -d` to start the database
3. Check that the database credentials in `.env` match your setup

### Frontend Can't Connect to Backend:
```
Network Error: Failed to fetch
```
**Solution**: Check that `REACT_APP_API_URL` in your `.env` file points to the correct backend URL.

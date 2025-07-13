# Deploy to Railway (Free Tier Available)

## Quick Deploy Steps:

### 1. Prepare for Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init
```

### 2. Deploy Backend
```bash
# Create backend service
railway add --service backend

# Set environment variables
railway variables set GEMINI_API_KEY=your_api_key_here
railway variables set DATABASE_URL=your_database_url_here

# Deploy
railway up --service backend
```

### 3. Deploy Frontend
```bash
# Create frontend service
railway add --service frontend

# Set environment variables
railway variables set REACT_APP_API_URL=https://your-backend-url.railway.app

# Deploy
railway up --service frontend
```

### 4. Deploy Database
```bash
# Add PostgreSQL database
railway add --service postgres

# Railway will automatically provide DATABASE_URL
```

## Alternative: Deploy to Vercel + Railway

### Frontend (Vercel)
1. Push code to GitHub
2. Connect GitHub to Vercel
3. Deploy frontend folder
4. Set environment variable: `REACT_APP_API_URL=https://your-backend.railway.app`

### Backend (Railway)
1. Connect GitHub to Railway
2. Deploy backend folder
3. Add PostgreSQL database
4. Set environment variables

## Alternative: Deploy to Heroku

### Backend
```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-app-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set GEMINI_API_KEY=your_api_key_here

# Deploy
git push heroku main
```

### Frontend
```bash
# Create frontend app
heroku create your-app-frontend

# Set environment variables
heroku config:set REACT_APP_API_URL=https://your-app-backend.herokuapp.com

# Deploy
git push heroku main
```

## Benefits of Cloud Deployment:
- ✅ 24/7 availability
- ✅ No need to keep your computer running
- ✅ Professional URLs
- ✅ SSL certificates (HTTPS)
- ✅ Better performance
- ✅ Automatic scaling

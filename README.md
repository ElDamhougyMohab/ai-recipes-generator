# 🍳 AI Recipe Generator & Meal Planner

A modern full-stack web application that leverages Google's Gemini AI to generate personalized recipes based on user-provided ingredients and dietary preferences.

## ✨ Key Features

- 🤖 **AI-Powered Recipe Generation** - Create recipes from available ingredients using Google Gemini AI
- 📱 **Modern React Frontend** - Responsive, intuitive user interface with smooth animations
- 🗄️ **Recipe Management** - Save, rate, search, and organize your recipe collection
- 📅 **Meal Planning** - Create weekly meal plans with generated recipes
- 🥗 **Dietary Support** - Accommodates dietary restrictions (gluten-free, vegetarian, vegan, etc.)
- 🔧 **REST API** - Complete FastAPI backend with OpenAPI documentation
- 🐳 **Docker Ready** - Containerized deployment for easy setup

## 🛠️ Technology Stack

- **Frontend**: React 18, Styled Components, Axios
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL 15
- **AI Integration**: Google Gemini API
- **DevOps**: Docker, Docker Compose, AWS ECS

## 🌐 Live Demo

**Production Application**: https://d173g01t5c4w0h.cloudfront.net/

*Deployed on AWS ECS with CloudFront CDN for optimized global delivery.*

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/ElDamhougyMohab/ai-recipes-generator.git
cd AI_Recipes_Generator

# Configure environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start with Docker (recommended)
docker-compose up --build
```

### 🪟 Windows Users (Easy Setup)
```batch
# Double-click or run these batch files:
start_local.bat    # Start the application
status_local.bat   # Check application status  
stop_local.bat     # Stop the application
```

### Access Points
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 💻 Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Database
```bash
docker run -d --name recipe-postgres \
  -e POSTGRES_DB=recipes_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 postgres:15
```

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Quick deployment options
- **[Advanced Deployment](docs/CLOUD_DEPLOY.md)** - AWS and cloud deployment
- **[External Access](docs/EXTERNAL_ACCESS.md)** - Network configuration
- **[Testing Suite](docs/TEST_AUTOMATION_GUIDE.md)** - Comprehensive testing
- **[API Documentation](https://d173g01t5c4w0h.cloudfront.net/docs)** - Interactive API docs

## 🗂️ Project Structure

```
AI_Recipes_Generator/
├── frontend/           # React application
├── backend/           # FastAPI application
├── database/          # Database initialization
├── terraform/         # AWS infrastructure
├── docs/             # Additional documentation
├── docker-compose.yml # Container orchestration
└── README.md         # This file
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

**Built with ❤️ using React, FastAPI, and Google Gemini AI**

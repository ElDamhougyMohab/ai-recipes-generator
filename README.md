# 🍳 AI Recipe Generator & Meal Planner

A modern web application that uses AI to generate personalized recipes based on ingredients and dietary preferences. Built with React, FastAPI, PostgreSQL, and Google's Gemini AI.

## 🚀 Features

- **AI Recipe Generation**: Input ingredients and get creative recipes powered by Gemini AI
- **Recipe Management**: Save, view, rate, and delete recipes
- **Meal Planning**: Create weekly meal plans with your favorite recipes
- **Dietary Preferences**: Support for various dietary restrictions and cuisine types
- **Modern UI**: Clean, responsive design with smooth animations
- **RESTful API**: Complete backend API with OpenAPI documentation

## 🏗️ Tech Stack

### Frontend
- **React 18** - Modern React with hooks
- **Styled Components** - CSS-in-JS styling
- **Axios** - HTTP client for API requests

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type hints

### Database
- **PostgreSQL 15** - Robust relational database

### AI Integration
- **Google Gemini API** - Advanced AI for recipe generation

### DevOps
- **Docker Compose** - Multi-container orchestration
- **Docker** - Containerization

## 📋 Prerequisites

- Docker and Docker Compose
- Google Gemini API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_Recipes_Generator
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## 📚 API Endpoints

### Recipes
- `POST /api/recipes/generate` - Generate recipes from ingredients
- `GET /api/recipes` - Get all saved recipes
- `GET /api/recipes/{id}` - Get specific recipe
- `POST /api/recipes` - Create new recipe
- `DELETE /api/recipes/{id}` - Delete recipe
- `PUT /api/recipes/{id}/rating` - Rate a recipe

### Meal Plans
- `POST /api/meal-plans` - Create meal plan
- `GET /api/meal-plans` - Get all meal plans

### Statistics
- `GET /api/stats` - Get application statistics

## 🗄️ Database Schema

### Recipes Table
```sql
- id (Primary Key)
- title (String)
- description (Text)
- instructions (Text)
- ingredients (JSON)
- prep_time (Integer, minutes)
- cook_time (Integer, minutes)
- servings (Integer)
- difficulty (String)
- rating (Float, 1-5)
- created_at (Timestamp)
- updated_at (Timestamp)
```

### Meal Plans Table
```sql
- id (Primary Key)
- name (String)
- week_start (Date)
- recipes (JSON)
- created_at (Timestamp)
```

## 🤖 AI Integration

The application uses Google's Gemini AI model to generate recipes. The AI service:

- Takes ingredients, dietary preferences, and cuisine type as input
- Generates 2-3 creative recipes with detailed instructions
- Handles parsing of AI responses with fallback mechanisms
- Provides sample recipes if AI service is unavailable

## 🎨 Frontend Architecture

### Components
- `RecipeGenerator` - Main interface for generating recipes
- `RecipeCard` - Display individual recipes with actions
- `IngredientInput` - Smart ingredient input with suggestions
- `MealPlanner` - Weekly meal planning interface

### Hooks
- `useRecipes` - Custom hook for recipe management

### Services
- `api.js` - Centralized API communication

## 🔒 Environment Variables

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## 🐳 Docker Services

- **frontend**: React development server (port 3000)
- **backend**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)

## 📝 Usage Examples

### Generate Recipes
```bash
curl -X POST "http://localhost:8000/api/recipes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "tomatoes", "garlic"],
    "dietary_preferences": ["gluten-free"],
    "cuisine_type": "Italian"
  }'
```

### Get All Recipes
```bash
curl "http://localhost:8000/api/recipes"
```

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest
```

Run frontend tests:
```bash
cd frontend
npm test
```

## 🚀 Deployment

For production deployment:

1. Set environment variables appropriately
2. Use production-ready database
3. Enable SSL/HTTPS
4. Consider using environment-specific Docker files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🐛 Known Issues

- AI generation may occasionally timeout with large ingredient lists
- Recipe parsing fallback could be improved
- Mobile responsiveness needs refinement

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini AI for recipe generation
- FastAPI for the excellent web framework
- React community for frontend tools

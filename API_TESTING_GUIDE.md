# 🧪 API Testing Guide for AI Recipes Generator

This guide shows you **5 different ways** to test these API endpoints:
- `POST /api/recipes/generate`
- `GET /api/recipes`
- `POST /api/recipes`
- `DELETE /api/recipes/{id}`
- `GET /api/stats`

## 🚀 Quick Start

### 1. Start the Application
```bash
# Start the Docker containers
docker-compose up -d

# OR use the batch file
start_app.bat
```

### 2. Verify API is Running
Visit: http://localhost:8000/health

---

## 📋 Method 1: Simple Python Script (Recommended)

**File:** `test_api_simple.py`

```bash
# Install required package
pip install requests

# Run the test script
python test_api_simple.py
```

**Features:**
- ✅ Tests all 5 endpoints
- ✅ Provides detailed output
- ✅ Handles errors gracefully
- ✅ Shows test results summary
- ✅ Works on all platforms

---

## 📋 Method 2: Use Existing Test Suite

**Files:** `docs/run_tests.bat` or `docs/run_tests.ps1`

```bash
# Windows Batch
docs\run_tests.bat

# PowerShell
.\docs\run_tests.ps1

# Direct Python
python docs/run_comprehensive_tests.py --quick
```

**Features:**
- ✅ Comprehensive test coverage
- ✅ Professional test reports
- ✅ Integration with pytest
- ✅ Coverage analysis
- ✅ Performance testing

---

## 📋 Method 3: PowerShell Script

**File:** `test_api.ps1`

```powershell
# Run the PowerShell test script
.\test_api.ps1
```

**Features:**
- ✅ Native Windows PowerShell
- ✅ Colored output
- ✅ Error handling
- ✅ JSON response formatting

---

## 📋 Method 4: cURL Commands

**File:** `test_api_curl.sh` (Linux/Mac) or use individual commands:

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Recipes
```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "pasta", "tomatoes"],
    "meal_type": "dinner",
    "dietary_preferences": [],
    "cuisine_type": "Italian"
  }'
```

### Get All Recipes
```bash
curl http://localhost:8000/api/recipes
```

### Create Recipe
```bash
curl -X POST http://localhost:8000/api/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Recipe",
    "description": "A test recipe",
    "instructions": "1. Test step",
    "ingredients": [{"name": "test", "amount": "1", "unit": "cup"}],
    "prep_time": 10,
    "cook_time": 15,
    "servings": 2,
    "difficulty": "Easy"
  }'
```

### Delete Recipe
```bash
curl -X DELETE http://localhost:8000/api/recipes/1
```

### Get Stats
```bash
curl http://localhost:8000/api/stats
```

---

## 📋 Method 5: Postman/Thunder Client

**File:** `api_tests.postman_collection.json`

1. Import the collection into Postman or Thunder Client
2. Set environment variable `base_url` to `http://localhost:8000`
3. Run the collection

**Endpoints included:**
- Health Check
- Generate Recipes
- Get All Recipes
- Create Recipe
- Delete Recipe
- Get Stats
- Get Recipe by ID

---

## 🎯 Manual Testing via Swagger UI

Visit: **http://localhost:8000/docs**

Interactive API documentation where you can:
- ✅ Test all endpoints directly
- ✅ See request/response schemas
- ✅ Try different parameters
- ✅ View example responses

---

## 🧪 Expected Responses

### POST /api/recipes/generate
```json
{
  "recipes": [
    {
      "title": "Chicken Pasta with Tomatoes",
      "description": "A delicious pasta dish...",
      "ingredients": [...],
      "instructions": "1. Cook pasta...",
      "prep_time": 15,
      "cook_time": 25,
      "servings": 4,
      "difficulty": "Easy",
      "is_temporary": true
    }
  ],
  "dietary_filtering": {...},
  "generation_info": {...}
}
```

### GET /api/recipes
```json
[
  {
    "id": 1,
    "title": "Recipe Title",
    "description": "Recipe description",
    "ingredients": [...],
    "prep_time": 15,
    "cook_time": 25,
    "servings": 4,
    "difficulty": "Easy",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  }
]
```

### POST /api/recipes
```json
{
  "id": 123,
  "title": "New Recipe",
  "description": "Recipe description",
  "ingredients": [...],
  "instructions": "1. Step one...",
  "prep_time": 10,
  "cook_time": 15,
  "servings": 4,
  "difficulty": "Easy",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00",
  "rating": null
}
```

### DELETE /api/recipes/{id}
```json
{
  "message": "Recipe deleted successfully"
}
```

### GET /api/stats
```json
{
  "total_recipes": 25,
  "average_rating": 4.2,
  "most_popular_cuisine": "Italian",
  "recent_generations": 12,
  "total_ingredients": 150,
  "difficulty_distribution": {
    "Easy": 10,
    "Medium": 8,
    "Hard": 7
  }
}
```

---

## 🛠️ Troubleshooting

### API Not Responding
```bash
# Check if containers are running
docker-compose ps

# Start the application
docker-compose up -d

# Check logs
docker-compose logs backend
```

### Python Script Issues
```bash
# Install requests
pip install requests

# Check Python version
python --version
```

### PowerShell Execution Policy
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎯 Recommended Testing Workflow

1. **Start Application**: `start_app.bat`
2. **Health Check**: Visit http://localhost:8000/health
3. **Quick Test**: `python test_api_simple.py`
4. **Comprehensive Tests**: `docs\run_tests.bat`
5. **Manual Testing**: http://localhost:8000/docs

---

## 📊 Test Coverage

All test methods cover:
- ✅ **Recipe Generation** with AI
- ✅ **CRUD Operations** (Create, Read, Delete)
- ✅ **Statistics** endpoint
- ✅ **Error Handling** and validation
- ✅ **Response Format** verification
- ✅ **Status Code** validation

Choose the method that best fits your workflow and environment!

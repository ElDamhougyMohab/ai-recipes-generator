#!/bin/bash
# cURL Test Script for AI Recipes Generator API
# Tests all main endpoints with proper JSON data

echo "🚀 Testing AI Recipes Generator API Endpoints"
echo "============================================="

BASE_URL="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_test() {
    echo -e "${YELLOW}🧪 Testing: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test 1: Health Check
print_test "Health Check"
curl -s -w "\nStatus: %{http_code}\n" "$BASE_URL/health"
echo ""

# Test 2: Generate Recipes (POST /api/recipes/generate)
print_test "Generate Recipes (POST /api/recipes/generate)"
curl -X POST "$BASE_URL/api/recipes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["chicken", "pasta", "tomatoes", "garlic"],
    "meal_type": "dinner",
    "dietary_preferences": [],
    "cuisine_type": "Italian"
  }' \
  -s -w "\nStatus: %{http_code}\n"
echo ""

# Test 3: Get All Recipes (GET /api/recipes)
print_test "Get All Recipes (GET /api/recipes)"
curl -X GET "$BASE_URL/api/recipes" \
  -H "Accept: application/json" \
  -s -w "\nStatus: %{http_code}\n"
echo ""

# Test 4: Create Recipe (POST /api/recipes)
print_test "Create Recipe (POST /api/recipes)"
RECIPE_RESPONSE=$(curl -X POST "$BASE_URL/api/recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Spaghetti Carbonara",
    "description": "A classic Italian pasta dish with eggs, cheese, and pancetta",
    "instructions": "1. Cook spaghetti according to package directions.\n2. Mix eggs and cheese in a bowl.\n3. Cook pancetta until crispy.\n4. Combine all ingredients while pasta is hot.",
    "ingredients": [
      {"name": "spaghetti", "amount": "400", "unit": "g"},
      {"name": "eggs", "amount": "4", "unit": "large"},
      {"name": "parmesan cheese", "amount": "100", "unit": "g"},
      {"name": "pancetta", "amount": "150", "unit": "g"}
    ],
    "prep_time": 10,
    "cook_time": 15,
    "servings": 4,
    "difficulty": "Medium",
    "cuisine_type": "Italian"
  }' \
  -s -w "\nStatus: %{http_code}\n")

echo "$RECIPE_RESPONSE"

# Extract recipe ID for deletion test (requires jq)
if command -v jq &> /dev/null; then
    RECIPE_ID=$(echo "$RECIPE_RESPONSE" | jq -r '.id // empty')
    if [ ! -z "$RECIPE_ID" ] && [ "$RECIPE_ID" != "null" ]; then
        print_success "Created recipe with ID: $RECIPE_ID"
        
        # Test 5: Delete Recipe (DELETE /api/recipes/{id})
        print_test "Delete Recipe (DELETE /api/recipes/$RECIPE_ID)"
        curl -X DELETE "$BASE_URL/api/recipes/$RECIPE_ID" \
          -s -w "\nStatus: %{http_code}\n"
        echo ""
    else
        print_error "Could not extract recipe ID for deletion test"
        echo ""
        
        # Fallback: Try deleting a recipe with ID 1
        print_test "Delete Recipe (DELETE /api/recipes/1) - Fallback"
        curl -X DELETE "$BASE_URL/api/recipes/1" \
          -s -w "\nStatus: %{http_code}\n"
        echo ""
    fi
else
    print_error "jq not found. Skipping automatic recipe deletion test."
    echo "To test deletion manually, use: curl -X DELETE $BASE_URL/api/recipes/{id}"
    echo ""
fi

# Test 6: Get Stats (GET /api/stats)
print_test "Get Stats (GET /api/stats)"
curl -X GET "$BASE_URL/api/stats" \
  -H "Accept: application/json" \
  -s -w "\nStatus: %{http_code}\n"
echo ""

# Additional Tests

# Test 7: Get Recipe by ID (if we have an ID)
if [ ! -z "$RECIPE_ID" ] && [ "$RECIPE_ID" != "null" ]; then
    print_test "Get Recipe by ID (GET /api/recipes/$RECIPE_ID)"
    curl -X GET "$BASE_URL/api/recipes/$RECIPE_ID" \
      -H "Accept: application/json" \
      -s -w "\nStatus: %{http_code}\n"
    echo ""
fi

# Test 8: Generate with Dietary Preferences
print_test "Generate with Dietary Preferences"
curl -X POST "$BASE_URL/api/recipes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["tofu", "vegetables", "rice"],
    "meal_type": "dinner",
    "dietary_preferences": ["vegetarian", "gluten-free"],
    "cuisine_type": "Asian"
  }' \
  -s -w "\nStatus: %{http_code}\n"
echo ""

# Test 9: Error Cases
print_test "Invalid Recipe Creation (missing required fields)"
curl -X POST "$BASE_URL/api/recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Missing title and ingredients"
  }' \
  -s -w "\nStatus: %{http_code}\n"
echo ""

print_test "Invalid Recipe Generation (missing ingredients)"
curl -X POST "$BASE_URL/api/recipes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "meal_type": "dinner"
  }' \
  -s -w "\nStatus: %{http_code}\n"
echo ""

echo "============================================="
echo "🏁 API Testing Complete!"
echo ""
echo "Expected Status Codes:"
echo "  200 = Success"
echo "  404 = Not Found (for delete of non-existent recipe)"
echo "  422 = Validation Error (for invalid data)"
echo ""
echo "Notes:"
echo "  - Make sure the API server is running: docker-compose up -d"
echo "  - Install jq for better JSON parsing: sudo apt-get install jq"
echo "  - Check the API documentation at: http://localhost:8000/docs"

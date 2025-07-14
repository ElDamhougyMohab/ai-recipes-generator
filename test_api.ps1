# PowerShell API Test Script for AI Recipes Generator
# Tests all main endpoints with proper JSON data

Write-Host "🚀 Testing AI Recipes Generator API Endpoints" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$BaseUrl = "http://localhost:8000"

# Function to make HTTP requests and display results
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Url,
        [string]$Body = $null,
        [string]$Description
    )
    
    Write-Host "🧪 Testing: $Description" -ForegroundColor Yellow
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
            "Accept" = "application/json"
        }
        
        if ($Body) {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $Body -Headers $headers -ErrorAction Stop
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Headers $headers -ErrorAction Stop
        }
        
        Write-Host "✅ Success!" -ForegroundColor Green
        Write-Host "Response:" -ForegroundColor White
        $response | ConvertTo-Json -Depth 3 | Write-Host
        Write-Host ""
        
        return $response
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
        Write-Host ""
        return $null
    }
}

# Test 1: Health Check
$healthResponse = Test-Endpoint -Method "GET" -Url "$BaseUrl/health" -Description "Health Check"

if (-not $healthResponse) {
    Write-Host "❌ Cannot connect to API. Make sure the server is running on http://localhost:8000" -ForegroundColor Red
    Write-Host "Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Test 2: Generate Recipes (POST /api/recipes/generate)
$generateBody = @{
    ingredients = @("chicken", "pasta", "tomatoes", "garlic")
    meal_type = "dinner"
    dietary_preferences = @()
    cuisine_type = "Italian"
} | ConvertTo-Json -Depth 3

$generateResponse = Test-Endpoint -Method "POST" -Url "$BaseUrl/api/recipes/generate" -Body $generateBody -Description "Generate Recipes (POST /api/recipes/generate)"

# Test 3: Get All Recipes (GET /api/recipes)
$recipesResponse = Test-Endpoint -Method "GET" -Url "$BaseUrl/api/recipes" -Description "Get All Recipes (GET /api/recipes)"

# Test 4: Create Recipe (POST /api/recipes)
$createRecipeBody = @{
    title = "Test Spaghetti Carbonara"
    description = "A classic Italian pasta dish with eggs, cheese, and pancetta"
    instructions = "1. Cook spaghetti according to package directions.`n2. Mix eggs and cheese in a bowl.`n3. Cook pancetta until crispy.`n4. Combine all ingredients while pasta is hot."
    ingredients = @(
        @{ name = "spaghetti"; amount = "400"; unit = "g" }
        @{ name = "eggs"; amount = "4"; unit = "large" }
        @{ name = "parmesan cheese"; amount = "100"; unit = "g" }
        @{ name = "pancetta"; amount = "150"; unit = "g" }
    )
    prep_time = 10
    cook_time = 15
    servings = 4
    difficulty = "Medium"
    cuisine_type = "Italian"
} | ConvertTo-Json -Depth 3

$createResponse = Test-Endpoint -Method "POST" -Url "$BaseUrl/api/recipes" -Body $createRecipeBody -Description "Create Recipe (POST /api/recipes)"

# Get recipe ID for deletion test
$recipeId = $null
if ($createResponse -and $createResponse.id) {
    $recipeId = $createResponse.id
    Write-Host "✅ Created recipe with ID: $recipeId" -ForegroundColor Green
}

# Test 5: Get Stats (GET /api/stats)
$statsResponse = Test-Endpoint -Method "GET" -Url "$BaseUrl/api/stats" -Description "Get Stats (GET /api/stats)"

# Test 6: Delete Recipe (DELETE /api/recipes/{id})
if ($recipeId) {
    try {
        Write-Host "🧪 Testing: Delete Recipe (DELETE /api/recipes/$recipeId)" -ForegroundColor Yellow
        $deleteResponse = Invoke-RestMethod -Uri "$BaseUrl/api/recipes/$recipeId" -Method "DELETE" -ErrorAction Stop
        Write-Host "✅ Recipe deleted successfully!" -ForegroundColor Green
        Write-Host ""
    }
    catch {
        Write-Host "❌ Delete failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
        Write-Host ""
    }
} else {
    Write-Host "⚠️ Skipping delete test - no recipe ID available" -ForegroundColor Yellow
}

# Additional Tests

# Test 7: Generate with Dietary Preferences
$dietaryBody = @{
    ingredients = @("tofu", "vegetables", "rice")
    meal_type = "dinner"
    dietary_preferences = @("vegetarian", "gluten-free")
    cuisine_type = "Asian"
} | ConvertTo-Json -Depth 3

$dietaryResponse = Test-Endpoint -Method "POST" -Url "$BaseUrl/api/recipes/generate" -Body $dietaryBody -Description "Generate with Dietary Preferences"

# Test 8: Error Cases
Write-Host "🧪 Testing Error Cases" -ForegroundColor Yellow

# Invalid recipe creation
$invalidBody = @{
    description = "Missing title and ingredients"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "$BaseUrl/api/recipes" -Method "POST" -Body $invalidBody -Headers @{"Content-Type"="application/json"} -ErrorAction Stop
    Write-Host "❌ Expected validation error but got success" -ForegroundColor Red
}
catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "✅ Validation error correctly returned (422)" -ForegroundColor Green
    } else {
        Write-Host "❌ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Invalid generation
$invalidGenBody = @{
    meal_type = "dinner"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "$BaseUrl/api/recipes/generate" -Method "POST" -Body $invalidGenBody -Headers @{"Content-Type"="application/json"} -ErrorAction Stop
    Write-Host "❌ Expected validation error but got success" -ForegroundColor Red
}
catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "✅ Generation validation error correctly returned (422)" -ForegroundColor Green
    } else {
        Write-Host "❌ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "🏁 API Testing Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary of tested endpoints:" -ForegroundColor White
Write-Host "  ✓ POST /api/recipes/generate" -ForegroundColor Green
Write-Host "  ✓ GET /api/recipes" -ForegroundColor Green
Write-Host "  ✓ POST /api/recipes" -ForegroundColor Green
Write-Host "  ✓ DELETE /api/recipes/{id}" -ForegroundColor Green
Write-Host "  ✓ GET /api/stats" -ForegroundColor Green
Write-Host ""
Write-Host "Notes:" -ForegroundColor Yellow
Write-Host "  - API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - API Status: http://localhost:8000/health" -ForegroundColor White
Write-Host "  - Start server: docker-compose up -d" -ForegroundColor White

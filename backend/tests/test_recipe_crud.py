"""
Comprehensive tests for recipe CRUD operations
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestRecipeCRUD:
    """Test cases for recipe CRUD operations"""

    def test_create_recipe_success(self, client: TestClient):
        """Test successful recipe creation"""
        recipe_data = {
            "title": "Test Chicken Pasta",
            "description": "A delicious test recipe",
            "instructions": "1. Cook pasta. 2. Add chicken. 3. Serve hot.",
            "ingredients": [
                {"name": "chicken breast", "amount": "2", "unit": "pieces", "notes": "boneless"},
                {"name": "pasta", "amount": "200", "unit": "g", "notes": None}
            ],
            "prep_time": 15,
            "cook_time": 25,
            "servings": 4,
            "difficulty": "Easy"
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == recipe_data["title"]
        assert data["description"] == recipe_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_create_recipe_minimal_data(self, client: TestClient):
        """Test recipe creation with minimal required data"""
        recipe_data = {
            "title": "Minimal Recipe",
            "instructions": "Cook everything together.",
            "ingredients": [
                {"name": "ingredient1", "amount": None, "unit": None, "notes": None}
            ]
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200

    def test_create_recipe_missing_title(self, client: TestClient):
        """Test recipe creation fails without title"""
        recipe_data = {
            "instructions": "Cook everything together.",
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup", "notes": None}
            ]
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_missing_instructions(self, client: TestClient):
        """Test recipe creation fails without instructions"""
        recipe_data = {
            "title": "Recipe Without Instructions",
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup", "notes": None}
            ]
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_missing_ingredients(self, client: TestClient):
        """Test recipe creation fails without ingredients"""
        recipe_data = {
            "title": "Recipe Without Ingredients",
            "instructions": "Cook everything together.",
            "ingredients": []
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_invalid_title_length(self, client: TestClient):
        """Test recipe creation with invalid title length"""
        # Title too short
        recipe_data = {
            "title": "AB",  # Less than 3 characters
            "instructions": "Cook everything together.",
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup", "notes": None}
            ]
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

        # Title too long
        recipe_data["title"] = "A" * 201  # More than 200 characters
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_invalid_instructions_length(self, client: TestClient):
        """Test recipe creation with invalid instructions length"""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Short",  # Less than 10 characters
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup", "notes": None}
            ]
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_invalid_difficulty(self, client: TestClient):
        """Test recipe creation with invalid difficulty"""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook everything together properly.",
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup", "notes": None}
            ],
            "difficulty": "Impossible"  # Invalid difficulty
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_invalid_time_values(self, client: TestClient):
        """Test recipe creation with invalid time values"""
        # Negative prep time
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook everything together properly.",
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup", "notes": None}
            ],
            "prep_time": -5
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

        # Excessive cook time
        recipe_data["prep_time"] = 15
        recipe_data["cook_time"] = 2000  # More than 1440 minutes (24 hours)
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_invalid_servings(self, client: TestClient):
        """Test recipe creation with invalid servings"""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Cook everything together properly.",
            "ingredients": [
                {"name": "ingredient1", "amount": "1", "unit": "cup", "notes": None}
            ],
            "servings": 0  # Invalid servings
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

        recipe_data["servings"] = 25  # More than 20
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_too_many_ingredients(self, client: TestClient):
        """Test recipe creation with too many ingredients"""
        ingredients = [
            {"name": f"ingredient_{i}", "amount": "1", "unit": "cup", "notes": None}
            for i in range(51)  # More than 50 ingredients
        ]

        recipe_data = {
            "title": "Recipe With Too Many Ingredients",
            "instructions": "Cook everything together properly.",
            "ingredients": ingredients
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 422

    def test_create_recipe_large_payload(self, client: TestClient):
        """Test recipe creation with maximum allowed payload"""
        ingredients = [
            {"name": f"ingredient_{i}", "amount": "1", "unit": "cup", "notes": "notes"}
            for i in range(50)  # Maximum ingredients
        ]

        recipe_data = {
            "title": "A" * 200,  # Maximum title length
            "description": "B" * 1000,  # Large description
            "instructions": "C" * 5000,  # Large instructions
            "ingredients": ingredients,
            "prep_time": 600,  # Maximum prep time
            "cook_time": 1440,  # Maximum cook time
            "servings": 20,  # Maximum servings
            "difficulty": "Expert"
        }

        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200

    def test_get_recipes_pagination(self, client: TestClient):
        """Test recipe retrieval with pagination"""
        response = client.get("/api/recipes?page=1&page_size=5")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert "per_page" in data
        assert "has_next" in data
        assert "has_prev" in data

    def test_get_recipes_invalid_pagination(self, client: TestClient):
        """Test recipe retrieval with invalid pagination parameters"""
        # Invalid page number
        response = client.get("/api/recipes?page=0")
        assert response.status_code == 422

        # Invalid page size
        response = client.get("/api/recipes?page_size=200")
        assert response.status_code == 422

    def test_get_recipe_by_id_success(self, client: TestClient, sample_recipe_data):
        """Test successful recipe retrieval by ID"""
        # First create a recipe
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_response.status_code == 200
        recipe_id = create_response.json()["id"]

        # Then retrieve it
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == recipe_id
        assert data["title"] == sample_recipe_data["title"]

    def test_get_recipe_by_id_not_found(self, client: TestClient):
        """Test recipe retrieval with non-existent ID"""
        response = client.get("/api/recipes/99999")
        assert response.status_code == 404

    def test_get_recipe_by_id_invalid_id(self, client: TestClient):
        """Test recipe retrieval with invalid ID format"""
        response = client.get("/api/recipes/invalid")
        assert response.status_code == 422

    def test_delete_recipe_success(self, client: TestClient, sample_recipe_data):
        """Test successful recipe deletion"""
        # First create a recipe
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_response.status_code == 200
        recipe_id = create_response.json()["id"]

        # Then delete it
        response = client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f"/api/recipes/{recipe_id}")
        assert get_response.status_code == 404

    def test_delete_recipe_not_found(self, client: TestClient):
        """Test recipe deletion with non-existent ID"""
        response = client.delete("/api/recipes/99999")
        assert response.status_code == 404

    def test_rate_recipe_success(self, client: TestClient, sample_recipe_data):
        """Test successful recipe rating"""
        # First create a recipe
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_response.status_code == 200
        recipe_id = create_response.json()["id"]

        # Then rate it
        response = client.put(f"/api/recipes/{recipe_id}/rating?rating=4.5")
        assert response.status_code == 200

        data = response.json()
        assert data["rating"] == 4.5

    def test_rate_recipe_invalid_rating(self, client: TestClient, sample_recipe_data):
        """Test recipe rating with invalid rating values"""
        # First create a recipe
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_response.status_code == 200
        recipe_id = create_response.json()["id"]

        # Test rating too low
        response = client.put(f"/api/recipes/{recipe_id}/rating?rating=0.5")
        assert response.status_code == 422

        # Test rating too high
        response = client.put(f"/api/recipes/{recipe_id}/rating?rating=5.5")
        assert response.status_code == 422

    def test_search_recipes_by_query(self, client: TestClient):
        """Test recipe search with query parameter"""
        response = client.get("/api/recipes/search?q=pasta")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_search_recipes_by_difficulty(self, client: TestClient):
        """Test recipe search by difficulty"""
        response = client.get("/api/recipes/search?difficulty=Easy")
        assert response.status_code == 200

    def test_search_recipes_by_rating(self, client: TestClient):
        """Test recipe search by minimum rating"""
        response = client.get("/api/recipes/search?min_rating=4.0")
        assert response.status_code == 200

    def test_search_recipes_by_time_constraints(self, client: TestClient):
        """Test recipe search by time constraints"""
        response = client.get("/api/recipes/search?max_prep_time=30&max_cook_time=60")
        assert response.status_code == 200

    def test_search_recipes_invalid_parameters(self, client: TestClient):
        """Test recipe search with invalid parameters"""
        # Invalid difficulty
        response = client.get("/api/recipes/search?difficulty=Impossible")
        assert response.status_code == 422

        # Invalid rating range
        response = client.get("/api/recipes/search?min_rating=6.0")
        assert response.status_code == 422

        # Invalid time values
        response = client.get("/api/recipes/search?max_prep_time=-5")
        assert response.status_code == 422

    def test_get_stats_endpoint(self, client: TestClient):
        """Test the statistics endpoint"""
        response = client.get("/api/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_recipes" in data
        assert "average_rating" in data
        assert isinstance(data["total_recipes"], int)
        assert isinstance(data["average_rating"], (int, float))

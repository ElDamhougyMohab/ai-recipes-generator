"""
Tests for recipe API endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestRecipeAPI:
    """Test cases for recipe CRUD operations"""

    def test_create_recipe_success(self, client: TestClient, sample_recipe_data):
        """Test successful recipe creation"""
        response = client.post("/api/recipes", json=sample_recipe_data)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["title"] == sample_recipe_data["title"]
        assert data["description"] == sample_recipe_data["description"]
        assert data["difficulty"] == sample_recipe_data["difficulty"]
        assert data["prep_time"] == sample_recipe_data["prep_time"]
        assert data["cook_time"] == sample_recipe_data["cook_time"]
        assert data["servings"] == sample_recipe_data["servings"]
        assert len(data["ingredients"]) == len(sample_recipe_data["ingredients"])
        assert "created_at" in data
        assert "updated_at" in data
        assert data["rating"] is None

    def test_create_recipe_validation_errors(self, client: TestClient):
        """Test recipe creation with validation errors"""
        # Test missing title
        invalid_data = {
            "description": "Test description",
            "instructions": "Test instructions",
            "ingredients": [{"name": "test", "amount": "1", "unit": "cup"}],
        }

        response = client.post("/api/recipes", json=invalid_data)
        assert response.status_code == 422

        # Test empty ingredients
        invalid_data_empty_ingredients = {
            "title": "Test Recipe",
            "description": "Test description",
            "instructions": "Test instructions",
            "ingredients": [],
        }

        response = client.post("/api/recipes", json=invalid_data_empty_ingredients)
        assert response.status_code == 422

    def test_create_recipe_invalid_difficulty(
        self, client: TestClient, sample_recipe_data
    ):
        """Test recipe creation with invalid difficulty"""
        sample_recipe_data["difficulty"] = "Invalid"

        response = client.post("/api/recipes", json=sample_recipe_data)
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data
        assert "Difficulty must be one of" in str(error_data["detail"])

    def test_create_recipe_invalid_ingredient_format(
        self, client: TestClient, sample_recipe_data
    ):
        """Test recipe creation with invalid ingredient format"""
        sample_recipe_data["ingredients"] = [
            {"name": "", "amount": "1", "unit": "cup"}  # Empty name
        ]

        response = client.post("/api/recipes", json=sample_recipe_data)
        assert response.status_code == 422

    def test_create_recipe_unicode_ingredients(
        self, client: TestClient, sample_recipe_data
    ):
        """Test recipe creation with unicode characters"""
        sample_recipe_data["ingredients"] = [
            {
                "name": "Jalapeño peppers",
                "amount": "2",
                "unit": "pieces",
                "notes": "fresh",
            },
            {
                "name": "Café au lait",
                "amount": "1",
                "unit": "cup",
                "notes": "for breakfast",
            },
            {"name": "Naïve herbs", "amount": "1", "unit": "tbsp", "notes": "mixed"},
        ]

        response = client.post("/api/recipes", json=sample_recipe_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["ingredients"]) == 3
        assert data["ingredients"][0]["name"] == "Jalapeño peppers"

    def test_get_recipe_success(self, client: TestClient, created_recipe):
        """Test retrieving existing recipe"""
        recipe_id = created_recipe["id"]

        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == recipe_id
        assert data["title"] == created_recipe["title"]

    def test_get_recipe_not_found(self, client: TestClient):
        """Test 404 for non-existent recipe"""
        response = client.get("/api/recipes/99999")
        assert response.status_code == 404

        error_data = response.json()
        assert "detail" in error_data
        assert "Recipe not found" in error_data["detail"]

    def test_get_recipe_invalid_id(self, client: TestClient):
        """Test invalid recipe ID format"""
        response = client.get("/api/recipes/invalid")
        assert response.status_code == 422

    def test_delete_recipe_success(self, client: TestClient, created_recipe):
        """Test successful recipe deletion"""
        recipe_id = created_recipe["id"]

        # Delete the recipe
        response = client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200

        # Verify it's deleted
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 404

    def test_delete_recipe_not_found(self, client: TestClient):
        """Test 404 for deleting non-existent recipe"""
        response = client.delete("/api/recipes/99999")
        assert response.status_code == 404

        error_data = response.json()
        assert "detail" in error_data
        assert "Recipe not found" in error_data["detail"]

    def test_rate_recipe_success(self, client: TestClient, created_recipe):
        """Test rating a recipe"""
        recipe_id = created_recipe["id"]

        # Rate the recipe
        response = client.put(
            f"/api/recipes/{recipe_id}/rating", params={"rating": 4.5}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["rating"] == 4.5

        # Verify rating is saved
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 4.5

    def test_rate_recipe_invalid_rating(self, client: TestClient, created_recipe):
        """Test rating with invalid values"""
        recipe_id = created_recipe["id"]

        # Test rating too high
        response = client.put(
            f"/api/recipes/{recipe_id}/rating", params={"rating": 6.0}
        )
        assert response.status_code == 422

        # Test rating too low
        response = client.put(
            f"/api/recipes/{recipe_id}/rating", params={"rating": -1.0}
        )
        assert response.status_code == 422

    def test_create_recipe_large_payload(self, client: TestClient):
        """Test creating recipe with large payload"""
        large_recipe = {
            "title": "A" * 200,  # Max length
            "description": "B" * 1000,  # Max length
            "instructions": "C" * 5000,  # Large instructions
            "ingredients": [
                {
                    "name": f"ingredient_{i}",
                    "amount": str(i),
                    "unit": "cup",
                    "notes": f"notes_{i}",
                }
                for i in range(50)  # Max ingredients
            ],
            "prep_time": 600,  # Max prep time
            "cook_time": 1440,  # Max cook time
            "servings": 20,  # Max servings
            "difficulty": "Expert",
        }

        response = client.post("/api/recipes", json=large_recipe)
        assert response.status_code == 200

        data = response.json()
        assert len(data["ingredients"]) == 50
        assert data["prep_time"] == 600
        assert data["cook_time"] == 1440

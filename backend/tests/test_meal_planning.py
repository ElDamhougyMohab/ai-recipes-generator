"""
Comprehensive tests for meal planning functionality
"""

import pytest
from fastapi.testclient import TestClient


class TestMealPlanning:
    """Test cases for meal planning operations"""

    def test_create_meal_plan_success(self, client: TestClient, sample_recipe_data):
        """Test successful meal plan creation"""
        # First create some recipes
        recipe_ids = []
        for i in range(3):
            recipe_data = sample_recipe_data.copy()
            recipe_data["title"] = f"Test Recipe {i+1}"
            create_response = client.post("/api/recipes", json=recipe_data)
            assert create_response.status_code == 200
            recipe_ids.append(create_response.json()["id"])

        # Create meal plan
        meal_plan_data = {
            "name": "Weekly Meal Plan",
            "recipes": {
                "monday": [recipe_ids[0]],
                "tuesday": [recipe_ids[1]],
                "wednesday": [recipe_ids[0], recipe_ids[2]]
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == meal_plan_data["name"]
        assert "id" in data
        assert "created_at" in data
        assert data["recipes"] == meal_plan_data["recipes"]

    def test_create_meal_plan_missing_name(self, client: TestClient):
        """Test meal plan creation fails without name"""
        meal_plan_data = {
            "recipes": {
                "monday": [1]
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_create_meal_plan_short_name(self, client: TestClient):
        """Test meal plan creation with name too short"""
        meal_plan_data = {
            "name": "AB",  # Less than 3 characters
            "recipes": {
                "monday": [1]
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_create_meal_plan_long_name(self, client: TestClient):
        """Test meal plan creation with name too long"""
        meal_plan_data = {
            "name": "A" * 101,  # More than 100 characters
            "recipes": {
                "monday": [1]
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_create_meal_plan_empty_recipes(self, client: TestClient):
        """Test meal plan creation with empty recipes"""
        meal_plan_data = {
            "name": "Empty Meal Plan",
            "recipes": {}
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_create_meal_plan_invalid_day(self, client: TestClient):
        """Test meal plan creation with invalid day names"""
        meal_plan_data = {
            "name": "Invalid Day Plan",
            "recipes": {
                "invalidday": [1],
                "monday": [2]
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_create_meal_plan_invalid_recipe_id(self, client: TestClient):
        """Test meal plan creation with invalid recipe IDs"""
        meal_plan_data = {
            "name": "Invalid Recipe Plan",
            "recipes": {
                "monday": [0],  # Invalid recipe ID (must be positive)
                "tuesday": [-1]  # Invalid recipe ID
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_create_meal_plan_too_many_recipes_per_day(self, client: TestClient):
        """Test meal plan creation with too many recipes per day"""
        recipe_ids = list(range(1, 12))  # 11 recipe IDs (more than max 10)
        
        meal_plan_data = {
            "name": "Overloaded Day Plan",
            "recipes": {
                "monday": recipe_ids
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_create_meal_plan_maximum_recipes_per_day(self, client: TestClient):
        """Test meal plan creation with maximum allowed recipes per day"""
        # First create 10 recipes
        recipe_ids = []
        for i in range(10):
            recipe_data = {
                "title": f"Recipe {i+1}",
                "instructions": "Cook properly.",
                "ingredients": [
                    {"name": f"ingredient_{i}", "amount": "1", "unit": "cup", "notes": None}
                ]
            }
            create_response = client.post("/api/recipes", json=recipe_data)
            assert create_response.status_code == 200
            recipe_ids.append(create_response.json()["id"])

        meal_plan_data = {
            "name": "Maximum Recipes Plan",
            "recipes": {
                "monday": recipe_ids  # Exactly 10 recipes
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 200

    def test_get_meal_plans_pagination(self, client: TestClient):
        """Test meal plan retrieval with pagination"""
        response = client.get("/api/meal-plans?page=1&page_size=5")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert "per_page" in data
        assert "has_next" in data
        assert "has_prev" in data

    def test_get_meal_plans_invalid_pagination(self, client: TestClient):
        """Test meal plan retrieval with invalid pagination"""
        # Invalid page number
        response = client.get("/api/meal-plans?page=0")
        assert response.status_code == 422

        # Invalid page size (enforced max is 10)
        response = client.get("/api/meal-plans?page_size=15")
        assert response.status_code == 200
        data = response.json()
        assert data["per_page"] == 10  # Should be capped at 10

    def test_get_meal_plan_by_id_success(self, client: TestClient, sample_recipe_data):
        """Test successful meal plan retrieval by ID"""
        # First create a recipe
        create_recipe_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_recipe_response.status_code == 200
        recipe_id = create_recipe_response.json()["id"]

        # Create meal plan
        meal_plan_data = {
            "name": "Test Meal Plan",
            "recipes": {
                "monday": [recipe_id]
            }
        }

        create_response = client.post("/api/meal-plans", json=meal_plan_data)
        assert create_response.status_code == 200
        meal_plan_id = create_response.json()["id"]

        # Retrieve meal plan
        response = client.get(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == meal_plan_id
        assert data["name"] == meal_plan_data["name"]

    def test_get_meal_plan_by_id_not_found(self, client: TestClient):
        """Test meal plan retrieval with non-existent ID"""
        response = client.get("/api/meal-plans/99999")
        assert response.status_code == 404

    def test_get_meal_plan_by_id_invalid_id(self, client: TestClient):
        """Test meal plan retrieval with invalid ID format"""
        response = client.get("/api/meal-plans/invalid")
        assert response.status_code == 422

    def test_delete_meal_plan_success(self, client: TestClient, sample_recipe_data):
        """Test successful meal plan deletion"""
        # First create a recipe
        create_recipe_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_recipe_response.status_code == 200
        recipe_id = create_recipe_response.json()["id"]

        # Create meal plan
        meal_plan_data = {
            "name": "Test Meal Plan",
            "recipes": {
                "monday": [recipe_id]
            }
        }

        create_response = client.post("/api/meal-plans", json=meal_plan_data)
        assert create_response.status_code == 200
        meal_plan_id = create_response.json()["id"]

        # Delete meal plan
        response = client.delete(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f"/api/meal-plans/{meal_plan_id}")
        assert get_response.status_code == 404

    def test_delete_meal_plan_not_found(self, client: TestClient):
        """Test meal plan deletion with non-existent ID"""
        response = client.delete("/api/meal-plans/99999")
        assert response.status_code == 404

    def test_meal_plan_with_all_days(self, client: TestClient, sample_recipe_data):
        """Test meal plan creation with all days of the week"""
        # Create recipes for each day
        recipe_ids = []
        for i in range(7):
            recipe_data = sample_recipe_data.copy()
            recipe_data["title"] = f"Day {i+1} Recipe"
            create_response = client.post("/api/recipes", json=recipe_data)
            assert create_response.status_code == 200
            recipe_ids.append(create_response.json()["id"])

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        meal_plan_data = {
            "name": "Full Week Plan",
            "recipes": {day: [recipe_ids[i]] for i, day in enumerate(days)}
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["recipes"]) == 7

    def test_meal_plan_case_insensitive_days(self, client: TestClient, sample_recipe_data):
        """Test meal plan with case variations in day names"""
        # Create a recipe
        create_recipe_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_recipe_response.status_code == 200
        recipe_id = create_recipe_response.json()["id"]

        meal_plan_data = {
            "name": "Case Test Plan",
            "recipes": {
                "MONDAY": [recipe_id],  # Uppercase should be rejected
                "Tuesday": [recipe_id]  # Title case should be rejected
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_meal_plan_duplicate_recipes_same_day(self, client: TestClient, sample_recipe_data):
        """Test meal plan with duplicate recipes on the same day"""
        # Create a recipe
        create_recipe_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_recipe_response.status_code == 200
        recipe_id = create_recipe_response.json()["id"]

        meal_plan_data = {
            "name": "Duplicate Recipe Plan",
            "recipes": {
                "monday": [recipe_id, recipe_id]  # Same recipe twice
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 200  # Should be allowed

    def test_meal_plan_with_nonexistent_recipe(self, client: TestClient):
        """Test meal plan creation with non-existent recipe ID"""
        meal_plan_data = {
            "name": "Invalid Recipe Plan",
            "recipes": {
                "monday": [99999]  # Non-existent recipe ID
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        # This might succeed at creation but fail when retrieving
        # The actual behavior depends on foreign key constraints
        assert response.status_code in [200, 422, 400]

    def test_meal_plan_recipes_not_list(self, client: TestClient):
        """Test meal plan creation with non-list recipe values"""
        meal_plan_data = {
            "name": "Invalid Format Plan",
            "recipes": {
                "monday": 1  # Should be a list, not an integer
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 422

    def test_meal_plan_comprehensive_validation(self, client: TestClient, sample_recipe_data):
        """Test comprehensive meal plan validation"""
        # Create multiple recipes
        recipe_ids = []
        for i in range(5):
            recipe_data = sample_recipe_data.copy()
            recipe_data["title"] = f"Validation Recipe {i+1}"
            create_response = client.post("/api/recipes", json=recipe_data)
            assert create_response.status_code == 200
            recipe_ids.append(create_response.json()["id"])

        # Valid meal plan
        meal_plan_data = {
            "name": "Comprehensive Validation Plan",
            "recipes": {
                "monday": [recipe_ids[0], recipe_ids[1]],
                "wednesday": [recipe_ids[2]],
                "friday": [recipe_ids[3], recipe_ids[4]],
                "sunday": [recipe_ids[0]]  # Reuse recipe from Monday
            }
        }

        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == meal_plan_data["name"]
        assert len(data["recipes"]) == 4  # 4 days with recipes
        assert len(data["recipes"]["monday"]) == 2
        assert len(data["recipes"]["friday"]) == 2

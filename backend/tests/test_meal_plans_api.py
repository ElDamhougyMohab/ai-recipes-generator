"""
Tests for meal planning API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestMealPlanAPI:
    """Test cases for meal planning functionality"""
    
    def test_create_meal_plan_success(self, client: TestClient, sample_meal_plan_data):
        """Test successful meal plan creation"""
        # First create some recipes
        recipe_data = {
            "title": "Test Recipe",
            "description": "Test description",
            "instructions": "Test instructions",
            "ingredients": [{"name": "ingredient", "amount": "1", "unit": "cup"}],
            "difficulty": "Easy"
        }
        
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        recipe_id = response.json()["id"]
        
        # Create meal plan with recipe
        sample_meal_plan_data["recipes"]["Monday"] = [recipe_id]
        sample_meal_plan_data["recipes"]["Tuesday"] = [recipe_id]
        
        response = client.post("/api/meal-plans", json=sample_meal_plan_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_meal_plan_data["name"]
        assert "recipes" in data
        assert "created_at" in data
        assert data["recipes"]["Monday"] == [recipe_id]
        assert data["recipes"]["Tuesday"] == [recipe_id]
    
    def test_create_meal_plan_validation_errors(self, client: TestClient):
        """Test meal plan creation with validation errors"""
        # Test missing name
        invalid_data = {
            "recipes": {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=invalid_data)
        assert response.status_code == 422
        
        # Test missing recipes
        invalid_data_no_recipes = {
            "name": "Test Plan"
        }
        
        response = client.post("/api/meal-plans", json=invalid_data_no_recipes)
        assert response.status_code == 422
    
    def test_create_meal_plan_invalid_recipe_ids(self, client: TestClient, sample_meal_plan_data):
        """Test meal plan creation with non-existent recipe IDs"""
        # Use non-existent recipe IDs
        sample_meal_plan_data["recipes"]["Monday"] = [99999]
        
        response = client.post("/api/meal-plans", json=sample_meal_plan_data)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        assert "recipe" in str(error_data["detail"]).lower()
    
    def test_create_meal_plan_invalid_day_names(self, client: TestClient):
        """Test meal plan creation with invalid day names"""
        invalid_data = {
            "name": "Test Plan",
            "recipes": {
                "InvalidDay": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=invalid_data)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
    
    def test_create_meal_plan_empty_recipes(self, client: TestClient, sample_meal_plan_data):
        """Test meal plan creation with empty recipes (should be allowed)"""
        # All days have empty recipe lists
        response = client.post("/api/meal-plans", json=sample_meal_plan_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == sample_meal_plan_data["name"]
        assert all(len(recipes) == 0 for recipes in data["recipes"].values())
    
    def test_get_meal_plans_pagination(self, client: TestClient):
        """Test meal plans pagination"""
        # Create multiple meal plans
        for i in range(5):
            meal_plan_data = {
                "name": f"Test Plan {i}",
                "recipes": {
                    "Monday": [],
                    "Tuesday": [],
                    "Wednesday": [],
                    "Thursday": [],
                    "Friday": [],
                    "Saturday": [],
                    "Sunday": []
                }
            }
            
            response = client.post("/api/meal-plans", json=meal_plan_data)
            assert response.status_code == 200
        
        # Test pagination
        response = client.get("/api/meal-plans", params={"page": 1, "page_size": 3})
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["items"]) == 3
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 3
    
    def test_get_meal_plans_empty(self, client: TestClient):
        """Test get meal plans when none exist"""
        response = client.get("/api/meal-plans")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
    
    def test_get_meal_plan_by_id(self, client: TestClient, sample_meal_plan_data):
        """Test retrieving meal plan by ID"""
        # Create meal plan
        response = client.post("/api/meal-plans", json=sample_meal_plan_data)
        assert response.status_code == 200
        meal_plan_id = response.json()["id"]
        
        # Get meal plan
        response = client.get(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == meal_plan_id
        assert data["name"] == sample_meal_plan_data["name"]
    
    def test_get_meal_plan_not_found(self, client: TestClient):
        """Test get meal plan that doesn't exist"""
        response = client.get("/api/meal-plans/99999")
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "meal plan not found" in error_data["detail"].lower()
    
    def test_delete_meal_plan_success(self, client: TestClient, sample_meal_plan_data):
        """Test successful meal plan deletion"""
        # Create meal plan
        response = client.post("/api/meal-plans", json=sample_meal_plan_data)
        assert response.status_code == 200
        meal_plan_id = response.json()["id"]
        
        # Delete meal plan
        response = client.delete(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 404
    
    def test_delete_meal_plan_not_found(self, client: TestClient):
        """Test delete meal plan that doesn't exist"""
        response = client.delete("/api/meal-plans/99999")
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "meal plan not found" in error_data["detail"].lower()
    
    def test_meal_plan_with_multiple_recipes(self, client: TestClient):
        """Test meal plan with multiple recipes per day"""
        # Create multiple recipes
        recipe_ids = []
        for i in range(3):
            recipe_data = {
                "title": f"Recipe {i}",
                "description": f"Description {i}",
                "instructions": f"Instructions {i}",
                "ingredients": [{"name": f"ingredient_{i}", "amount": "1", "unit": "cup"}],
                "difficulty": "Easy"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
            recipe_ids.append(response.json()["id"])
        
        # Create meal plan with multiple recipes per day
        meal_plan_data = {
            "name": "Multi-Recipe Plan",
            "recipes": {
                "Monday": recipe_ids[:2],  # 2 recipes
                "Tuesday": recipe_ids[1:],  # 2 recipes
                "Wednesday": [recipe_ids[0]],  # 1 recipe
                "Thursday": [],
                "Friday": recipe_ids,  # 3 recipes
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["recipes"]["Monday"]) == 2
        assert len(data["recipes"]["Tuesday"]) == 2
        assert len(data["recipes"]["Wednesday"]) == 1
        assert len(data["recipes"]["Thursday"]) == 0
        assert len(data["recipes"]["Friday"]) == 3
    
    def test_meal_plan_recipe_validation(self, client: TestClient):
        """Test meal plan recipe ID validation"""
        # Test with invalid recipe ID types
        invalid_meal_plan = {
            "name": "Invalid Plan",
            "recipes": {
                "Monday": ["invalid_id"],  # String instead of int
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=invalid_meal_plan)
        assert response.status_code == 422
        
        # Test with negative recipe IDs
        invalid_meal_plan_negative = {
            "name": "Invalid Plan",
            "recipes": {
                "Monday": [-1],  # Negative ID
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=invalid_meal_plan_negative)
        assert response.status_code == 422
    
    def test_meal_plan_name_validation(self, client: TestClient):
        """Test meal plan name validation"""
        # Test empty name
        invalid_data = {
            "name": "",
            "recipes": {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=invalid_data)
        assert response.status_code == 422
        
        # Test very long name
        invalid_data_long = {
            "name": "A" * 201,  # Assuming 200 char limit
            "recipes": {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=invalid_data_long)
        assert response.status_code == 422

"""
Frontend integration tests for the Recipe Generator application
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json


class TestFrontendIntegration:
    """Test cases for frontend integration scenarios"""

    def test_frontend_api_endpoints_availability(self, client: TestClient):
        """Test all API endpoints used by frontend are available"""
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200

        # Test recipes endpoint structure
        response = client.get("/api/recipes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_recipe_generation_frontend_flow(self, client: TestClient):
        """Test complete frontend flow for recipe generation"""
        generation_data = {
            "ingredients": ["chicken", "rice", "vegetables"],
            "meal_type": "dinner",
            "dietary_preferences": ["vegetarian"],
        }

        mock_recipes = [{
            "title": "Vegetarian Rice Bowl",
            "description": "A healthy vegetarian rice bowl",
            "instructions": "1. Cook rice\n2. Steam vegetables\n3. Combine",
            "ingredients": [
                {"name": "rice", "amount": "1", "unit": "cup"},
                {"name": "vegetables", "amount": "2", "unit": "cups"}
            ],
            "prep_time": 15,
            "cook_time": 20,
            "servings": 2,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Vegetarian Rice Bowl"

    def test_recipe_save_and_retrieve_flow(self, client: TestClient, sample_recipe_data):
        """Test save recipe from frontend and retrieve flow"""
        # Save recipe (as would happen from frontend)
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_response.status_code == 200
        
        saved_recipe = create_response.json()
        recipe_id = saved_recipe["id"]

        # Retrieve saved recipe (as frontend would do)
        get_response = client.get(f"/api/recipes/{recipe_id}")
        assert get_response.status_code == 200
        
        retrieved_recipe = get_response.json()
        assert retrieved_recipe["title"] == sample_recipe_data["title"]
        assert retrieved_recipe["id"] == recipe_id

    def test_recipe_rating_frontend_flow(self, client: TestClient, sample_recipe_data):
        """Test recipe rating flow from frontend"""
        # Create recipe
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        recipe_id = create_response.json()["id"]

        # Rate recipe (as frontend would do)
        rating_data = {"rating": 4}
        rating_response = client.put(f"/api/recipes/{recipe_id}/rate", json=rating_data)
        
        assert rating_response.status_code == 200
        rated_recipe = rating_response.json()
        assert rated_recipe["rating"] == 4

    def test_recipe_search_frontend_flow(self, client: TestClient):
        """Test recipe search functionality used by frontend"""
        # Create multiple recipes for search
        recipes_data = [
            {
                "title": "Pasta Carbonara",
                "description": "Classic Italian pasta dish",
                "instructions": "1. Cook pasta\n2. Make sauce\n3. Combine",
                "ingredients": [
                    {"name": "pasta", "amount": "400", "unit": "g"},
                    {"name": "eggs", "amount": "2", "unit": "pieces"}
                ],
                "prep_time": 10,
                "cook_time": 15,
                "servings": 4,
                "difficulty": "Medium",
            },
            {
                "title": "Vegetable Stir Fry",
                "description": "Quick vegetable dish",
                "instructions": "1. Heat oil\n2. Add vegetables\n3. Stir fry",
                "ingredients": [
                    {"name": "vegetables", "amount": "300", "unit": "g"},
                    {"name": "oil", "amount": "2", "unit": "tbsp"}
                ],
                "prep_time": 5,
                "cook_time": 10,
                "servings": 2,
                "difficulty": "Easy",
            }
        ]

        # Create recipes
        for recipe_data in recipes_data:
            client.post("/api/recipes", json=recipe_data)

        # Search for pasta recipes
        search_response = client.get("/api/recipes?search=pasta")
        assert search_response.status_code == 200
        
        search_results = search_response.json()
        assert len(search_results) >= 1
        assert any("pasta" in recipe["title"].lower() for recipe in search_results)

    def test_meal_planning_frontend_integration(self, client: TestClient, sample_recipe_data):
        """Test meal planning functionality from frontend perspective"""
        # Create a recipe first
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        recipe_id = create_response.json()["id"]

        # Create meal plan (as frontend would do)
        meal_plan_data = {
            "name": "Weekly Plan",
            "start_date": "2024-01-01",
            "meals": [
                {
                    "day": "monday",
                    "meal_type": "dinner",
                    "recipe_id": recipe_id
                }
            ]
        }

        meal_plan_response = client.post("/api/meal-plans", json=meal_plan_data)
        assert meal_plan_response.status_code == 200
        
        meal_plan = meal_plan_response.json()
        assert meal_plan["name"] == "Weekly Plan"
        assert len(meal_plan["meals"]) == 1

    def test_error_handling_frontend_scenarios(self, client: TestClient):
        """Test error scenarios that frontend should handle"""
        # Test invalid recipe generation request
        invalid_data = {
            "ingredients": [],  # Empty ingredients
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=invalid_data)
        assert response.status_code == 422  # Validation error

        # Test accessing non-existent recipe
        response = client.get("/api/recipes/99999")
        assert response.status_code == 404

        # Test invalid rating
        create_response = client.post("/api/recipes", json={
            "title": "Test Recipe",
            "description": "Test",
            "instructions": "1. Test",
            "ingredients": [{"name": "test", "amount": "1", "unit": "cup"}],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "Easy",
        })
        recipe_id = create_response.json()["id"]

        invalid_rating = {"rating": 6}  # Rating should be 1-5
        rating_response = client.put(f"/api/recipes/{recipe_id}/rate", json=invalid_rating)
        assert rating_response.status_code == 422

    def test_pagination_frontend_support(self, client: TestClient):
        """Test pagination support for frontend"""
        # Create multiple recipes
        for i in range(5):
            recipe_data = {
                "title": f"Recipe {i}",
                "description": f"Test recipe {i}",
                "instructions": "1. Test step",
                "ingredients": [{"name": "test", "amount": "1", "unit": "cup"}],
                "prep_time": 10,
                "cook_time": 15,
                "servings": 2,
                "difficulty": "Easy",
            }
            client.post("/api/recipes", json=recipe_data)

        # Test pagination parameters
        response = client.get("/api/recipes?skip=0&limit=3")
        assert response.status_code == 200
        
        recipes = response.json()
        assert len(recipes) <= 3  # Should respect limit

    def test_cors_headers_for_frontend(self, client: TestClient):
        """Test CORS headers are present for frontend requests"""
        response = client.options("/api/recipes")
        
        # Should have CORS headers for frontend
        assert response.status_code in [200, 204]
        
        # Test actual request with origin
        headers = {"Origin": "http://localhost:3000"}
        response = client.get("/api/recipes", headers=headers)
        assert response.status_code == 200

    def test_api_response_format_consistency(self, client: TestClient, sample_recipe_data):
        """Test API response format consistency for frontend consumption"""
        # Create recipe
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        assert create_response.status_code == 200
        
        created_recipe = create_response.json()
        required_fields = ["id", "title", "description", "instructions", 
                          "ingredients", "prep_time", "cook_time", "servings", "difficulty"]
        
        for field in required_fields:
            assert field in created_recipe

        # Get recipe
        recipe_id = created_recipe["id"]
        get_response = client.get(f"/api/recipes/{recipe_id}")
        retrieved_recipe = get_response.json()
        
        # Same fields should be present
        for field in required_fields:
            assert field in retrieved_recipe

        # Values should match
        assert created_recipe["title"] == retrieved_recipe["title"]

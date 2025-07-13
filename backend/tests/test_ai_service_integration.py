"""
Comprehensive tests for AI service integration and error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json


class TestAIServiceIntegration:
    """Test cases for AI service integration and error scenarios"""

    def test_ai_service_timeout(self, client: TestClient):
        """Test handling of AI service timeouts"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.side_effect = TimeoutError("AI service timeout")
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 500
        assert "timeout" in response.json()["detail"].lower()

    def test_ai_service_network_error(self, client: TestClient):
        """Test handling of network errors"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.side_effect = ConnectionError("Network connection failed")
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 500

    def test_ai_service_rate_limit_error(self, client: TestClient):
        """Test handling of rate limiting from AI service"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.side_effect = Exception("Rate limit exceeded")
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 500

    def test_ai_service_invalid_response_format(self, client: TestClient):
        """Test handling of invalid AI response format"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            # Return invalid format (not a list)
            mock_generate.return_value = "invalid response format"
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 500

    def test_ai_service_malformed_json_response(self, client: TestClient):
        """Test handling of malformed JSON from AI service"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        with patch("app.services.gemini_service.GeminiService._parse_response") as mock_parse:
            mock_parse.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            response = client.post("/api/recipes/generate", json=generation_data)

        # Should fallback to default recipes
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data

    def test_ai_service_incomplete_recipe_data(self, client: TestClient):
        """Test handling of incomplete recipe data from AI"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        incomplete_recipes = [{
            "title": "Incomplete Recipe",
            # Missing required fields like instructions, ingredients, etc.
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = incomplete_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200  # Should handle gracefully

    def test_ai_service_empty_response(self, client: TestClient):
        """Test handling of empty response from AI service"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = []
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 0

    def test_fallback_recipes_quality(self, client: TestClient):
        """Test that fallback recipes meet quality standards"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.side_effect = Exception("AI service unavailable")
            response = client.post("/api/recipes/generate", json=generation_data)

        # Should fallback to default recipes
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        
        if len(data["recipes"]) > 0:
            recipe = data["recipes"][0]
            assert "title" in recipe
            assert "instructions" in recipe
            assert "ingredients" in recipe

    def test_ai_service_partial_failure(self, client: TestClient):
        """Test handling when AI service returns some valid and some invalid recipes"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mixed_recipes = [
            {
                "title": "Valid Recipe",
                "description": "A valid recipe",
                "instructions": "1. Cook ingredients.",
                "ingredients": [{"name": "chicken", "amount": "1", "unit": "piece"}],
                "prep_time": 15,
                "cook_time": 20,
                "servings": 4,
                "difficulty": "Easy",
            },
            {
                "title": None,  # Invalid recipe
                "instructions": "",
            }
        ]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mixed_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200

    def test_ai_service_response_validation(self, client: TestClient):
        """Test validation of AI service response fields"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        invalid_field_recipes = [{
            "title": "Test Recipe",
            "description": "A test recipe",
            "instructions": "1. Cook ingredients.",
            "ingredients": [{"name": "chicken", "amount": "1", "unit": "piece"}],
            "prep_time": -5,  # Invalid negative prep time
            "cook_time": 2000,  # Invalid excessive cook time
            "servings": 0,  # Invalid servings
            "difficulty": "Impossible",  # Invalid difficulty
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = invalid_field_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200  # Should handle invalid fields gracefully

    def test_ai_service_cuisine_specific_generation(self, client: TestClient):
        """Test AI service generates cuisine-specific recipes"""
        cuisines = ["italian", "chinese", "mexican", "indian"]
        
        for cuisine in cuisines:
            generation_data = {
                "ingredients": ["chicken", "vegetables"],
                "meal_type": "dinner",
                "dietary_preferences": [],
                "cuisine_type": cuisine
            }

            mock_recipes = [{
                "title": f"{cuisine.title()} Chicken Dish",
                "description": f"A traditional {cuisine} recipe",
                "instructions": f"1. Prepare {cuisine} style. 2. Cook thoroughly.",
                "ingredients": [
                    {"name": "chicken", "amount": "1", "unit": "piece"},
                    {"name": "vegetables", "amount": "2", "unit": "cups"}
                ],
                "prep_time": 15,
                "cook_time": 25,
                "servings": 4,
                "difficulty": "Medium",
            }]

            with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
                mock_generate.return_value = mock_recipes
                response = client.post("/api/recipes/generate", json=generation_data)

            assert response.status_code == 200
            data = response.json()
            assert cuisine in data["generation_info"]["cuisine_type"]

    def test_ai_service_meal_type_specific_generation(self, client: TestClient):
        """Test AI service generates meal-type-specific recipes"""
        meal_types = ["breakfast", "lunch", "dinner", "snack"]
        
        for meal_type in meal_types:
            generation_data = {
                "ingredients": ["eggs", "bread", "vegetables"],
                "meal_type": meal_type,
                "dietary_preferences": [],
            }

            mock_recipes = [{
                "title": f"{meal_type.title()} Recipe",
                "description": f"A perfect {meal_type} dish",
                "instructions": f"1. Prepare for {meal_type}. 2. Cook appropriately.",
                "ingredients": [
                    {"name": "eggs", "amount": "2", "unit": "whole"},
                    {"name": "bread", "amount": "2", "unit": "slices"}
                ],
                "prep_time": 10,
                "cook_time": 15,
                "servings": 2,
                "difficulty": "Easy",
            }]

            with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
                mock_generate.return_value = mock_recipes
                response = client.post("/api/recipes/generate", json=generation_data)

            assert response.status_code == 200
            data = response.json()
            assert meal_type in data["generation_info"]["meal_type"]

    def test_ai_service_multiple_recipe_generation(self, client: TestClient):
        """Test AI service can generate multiple recipes"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes", "basil", "garlic"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        multiple_recipes = [
            {
                "title": "Chicken Pasta Recipe 1",
                "description": "First variation",
                "instructions": "1. Cook pasta. 2. Add chicken.",
                "ingredients": [
                    {"name": "chicken", "amount": "200", "unit": "g"},
                    {"name": "pasta", "amount": "150", "unit": "g"}
                ],
                "prep_time": 15,
                "cook_time": 20,
                "servings": 4,
                "difficulty": "Easy",
            },
            {
                "title": "Chicken Pasta Recipe 2",
                "description": "Second variation",
                "instructions": "1. Sauté chicken. 2. Cook pasta separately.",
                "ingredients": [
                    {"name": "chicken", "amount": "250", "unit": "g"},
                    {"name": "pasta", "amount": "200", "unit": "g"}
                ],
                "prep_time": 20,
                "cook_time": 25,
                "servings": 4,
                "difficulty": "Medium",
            }
        ]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = multiple_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 2
        assert data["generation_info"]["total_recipes"] == 2

    def test_ai_service_dietary_integration(self, client: TestClient):
        """Test AI service properly integrates with dietary filtering"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "vegetables"],
            "meal_type": "dinner",
            "dietary_preferences": ["vegetarian"],
        }

        # AI should receive filtered ingredients (without chicken)
        vegetarian_recipes = [{
            "title": "Vegetarian Pasta",
            "description": "A vegetarian pasta dish",
            "instructions": "1. Cook pasta. 2. Add vegetables.",
            "ingredients": [
                {"name": "pasta", "amount": "200", "unit": "g"},
                {"name": "vegetables", "amount": "2", "unit": "cups"}
            ],
            "prep_time": 15,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = vegetarian_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == True
        assert "chicken" in data["dietary_filtering"]["forbidden_ingredients"]

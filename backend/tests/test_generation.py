"""
Tests for recipe generation functionality with AI integration
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestRecipeGeneration:
    """Test cases for AI recipe generation endpoints"""

    def test_generate_recipe_success(self, client: TestClient):
        """Test successful recipe generation"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        # Mock the Gemini service response
        mock_recipes = [
            {
                "title": "Chicken Pasta with Tomatoes",
                "description": "A delicious pasta dish with chicken and fresh tomatoes",
                "instructions": "1. Cook pasta according to package directions. 2. Season chicken and cook in a pan. 3. Add tomatoes and combine.",
                "ingredients": [
                    {"name": "chicken breast", "amount": "2", "unit": "pieces"},
                    {"name": "pasta", "amount": "200", "unit": "g"},
                    {"name": "tomatoes", "amount": "3", "unit": "medium"},
                ],
                "prep_time": 15,
                "cook_time": 25,
                "servings": 4,
                "difficulty": "Easy",
            }
        ]

        with patch(
            "app.services.gemini_service.GeminiService.generate_recipes"
        ) as mock_generate:
            mock_generate.return_value = mock_recipes

            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200

        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["title"] == "Chicken Pasta with Tomatoes"
        assert data["recipes"][0]["is_temporary"] == True
        assert "dietary_filtering" in data
        assert "generation_info" in data

    def test_generate_recipe_missing_ingredients(self, client: TestClient):
        """Test generation with missing ingredients"""
        generation_data = {"meal_type": "dinner", "dietary_preferences": []}

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_multiple_ingredients(self, client: TestClient):
        """Test generation with multiple ingredients"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes", "basil", "garlic"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mock_recipes = [
            {
                "title": "Chicken Pasta Primavera",
                "description": "A flavorful pasta dish with chicken and herbs",
                "instructions": "1. Cook pasta. 2. Sauté chicken with garlic. 3. Add tomatoes and basil. 4. Combine and serve.",
                "ingredients": [
                    {"name": "chicken breast", "amount": "2", "unit": "pieces"},
                    {"name": "pasta", "amount": "200", "unit": "g"},
                    {"name": "tomatoes", "amount": "3", "unit": "medium"},
                    {"name": "basil", "amount": "10", "unit": "leaves"},
                    {"name": "garlic", "amount": "2", "unit": "cloves"},
                ],
                "prep_time": 20,
                "cook_time": 30,
                "servings": 4,
                "difficulty": "Medium",
            }
        ]

        with patch(
            "app.services.gemini_service.GeminiService.generate_recipes"
        ) as mock_generate:
            mock_generate.return_value = mock_recipes

            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200

        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["title"] == "Chicken Pasta Primavera"
        assert len(data["recipes"][0]["ingredients"]) == 5

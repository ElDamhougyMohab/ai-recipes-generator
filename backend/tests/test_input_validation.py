"""
Comprehensive tests for input validation across all endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestInputValidation:
    """Test cases for input validation and edge cases"""

    def test_generate_recipe_empty_ingredients_list(self, client: TestClient):
        """Test generation with empty ingredients list"""
        generation_data = {
            "ingredients": [],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422
        assert "ingredients" in response.json()["detail"][0]["loc"]

    def test_generate_recipe_invalid_ingredient_characters(self, client: TestClient):
        """Test generation with invalid ingredient characters"""
        generation_data = {
            "ingredients": ["chicken<script>", "pasta@#$%", "tomatoes!!!"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_too_long_ingredient_names(self, client: TestClient):
        """Test generation with ingredient names exceeding 100 characters"""
        long_ingredient = "a" * 101  # 101 characters
        generation_data = {
            "ingredients": ["chicken", long_ingredient, "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_too_short_ingredient_names(self, client: TestClient):
        """Test generation with ingredient names less than 2 characters"""
        generation_data = {
            "ingredients": ["a", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_duplicate_ingredients(self, client: TestClient):
        """Test generation with duplicate ingredients"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "chicken"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_max_ingredients_boundary(self, client: TestClient):
        """Test generation with exactly 30 ingredients (boundary test)"""
        ingredients = [f"ingredient_{i}" for i in range(30)]
        generation_data = {
            "ingredients": ingredients,
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mock_recipes = [{
            "title": "Complex Recipe",
            "description": "A recipe with many ingredients",
            "instructions": "1. Mix all ingredients. 2. Cook thoroughly.",
            "ingredients": [{"name": ing, "amount": "1", "unit": "cup"} for ing in ingredients[:10]],
            "prep_time": 30,
            "cook_time": 45,
            "servings": 6,
            "difficulty": "Hard",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200

    def test_generate_recipe_exceed_max_ingredients(self, client: TestClient):
        """Test generation with more than 30 ingredients"""
        ingredients = [f"ingredient_{i}" for i in range(31)]
        generation_data = {
            "ingredients": ingredients,
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_non_string_ingredients(self, client: TestClient):
        """Test generation with non-string ingredients"""
        generation_data = {
            "ingredients": ["chicken", 123, "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_invalid_dietary_preferences(self, client: TestClient):
        """Test generation with invalid dietary preferences"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": ["invalid_diet", "fake_preference"],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_max_dietary_preferences(self, client: TestClient):
        """Test generation with maximum dietary preferences (10)"""
        generation_data = {
            "ingredients": ["vegetables", "quinoa", "nuts"],
            "meal_type": "dinner",
            "dietary_preferences": [
                "vegetarian", "vegan", "gluten-free", "dairy-free", "nut-free",
                "low-carb", "keto", "paleo", "mediterranean", "halal"
            ],
        }

        mock_recipes = [{
            "title": "Complex Dietary Recipe",
            "description": "A recipe meeting multiple dietary restrictions",
            "instructions": "1. Prepare ingredients carefully. 2. Cook according to restrictions.",
            "ingredients": [
                {"name": "quinoa", "amount": "1", "unit": "cup"},
                {"name": "vegetables", "amount": "2", "unit": "cups"}
            ],
            "prep_time": 20,
            "cook_time": 25,
            "servings": 4,
            "difficulty": "Medium",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200

    def test_generate_recipe_exceed_max_dietary_preferences(self, client: TestClient):
        """Test generation with more than 10 dietary preferences"""
        generation_data = {
            "ingredients": ["vegetables", "quinoa"],
            "meal_type": "dinner",
            "dietary_preferences": [
                "vegetarian", "vegan", "gluten-free", "dairy-free", "nut-free",
                "low-carb", "keto", "paleo", "mediterranean", "halal", "extra_diet"
            ],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_invalid_cuisine_type(self, client: TestClient):
        """Test generation with invalid cuisine type"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
            "cuisine_type": "invalid_cuisine"
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_invalid_meal_type(self, client: TestClient):
        """Test generation with invalid meal type"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "invalid_meal",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_case_insensitive_dietary_preferences(self, client: TestClient):
        """Test generation with case variations in dietary preferences"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": ["VEGETARIAN", "Gluten-Free", "dairy-free"],
        }

        mock_recipes = [{
            "title": "Dietary Compliant Recipe",
            "description": "A recipe meeting dietary preferences",
            "instructions": "1. Prepare without restricted ingredients.",
            "ingredients": [
                {"name": "pasta", "amount": "200", "unit": "g"},
                {"name": "tomatoes", "amount": "3", "unit": "medium"}
            ],
            "prep_time": 15,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200

    def test_generate_recipe_missing_request_body(self, client: TestClient):
        """Test generation with missing request body"""
        response = client.post("/api/recipes/generate")
        assert response.status_code == 422

    def test_generate_recipe_malformed_json(self, client: TestClient):
        """Test generation with malformed JSON"""
        response = client.post(
            "/api/recipes/generate",
            data="{'malformed': json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_generate_recipe_whitespace_only_ingredients(self, client: TestClient):
        """Test generation with whitespace-only ingredients"""
        generation_data = {
            "ingredients": ["   ", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        response = client.post("/api/recipes/generate", json=generation_data)
        assert response.status_code == 422

    def test_generate_recipe_special_unicode_ingredients(self, client: TestClient):
        """Test generation with Unicode ingredients"""
        generation_data = {
            "ingredients": ["café", "naïve", "résumé"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mock_recipes = [{
            "title": "International Recipe",
            "description": "A recipe with international ingredients",
            "instructions": "1. Prepare international ingredients.",
            "ingredients": [
                {"name": "café", "amount": "1", "unit": "cup"},
                {"name": "naïve", "amount": "2", "unit": "tbsp"}
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

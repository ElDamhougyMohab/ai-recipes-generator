"""
Comprehensive tests for dietary restriction functionality
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestDietaryRestrictions:
    """Test cases for dietary restriction filtering and validation"""

    def test_vegetarian_filtering(self, client: TestClient):
        """Test vegetarian diet filters meat ingredients"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes", "cheese"],
            "meal_type": "dinner",
            "dietary_preferences": ["vegetarian"],
        }

        mock_recipes = [{
            "title": "Vegetarian Pasta",
            "description": "A delicious vegetarian pasta dish",
            "instructions": "1. Cook pasta. 2. Add cheese and tomatoes.",
            "ingredients": [
                {"name": "pasta", "amount": "200", "unit": "g"},
                {"name": "tomatoes", "amount": "3", "unit": "medium"},
                {"name": "cheese", "amount": "100", "unit": "g"}
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
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == True
        assert "chicken" in data["dietary_filtering"]["forbidden_ingredients"]

    def test_vegan_filtering(self, client: TestClient):
        """Test vegan diet filters all animal products"""
        generation_data = {
            "ingredients": ["chicken", "milk", "eggs", "pasta", "vegetables"],
            "meal_type": "dinner",
            "dietary_preferences": ["vegan"],
        }

        mock_recipes = [{
            "title": "Vegan Pasta",
            "description": "A completely vegan pasta dish",
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
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == True
        forbidden = data["dietary_filtering"]["forbidden_ingredients"]
        assert "chicken" in forbidden
        assert "milk" in forbidden
        assert "eggs" in forbidden

    def test_gluten_free_filtering(self, client: TestClient):
        """Test gluten-free diet filters wheat products"""
        generation_data = {
            "ingredients": ["wheat flour", "bread", "pasta", "rice", "vegetables"],
            "meal_type": "dinner",
            "dietary_preferences": ["gluten-free"],
        }

        mock_recipes = [{
            "title": "Gluten-Free Rice Bowl",
            "description": "A gluten-free rice and vegetable dish",
            "instructions": "1. Cook rice. 2. Add vegetables.",
            "ingredients": [
                {"name": "rice", "amount": "1", "unit": "cup"},
                {"name": "vegetables", "amount": "2", "unit": "cups"}
            ],
            "prep_time": 10,
            "cook_time": 25,
            "servings": 4,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == True
        forbidden = data["dietary_filtering"]["forbidden_ingredients"]
        assert any("wheat" in item or "bread" in item or "pasta" in item for item in forbidden)

    def test_dairy_free_filtering(self, client: TestClient):
        """Test dairy-free diet filters dairy products"""
        generation_data = {
            "ingredients": ["milk", "cheese", "butter", "vegetables", "rice"],
            "meal_type": "dinner",
            "dietary_preferences": ["dairy-free"],
        }

        mock_recipes = [{
            "title": "Dairy-Free Rice Bowl",
            "description": "A dairy-free rice and vegetable dish",
            "instructions": "1. Cook rice. 2. Add vegetables.",
            "ingredients": [
                {"name": "rice", "amount": "1", "unit": "cup"},
                {"name": "vegetables", "amount": "2", "unit": "cups"}
            ],
            "prep_time": 10,
            "cook_time": 25,
            "servings": 4,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == True
        forbidden = data["dietary_filtering"]["forbidden_ingredients"]
        assert "milk" in forbidden
        assert "cheese" in forbidden
        assert "butter" in forbidden

    def test_multiple_dietary_restrictions(self, client: TestClient):
        """Test multiple dietary restrictions together"""
        generation_data = {
            "ingredients": ["chicken", "milk", "wheat flour", "vegetables", "quinoa"],
            "meal_type": "dinner",
            "dietary_preferences": ["vegan", "gluten-free"],
        }

        mock_recipes = [{
            "title": "Vegan Gluten-Free Quinoa Bowl",
            "description": "A vegan and gluten-free quinoa dish",
            "instructions": "1. Cook quinoa. 2. Add vegetables.",
            "ingredients": [
                {"name": "quinoa", "amount": "1", "unit": "cup"},
                {"name": "vegetables", "amount": "2", "unit": "cups"}
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
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == True
        forbidden = data["dietary_filtering"]["forbidden_ingredients"]
        assert "chicken" in forbidden
        assert "milk" in forbidden
        assert "wheat flour" in forbidden

    def test_protein_suggestions_when_filtered(self, client: TestClient):
        """Test protein suggestions when meat ingredients are filtered"""
        generation_data = {
            "ingredients": ["beef", "chicken", "vegetables", "rice"],
            "meal_type": "dinner",
            "dietary_preferences": ["vegetarian"],
        }

        mock_recipes = [{
            "title": "Vegetarian Rice Bowl",
            "description": "A protein-rich vegetarian dish",
            "instructions": "1. Cook rice. 2. Add vegetables and protein alternatives.",
            "ingredients": [
                {"name": "rice", "amount": "1", "unit": "cup"},
                {"name": "vegetables", "amount": "2", "unit": "cups"},
                {"name": "tofu", "amount": "200", "unit": "g"}
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
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == True
        assert len(data["dietary_filtering"]["protein_suggestions"]) > 0

    def test_no_dietary_conflicts(self, client: TestClient):
        """Test case where no ingredients conflict with dietary preferences"""
        generation_data = {
            "ingredients": ["vegetables", "rice", "olive oil"],
            "meal_type": "dinner",
            "dietary_preferences": ["vegan"],
        }

        mock_recipes = [{
            "title": "Simple Vegan Rice",
            "description": "A simple vegan rice dish",
            "instructions": "1. Cook rice. 2. Add vegetables.",
            "ingredients": [
                {"name": "rice", "amount": "1", "unit": "cup"},
                {"name": "vegetables", "amount": "2", "unit": "cups"},
                {"name": "olive oil", "amount": "2", "unit": "tbsp"}
            ],
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200
        data = response.json()
        assert data["dietary_filtering"]["has_conflicts"] == False
        assert len(data["dietary_filtering"]["forbidden_ingredients"]) == 0

    def test_keto_diet_filtering(self, client: TestClient):
        """Test keto diet preferences"""
        generation_data = {
            "ingredients": ["bread", "pasta", "rice", "meat", "cheese", "avocado"],
            "meal_type": "dinner",
            "dietary_preferences": ["keto"],
        }

        mock_recipes = [{
            "title": "Keto Meat and Cheese",
            "description": "A keto-friendly high-fat dish",
            "instructions": "1. Cook meat. 2. Add cheese and avocado.",
            "ingredients": [
                {"name": "meat", "amount": "200", "unit": "g"},
                {"name": "cheese", "amount": "100", "unit": "g"},
                {"name": "avocado", "amount": "1", "unit": "whole"}
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

    def test_paleo_diet_filtering(self, client: TestClient):
        """Test paleo diet preferences"""
        generation_data = {
            "ingredients": ["grains", "legumes", "meat", "vegetables", "fruits"],
            "meal_type": "dinner",
            "dietary_preferences": ["paleo"],
        }

        mock_recipes = [{
            "title": "Paleo Meat and Vegetables",
            "description": "A paleo-friendly dish",
            "instructions": "1. Cook meat. 2. Add vegetables.",
            "ingredients": [
                {"name": "meat", "amount": "200", "unit": "g"},
                {"name": "vegetables", "amount": "2", "unit": "cups"}
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

    def test_dietary_validation_endpoint(self, client: TestClient):
        """Test the dietary validation endpoint"""
        validation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "dietary_preferences": ["vegetarian"],
        }

        response = client.post("/api/recipes/validate-diet", json=validation_data)
        assert response.status_code == 200

        data = response.json()
        assert "has_conflicts" in data
        assert "allowed_ingredients" in data
        assert "forbidden_ingredients" in data
        assert "protein_suggestions" in data

    def test_case_sensitivity_dietary_preferences(self, client: TestClient):
        """Test that dietary preferences are case insensitive"""
        generation_data = {
            "ingredients": ["chicken", "vegetables"],
            "meal_type": "dinner",
            "dietary_preferences": ["VEGETARIAN", "Dairy-Free"],
        }

        mock_recipes = [{
            "title": "Vegetarian Vegetables",
            "description": "A vegetarian dish",
            "instructions": "1. Cook vegetables.",
            "ingredients": [
                {"name": "vegetables", "amount": "2", "unit": "cups"}
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 4,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            response = client.post("/api/recipes/generate", json=generation_data)

        assert response.status_code == 200

    def test_comprehensive_dietary_combinations(self, client: TestClient):
        """Test various combinations of dietary restrictions"""
        test_combinations = [
            (["vegetarian", "gluten-free"], ["chicken", "wheat"], ["vegetables", "rice"]),
            (["vegan", "nut-free"], ["milk", "peanuts"], ["vegetables", "quinoa"]),
            (["dairy-free", "low-carb"], ["milk", "bread"], ["meat", "vegetables"]),
        ]

        for dietary_prefs, forbidden_ingredients, allowed_ingredients in test_combinations:
            generation_data = {
                "ingredients": forbidden_ingredients + allowed_ingredients,
                "meal_type": "dinner",
                "dietary_preferences": dietary_prefs,
            }

            mock_recipes = [{
                "title": f"Diet-Compliant Recipe",
                "description": f"A recipe following {', '.join(dietary_prefs)} diet",
                "instructions": "1. Prepare allowed ingredients.",
                "ingredients": [
                    {"name": ing, "amount": "1", "unit": "cup"} for ing in allowed_ingredients
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
            data = response.json()
            # Should have conflicts due to forbidden ingredients
            assert data["dietary_filtering"]["has_conflicts"] == True

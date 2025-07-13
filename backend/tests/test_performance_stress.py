"""
Performance and stress tests for the API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import time
import concurrent.futures
import threading


class TestPerformance:
    """Test cases for performance and stress testing"""

    def test_recipe_generation_response_time(self, client: TestClient):
        """Test recipe generation completes within acceptable time"""
        generation_data = {
            "ingredients": ["chicken", "pasta", "tomatoes"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mock_recipes = [{
            "title": "Quick Recipe",
            "description": "A quick test recipe",
            "instructions": "1. Cook quickly.",
            "ingredients": [
                {"name": "chicken", "amount": "1", "unit": "piece"}
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "Easy",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            
            start_time = time.time()
            response = client.post("/api/recipes/generate", json=generation_data)
            end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 5.0  # Should complete within 5 seconds

    def test_recipe_crud_response_time(self, client: TestClient, sample_recipe_data):
        """Test recipe CRUD operations response time"""
        # Create recipe
        start_time = time.time()
        create_response = client.post("/api/recipes", json=sample_recipe_data)
        create_time = time.time() - start_time

        assert create_response.status_code == 200
        assert create_time < 2.0  # Create should be fast

        recipe_id = create_response.json()["id"]

        # Read recipe
        start_time = time.time()
        read_response = client.get(f"/api/recipes/{recipe_id}")
        read_time = time.time() - start_time

        assert read_response.status_code == 200
        assert read_time < 1.0  # Read should be very fast

        # Delete recipe
        start_time = time.time()
        delete_response = client.delete(f"/api/recipes/{recipe_id}")
        delete_time = time.time() - start_time

        assert delete_response.status_code == 200
        assert delete_time < 2.0  # Delete should be fast

    def test_concurrent_recipe_generation(self, client: TestClient):
        """Test handling of concurrent recipe generation requests"""
        generation_data = {
            "ingredients": ["chicken", "pasta"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mock_recipes = [{
            "title": "Concurrent Recipe",
            "description": "A test recipe for concurrency",
            "instructions": "1. Cook concurrently.",
            "ingredients": [
                {"name": "chicken", "amount": "1", "unit": "piece"}
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "Easy",
        }]

        def make_request():
            with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
                mock_generate.return_value = mock_recipes
                response = client.post("/api/recipes/generate", json=generation_data)
                return response.status_code

        # Test 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(status == 200 for status in results)

    def test_large_ingredient_list_performance(self, client: TestClient):
        """Test performance with maximum ingredient count"""
        ingredients = [f"ingredient_{i}" for i in range(30)]  # Maximum allowed
        generation_data = {
            "ingredients": ingredients,
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mock_recipes = [{
            "title": "Large Ingredient Recipe",
            "description": "A recipe with many ingredients",
            "instructions": "1. Mix all ingredients carefully.",
            "ingredients": [
                {"name": ing, "amount": "1", "unit": "cup"} for ing in ingredients[:10]
            ],
            "prep_time": 30,
            "cook_time": 45,
            "servings": 8,
            "difficulty": "Hard",
        }]

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            
            start_time = time.time()
            response = client.post("/api/recipes/generate", json=generation_data)
            end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 10.0  # Should handle large lists within 10 seconds

    def test_stress_test_recipe_generation(self, client: TestClient):
        """Stress test with many recipe generation requests"""
        generation_data = {
            "ingredients": ["chicken", "vegetables"],
            "meal_type": "dinner",
            "dietary_preferences": [],
        }

        mock_recipes = [{
            "title": "Stress Test Recipe",
            "description": "A recipe for stress testing",
            "instructions": "1. Handle stress well.",
            "ingredients": [
                {"name": "chicken", "amount": "1", "unit": "piece"}
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "Easy",
        }]

        success_count = 0
        total_requests = 20  # Reduced for testing

        with patch("app.services.gemini_service.GeminiService.generate_recipes") as mock_generate:
            mock_generate.return_value = mock_recipes
            
            for _ in range(total_requests):
                try:
                    response = client.post("/api/recipes/generate", json=generation_data)
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass  # Count failures

        # Should handle at least 90% of requests successfully
        success_rate = success_count / total_requests
        assert success_rate >= 0.9

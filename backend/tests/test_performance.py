"""
Performance and load tests for API endpoints
"""
import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient


class TestPerformance:
    """Test cases for API performance and load handling"""
    
    def test_pagination_performance_large_dataset(self, client: TestClient):
        """Test pagination performance with large dataset"""
        # Create a large number of recipes
        start_time = time.time()
        
        recipes_to_create = 50
        for i in range(recipes_to_create):
            recipe_data = {
                "title": f"Performance Test Recipe {i}",
                "description": f"Recipe {i} for performance testing",
                "instructions": f"1. Prepare ingredients for recipe {i}. 2. Cook recipe {i}. 3. Serve recipe {i}.",
                "ingredients": [
                    {"name": f"ingredient_{i}_1", "amount": str(i+1), "unit": "cup"},
                    {"name": f"ingredient_{i}_2", "amount": "2", "unit": "tbsp"}
                ],
                "prep_time": 10 + (i % 10),
                "cook_time": 20 + (i % 20),
                "servings": (i % 6) + 2,
                "difficulty": ["Easy", "Medium", "Hard"][i % 3]
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
        
        creation_time = time.time() - start_time
        
        # Test pagination performance
        start_time = time.time()
        
        # Test multiple pages
        for page in range(1, 6):  # Test first 5 pages
            response = client.get("/api/recipes", params={"page": page, "page_size": 10})
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["items"]) <= 10
            assert data["page"] == page
        
        pagination_time = time.time() - start_time
        
        # Performance assertions
        assert creation_time < 30.0  # Should create 50 recipes in under 30 seconds
        assert pagination_time < 5.0  # Should paginate through 5 pages in under 5 seconds
    
    def test_search_performance_large_dataset(self, client: TestClient):
        """Test search performance with large dataset"""
        # Create recipes with searchable content
        search_terms = ["chicken", "pasta", "tomato", "beef", "vegetarian"]
        
        for i in range(30):
            term = search_terms[i % len(search_terms)]
            recipe_data = {
                "title": f"{term.title()} Recipe {i}",
                "description": f"A delicious {term} dish for testing search performance",
                "instructions": f"1. Prepare {term}. 2. Cook {term}. 3. Serve {term}.",
                "ingredients": [
                    {"name": term, "amount": str(i+1), "unit": "cup"},
                    {"name": "salt", "amount": "1", "unit": "tsp"}
                ],
                "prep_time": 15,
                "cook_time": 25,
                "servings": 4,
                "difficulty": "Easy"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
        
        # Test search performance
        start_time = time.time()
        
        for term in search_terms:
            response = client.get("/api/recipes/search", params={"q": term})
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["items"]) > 0
        
        search_time = time.time() - start_time
        
        # Performance assertion
        assert search_time < 3.0  # Should complete 5 searches in under 3 seconds
    
    def test_recipe_creation_performance(self, client: TestClient):
        """Test recipe creation performance"""
        recipe_data = {
            "title": "Performance Test Recipe",
            "description": "A recipe for performance testing",
            "instructions": "1. Prepare ingredients. 2. Cook food. 3. Serve.",
            "ingredients": [
                {"name": "chicken breast", "amount": "2", "unit": "pieces"},
                {"name": "pasta", "amount": "200", "unit": "g"},
                {"name": "tomatoes", "amount": "3", "unit": "medium"}
            ],
            "prep_time": 15,
            "cook_time": 25,
            "servings": 4,
            "difficulty": "Easy"
        }
        
        # Test creation time
        start_time = time.time()
        
        response = client.post("/api/recipes", json=recipe_data)
        
        creation_time = time.time() - start_time
        
        assert response.status_code == 200
        assert creation_time < 1.0  # Should create recipe in under 1 second
    
    def test_concurrent_recipe_creation(self, client: TestClient):
        """Test concurrent recipe creation"""
        def create_recipe(recipe_id):
            recipe_data = {
                "title": f"Concurrent Recipe {recipe_id}",
                "description": f"Recipe {recipe_id} created concurrently",
                "instructions": f"1. Make recipe {recipe_id}. 2. Enjoy.",
                "ingredients": [
                    {"name": f"ingredient_{recipe_id}", "amount": "1", "unit": "cup"}
                ],
                "prep_time": 10,
                "cook_time": 15,
                "servings": 2,
                "difficulty": "Easy"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            return response.status_code == 200
        
        # Test concurrent creation
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_recipe, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        concurrent_time = time.time() - start_time
        
        # All creations should succeed
        assert all(results)
        assert concurrent_time < 10.0  # Should complete 10 concurrent creations in under 10 seconds
    
    def test_meal_plan_creation_performance(self, client: TestClient):
        """Test meal plan creation performance"""
        # Create some recipes first
        recipe_ids = []
        for i in range(5):
            recipe_data = {
                "title": f"Meal Plan Recipe {i}",
                "description": f"Recipe {i} for meal planning",
                "instructions": f"1. Cook recipe {i}. 2. Serve.",
                "ingredients": [{"name": f"ingredient_{i}", "amount": "1", "unit": "cup"}],
                "difficulty": "Easy"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
            recipe_ids.append(response.json()["id"])
        
        # Test meal plan creation performance
        meal_plan_data = {
            "name": "Performance Test Meal Plan",
            "recipes": {
                "Monday": recipe_ids[:2],
                "Tuesday": recipe_ids[2:4],
                "Wednesday": [recipe_ids[4]],
                "Thursday": recipe_ids[:3],
                "Friday": recipe_ids[1:4],
                "Saturday": recipe_ids,
                "Sunday": recipe_ids[::2]
            }
        }
        
        start_time = time.time()
        
        response = client.post("/api/meal-plans", json=meal_plan_data)
        
        creation_time = time.time() - start_time
        
        assert response.status_code == 200
        assert creation_time < 2.0  # Should create meal plan in under 2 seconds
    
    def test_api_response_time_consistency(self, client: TestClient):
        """Test API response time consistency"""
        # Create a recipe first
        recipe_data = {
            "title": "Consistency Test Recipe",
            "description": "A recipe for testing response time consistency",
            "instructions": "1. Test consistency. 2. Measure time. 3. Validate.",
            "ingredients": [{"name": "test ingredient", "amount": "1", "unit": "cup"}],
            "difficulty": "Easy"
        }
        
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        recipe_id = response.json()["id"]
        
        # Test multiple requests to same endpoint
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = client.get(f"/api/recipes/{recipe_id}")
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
        
        # Check consistency
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # All responses should be fast and consistent
        assert avg_response_time < 0.5  # Average under 0.5 seconds
        assert max_response_time < 1.0  # Maximum under 1 second
        assert (max_response_time - min_response_time) < 0.5  # Variation under 0.5 seconds
    
    def test_memory_usage_large_payload(self, client: TestClient):
        """Test memory usage with large payloads"""
        # Create recipe with maximum allowed data
        large_recipe = {
            "title": "L" * 200,  # Maximum title length
            "description": "D" * 1000,  # Maximum description length
            "instructions": "I" * 2000,  # Large instructions
            "ingredients": [
                {
                    "name": f"ingredient_{i}",
                    "amount": str(i),
                    "unit": "cup",
                    "notes": f"notes_{i}" * 10
                }
                for i in range(50)  # Maximum ingredients
            ],
            "prep_time": 600,  # Maximum prep time
            "cook_time": 1440,  # Maximum cook time
            "servings": 20,  # Maximum servings
            "difficulty": "Expert"
        }
        
        start_time = time.time()
        
        response = client.post("/api/recipes", json=large_recipe)
        
        processing_time = time.time() - start_time
        
        assert response.status_code == 200
        assert processing_time < 3.0  # Should handle large payload in under 3 seconds
        
        # Verify data integrity
        data = response.json()
        assert len(data["ingredients"]) == 50
        assert len(data["title"]) == 200
        assert len(data["description"]) == 1000
    
    def test_database_connection_stress(self, client: TestClient):
        """Test database connection under stress"""
        # Perform multiple database operations rapidly
        operations = []
        
        start_time = time.time()
        
        # Create recipes
        for i in range(20):
            recipe_data = {
                "title": f"Stress Test Recipe {i}",
                "description": f"Recipe {i} for stress testing",
                "instructions": f"1. Create recipe {i}. 2. Test database.",
                "ingredients": [{"name": f"ingredient_{i}", "amount": "1", "unit": "cup"}],
                "difficulty": "Easy"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            operations.append(response.status_code == 200)
        
        # Read recipes
        for i in range(10):
            response = client.get("/api/recipes", params={"page": i+1, "page_size": 5})
            operations.append(response.status_code == 200)
        
        # Search recipes
        for i in range(5):
            response = client.get("/api/recipes/search", params={"q": f"recipe"})
            operations.append(response.status_code == 200)
        
        stress_time = time.time() - start_time
        
        # All operations should succeed
        assert all(operations)
        assert stress_time < 15.0  # Should complete all operations in under 15 seconds
    
    @pytest.mark.asyncio
    async def test_async_performance(self, async_client):
        """Test async endpoint performance"""
        # Test async recipe creation
        recipe_data = {
            "title": "Async Performance Test",
            "description": "Testing async performance",
            "instructions": "1. Test async. 2. Measure performance.",
            "ingredients": [{"name": "async ingredient", "amount": "1", "unit": "cup"}],
            "difficulty": "Easy"
        }
        
        start_time = time.time()
        
        response = await async_client.post("/api/recipes", json=recipe_data)
        
        async_time = time.time() - start_time
        
        assert response.status_code == 200
        assert async_time < 1.0  # Should complete async operation in under 1 second
    
    def test_error_handling_performance(self, client: TestClient):
        """Test error handling performance"""
        # Test validation error handling performance
        invalid_recipe = {
            "title": "",  # Invalid title
            "instructions": "Test",
            "ingredients": []  # Invalid ingredients
        }
        
        start_time = time.time()
        
        # Multiple validation errors
        for _ in range(10):
            response = client.post("/api/recipes", json=invalid_recipe)
            assert response.status_code == 422
        
        error_handling_time = time.time() - start_time
        
        # Error handling should be fast
        assert error_handling_time < 2.0  # Should handle 10 validation errors in under 2 seconds

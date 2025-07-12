"""
Tests for search functionality
"""
import pytest
from fastapi.testclient import TestClient


class TestSearch:
    """Test cases for recipe search functionality"""
    
    def test_search_recipes_by_title(self, client: TestClient):
        """Test searching recipes by title"""
        # Create test recipes
        recipes = [
            {"title": "Chicken Pasta", "description": "Delicious chicken pasta", "instructions": "Cook pasta", "ingredients": [{"name": "chicken", "amount": "1", "unit": "lb"}], "difficulty": "Easy"},
            {"title": "Beef Stir Fry", "description": "Quick beef stir fry", "instructions": "Stir fry beef", "ingredients": [{"name": "beef", "amount": "1", "unit": "lb"}], "difficulty": "Medium"},
            {"title": "Chicken Curry", "description": "Spicy chicken curry", "instructions": "Cook curry", "ingredients": [{"name": "chicken", "amount": "2", "unit": "lb"}], "difficulty": "Hard"}
        ]
        
        for recipe in recipes:
            response = client.post("/api/recipes", json=recipe)
            assert response.status_code == 200
        
        # Search for "chicken"
        response = client.get("/api/recipes/search", params={"q": "chicken"})
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2  # Should find 2 chicken recipes
        
        # Verify results contain chicken
        for recipe in data["items"]:
            assert "chicken" in recipe["title"].lower()
    
    def test_search_recipes_by_description(self, client: TestClient):
        """Test searching recipes by description"""
        # Create test recipes
        recipes = [
            {"title": "Recipe 1", "description": "Delicious spicy meal", "instructions": "Cook the spicy meal properly", "ingredients": [{"name": "ingredient", "amount": "1", "unit": "cup"}], "difficulty": "Easy"},
            {"title": "Recipe 2", "description": "Mild and sweet", "instructions": "Cook the mild meal properly", "ingredients": [{"name": "ingredient", "amount": "1", "unit": "cup"}], "difficulty": "Easy"},
            {"title": "Recipe 3", "description": "Very spicy dish", "instructions": "Cook the very spicy dish properly", "ingredients": [{"name": "ingredient", "amount": "1", "unit": "cup"}], "difficulty": "Easy"}
        ]
        
        for recipe in recipes:
            response = client.post("/api/recipes", json=recipe)
            assert response.status_code == 200
        
        # Search for "spicy"
        response = client.get("/api/recipes/search", params={"q": "spicy"})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 2
        
        # Verify results contain spicy
        for recipe in data["items"]:
            assert "spicy" in recipe["description"].lower()
    
    def test_search_recipes_by_ingredients(self, client: TestClient):
        """Test searching recipes by ingredients"""
        # Create test recipes
        recipes = [
            {
                "title": "Pasta with Tomatoes",
                "description": "Simple pasta",
                "instructions": "Cook pasta according to package directions",
                "ingredients": [
                    {"name": "pasta", "amount": "200", "unit": "g"},
                    {"name": "tomatoes", "amount": "3", "unit": "pieces"}
                ],
                "difficulty": "Easy"
            },
            {
                "title": "Tomato Soup",
                "description": "Creamy soup",
                "instructions": "Blend tomatoes with cream and seasonings",
                "ingredients": [
                    {"name": "tomatoes", "amount": "500", "unit": "g"},
                    {"name": "cream", "amount": "100", "unit": "ml"}
                ],
                "difficulty": "Easy"
            },
            {
                "title": "Beef Stew",
                "description": "Hearty stew",
                "instructions": "Stew beef with vegetables for hours",
                "ingredients": [
                    {"name": "beef", "amount": "1", "unit": "lb"},
                    {"name": "potatoes", "amount": "3", "unit": "pieces"}
                ],
                "difficulty": "Medium"
            }
        ]
        
        for recipe in recipes:
            response = client.post("/api/recipes", json=recipe)
            assert response.status_code == 200
        
        # Search for "tomatoes"
        response = client.get("/api/recipes/search", params={"q": "tomatoes"})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 2
        
        # Verify results contain tomatoes
        for recipe in data["items"]:
            has_tomatoes = any("tomato" in ingredient["name"].lower() for ingredient in recipe["ingredients"])
            assert has_tomatoes
    
    def test_search_recipes_case_insensitive(self, client: TestClient):
        """Test case-insensitive search"""
        # Create test recipe
        recipe_data = {
            "title": "Chicken Pasta",
            "description": "Delicious pasta with chicken",
            "instructions": "Cook pasta and chicken",
            "ingredients": [{"name": "chicken", "amount": "1", "unit": "lb"}],
            "difficulty": "Easy"
        }
        
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        
        # Test different cases
        search_terms = ["chicken", "CHICKEN", "Chicken", "ChIcKeN"]
        
        for term in search_terms:
            response = client.get("/api/recipes/search", params={"q": term})
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["title"] == "Chicken Pasta"
    
    def test_search_recipes_partial_match(self, client: TestClient):
        """Test partial word matching in search"""
        # Create test recipe
        recipe_data = {
            "title": "Spaghetti Bolognese",
            "description": "Traditional Italian pasta",
            "instructions": "Cook spaghetti",
            "ingredients": [{"name": "spaghetti", "amount": "200", "unit": "g"}],
            "difficulty": "Medium"
        }
        
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        
        # Search for partial matches
        partial_terms = ["spag", "bologna", "ital"]
        
        for term in partial_terms:
            response = client.get("/api/recipes/search", params={"q": term})
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["items"]) == 1
    
    def test_search_recipes_with_pagination(self, client: TestClient):
        """Test search results with pagination"""
        # Create multiple recipes with "pasta" in title
        for i in range(12):
            recipe_data = {
                "title": f"Pasta Recipe {i}",
                "description": f"Pasta recipe number {i}",
                "instructions": f"Cook pasta {i}",
                "ingredients": [{"name": "pasta", "amount": "200", "unit": "g"}],
                "difficulty": "Easy"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
        
        # Search with pagination
        response = client.get("/api/recipes/search", params={"q": "pasta", "page": 1, "page_size": 5})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 12
        assert data["pages"] == 3  # ceil(12/5) = 3
        assert data["has_next"] == True
        assert data["has_prev"] == False
        
        # Test second page
        response = client.get("/api/recipes/search", params={"q": "pasta", "page": 2, "page_size": 5})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 2
        assert data["has_next"] == True
        assert data["has_prev"] == True
    
    def test_search_recipes_no_results(self, client: TestClient):
        """Test search with no matching results"""
        # Create a recipe
        recipe_data = {
            "title": "Chicken Pasta",
            "description": "Delicious pasta",
            "instructions": "Cook pasta",
            "ingredients": [{"name": "chicken", "amount": "1", "unit": "lb"}],
            "difficulty": "Easy"
        }
        
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        
        # Search for non-existent term
        response = client.get("/api/recipes/search", params={"q": "nonexistent"})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 0
        assert data["total"] == 0
        assert data["pages"] == 0
    
    def test_search_recipes_empty_query(self, client: TestClient):
        """Test search with empty query"""
        response = client.get("/api/recipes/search", params={"q": ""})
        assert response.status_code == 422
    
    def test_search_recipes_special_characters(self, client: TestClient):
        """Test search with special characters"""
        # Create recipe with special characters
        recipe_data = {
            "title": "Café au Lait Recipe",
            "description": "French coffee with naïve herbs",
            "instructions": "Brew coffee",
            "ingredients": [{"name": "café beans", "amount": "50", "unit": "g"}],
            "difficulty": "Easy"
        }
        
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        
        # Search for special characters
        response = client.get("/api/recipes/search", params={"q": "café"})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 1
        assert "café" in data["items"][0]["title"].lower()
    
    def test_search_recipes_multiple_words(self, client: TestClient):
        """Test search with multiple words"""
        # Create test recipes
        recipes = [
            {"title": "Chicken Pasta Salad", "description": "Cold pasta salad", "instructions": "Mix ingredients", "ingredients": [{"name": "chicken", "amount": "1", "unit": "lb"}], "difficulty": "Easy"},
            {"title": "Beef Pasta Bake", "description": "Baked pasta dish", "instructions": "Bake pasta", "ingredients": [{"name": "beef", "amount": "1", "unit": "lb"}], "difficulty": "Medium"},
            {"title": "Vegetarian Pasta", "description": "Simple pasta", "instructions": "Cook pasta", "ingredients": [{"name": "pasta", "amount": "200", "unit": "g"}], "difficulty": "Easy"}
        ]
        
        for recipe in recipes:
            response = client.post("/api/recipes", json=recipe)
            assert response.status_code == 200
        
        # Search for multiple words
        response = client.get("/api/recipes/search", params={"q": "pasta salad"})
        assert response.status_code == 200
        
        data = response.json()
        # Should find recipes containing both words
        assert len(data["items"]) >= 1
        
        # Verify at least one result contains both words
        found_both = False
        for recipe in data["items"]:
            title_desc = f"{recipe['title']} {recipe['description']}".lower()
            if "pasta" in title_desc and "salad" in title_desc:
                found_both = True
                break
        assert found_both

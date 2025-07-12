"""
Tests for pagination functionality
"""
import pytest
from fastapi.testclient import TestClient


class TestPagination:
    """Test cases for pagination functionality"""
    
    def test_get_recipes_default_pagination(self, client: TestClient, created_multiple_recipes):
        """Test default pagination (page=1, per_page=10)"""
        response = client.get("/api/recipes")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        # Check pagination values
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["total"] == 15  # We created 15 recipes
        assert data["pages"] == 2  # ceil(15/10) = 2
        assert data["has_next"] == True
        assert data["has_prev"] == False
        assert len(data["items"]) == 10
    
    def test_get_recipes_custom_pagination(self, client: TestClient, created_multiple_recipes):
        """Test custom pagination (page=2, per_page=5)"""
        response = client.get("/api/recipes", params={"page": 2, "per_page": 5})
        assert response.status_code == 200
        
        data = response.json()
        
        # Check pagination values
        assert data["page"] == 2
        assert data["per_page"] == 5
        assert data["total"] == 15
        assert data["pages"] == 3  # ceil(15/5) = 3
        assert data["has_next"] == True
        assert data["has_prev"] == True
        assert len(data["items"]) == 5
    
    def test_get_recipes_last_page(self, client: TestClient, created_multiple_recipes):
        """Test last page of pagination"""
        response = client.get("/api/recipes", params={"page": 2, "per_page": 10})
        assert response.status_code == 200
        
        data = response.json()
        
        # Check last page
        assert data["page"] == 2
        assert data["per_page"] == 10
        assert data["total"] == 15
        assert data["pages"] == 2
        assert data["has_next"] == False
        assert data["has_prev"] == True
        assert len(data["items"]) == 5  # Remaining 5 items
    
    def test_get_recipes_max_per_page_limit(self, client: TestClient, created_multiple_recipes):
        """Test per_page is limited to maximum (10)"""
        response = client.get("/api/recipes", params={"page": 1, "per_page": 15})
        assert response.status_code == 200
        
        data = response.json()
        
        # Should be limited to 10
        assert data["per_page"] == 10
        assert len(data["items"]) == 10
    
    def test_get_recipes_empty_database(self, client: TestClient):
        """Test pagination with no recipes"""
        response = client.get("/api/recipes")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check empty pagination
        assert data["total"] == 0
        assert data["pages"] == 0
        assert data["has_next"] == False
        assert data["has_prev"] == False
        assert len(data["items"]) == 0
    
    def test_get_recipes_invalid_page_number(self, client: TestClient, created_multiple_recipes):
        """Test invalid page numbers"""
        # Test negative page number
        response = client.get("/api/recipes", params={"page": -1})
        assert response.status_code == 422
        
        # Test zero page number
        response = client.get("/api/recipes", params={"page": 0})
        assert response.status_code == 422
        
        # Test page number too high (should return empty results)
        response = client.get("/api/recipes", params={"page": 999})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 0
        assert data["page"] == 999
    
    def test_get_recipes_invalid_per_page(self, client: TestClient, created_multiple_recipes):
        """Test invalid page sizes"""
        # Test negative page size
        response = client.get("/api/recipes", params={"per_page": -1})
        assert response.status_code == 422
        
        # Test zero page size
        response = client.get("/api/recipes", params={"per_page": 0})
        assert response.status_code == 422
        
        # Test page size too high (should be capped at 10)
        response = client.get("/api/recipes", params={"per_page": 100})
        assert response.status_code == 200
        
        data = response.json()
        assert data["per_page"] == 10
    
    def test_pagination_consistency(self, client: TestClient, created_multiple_recipes):
        """Test pagination consistency across multiple requests"""
        # Get all recipes across pages
        all_recipe_ids = []
        
        # Page 1
        response = client.get("/api/recipes", params={"page": 1, "per_page": 10})
        assert response.status_code == 200
        page1_data = response.json()
        all_recipe_ids.extend([recipe["id"] for recipe in page1_data["items"]])
        
        # Page 2
        response = client.get("/api/recipes", params={"page": 2, "per_page": 10})
        assert response.status_code == 200
        page2_data = response.json()
        all_recipe_ids.extend([recipe["id"] for recipe in page2_data["items"]])
        
        # Check no duplicates
        assert len(all_recipe_ids) == len(set(all_recipe_ids))
        
        # Check total count
        assert len(all_recipe_ids) == 15
    
    def test_pagination_with_different_per_pages(self, client: TestClient, created_multiple_recipes):
        """Test pagination with different page sizes"""
        per_pages = [1, 3, 5, 10]
        
        for per_page in per_pages:
            response = client.get("/api/recipes", params={"page": 1, "per_page": per_page})
            assert response.status_code == 200
            
            data = response.json()
            assert data["per_page"] == per_page
            assert len(data["items"]) == min(per_page, 15)  # Don't exceed total recipes
            
            # Check total pages calculation
            expected_pages = (15 + per_page - 1) // per_page  # Ceiling division
            assert data["pages"] == expected_pages
    
    def test_pagination_metadata_accuracy(self, client: TestClient):
        """Test accuracy of pagination metadata with known data"""
        # Create exactly 7 recipes
        for i in range(7):
            recipe_data = {
                "title": f"Recipe {i}",
                "description": f"Description {i}",
                "instructions": f"Instructions {i}",
                "ingredients": [{"name": f"ingredient_{i}", "amount": "1", "unit": "cup"}],
                "prep_time": 10,
                "cook_time": 20,
                "servings": 4,
                "difficulty": "Easy"
            }
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
        
        # Test per_page = 3
        response = client.get("/api/recipes", params={"per_page": 3})
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 7
        assert data["pages"] == 3  # ceil(7/3) = 3
        assert data["page"] == 1
        assert data["per_page"] == 3
        assert data["has_next"] == True
        assert data["has_prev"] == False
        assert len(data["items"]) == 3
        
        # Test page 2
        response = client.get("/api/recipes", params={"page": 2, "per_page": 3})
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 2
        assert data["has_next"] == True
        assert data["has_prev"] == True
        assert len(data["items"]) == 3
        
        # Test page 3 (last page)
        response = client.get("/api/recipes", params={"page": 3, "per_page": 3})
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 3
        assert data["has_next"] == False
        assert data["has_prev"] == True
        assert len(data["items"]) == 1  # Only 1 recipe on last page

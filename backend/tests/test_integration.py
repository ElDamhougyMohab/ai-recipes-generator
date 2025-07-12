"""
Integration tests for end-to-end workflows
"""
import pytest
from fastapi.testclient import TestClient


class TestIntegration:
    """Test cases for complete end-to-end workflows"""
    
    def test_complete_recipe_workflow(self, client: TestClient):
        """Test complete recipe workflow: Create → Read → Search → Delete"""
        # Step 1: Create a recipe
        recipe_data = {
            "title": "Integration Test Chicken Pasta",
            "description": "A complete recipe for integration testing",
            "instructions": "1. Cook pasta according to package directions. 2. Season chicken and cook. 3. Combine and serve.",
            "ingredients": [
                {"name": "chicken breast", "amount": "2", "unit": "pieces", "notes": "boneless"},
                {"name": "pasta", "amount": "200", "unit": "g", "notes": "penne or fusilli"},
                {"name": "olive oil", "amount": "2", "unit": "tbsp", "notes": None}
            ],
            "prep_time": 15,
            "cook_time": 25,
            "servings": 4,
            "difficulty": "Easy"
        }
        
        # Create recipe
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        
        created_recipe = response.json()
        recipe_id = created_recipe["id"]
        
        # Verify creation
        assert created_recipe["title"] == recipe_data["title"]
        assert len(created_recipe["ingredients"]) == 3
        
        # Step 2: Read the recipe
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        
        retrieved_recipe = response.json()
        assert retrieved_recipe["id"] == recipe_id
        assert retrieved_recipe["title"] == recipe_data["title"]
        
        # Step 3: Search for the recipe
        response = client.get("/api/recipes/search", params={"q": "chicken"})
        assert response.status_code == 200
        
        search_results = response.json()
        assert len(search_results["items"]) >= 1
        
        # Find our recipe in search results
        found_recipe = next((r for r in search_results["items"] if r["id"] == recipe_id), None)
        assert found_recipe is not None
        assert found_recipe["title"] == recipe_data["title"]
        
        # Step 4: Rate the recipe
        response = client.put(f"/api/recipes/{recipe_id}/rating", params={"rating": 4.5})
        assert response.status_code == 200
        
        rated_recipe = response.json()
        assert rated_recipe["rating"] == 4.5
        
        # Step 5: Verify rating is persisted
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        
        final_recipe = response.json()
        assert final_recipe["rating"] == 4.5
        
        # Step 6: Delete the recipe
        response = client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        
        # Step 7: Verify deletion
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 404
    
    def test_complete_meal_planning_workflow(self, client: TestClient):
        """Test complete meal planning workflow: Create recipes → Create meal plan → Read → Delete"""
        # Step 1: Create multiple recipes
        recipes_data = [
            {
                "title": "Breakfast Pancakes",
                "description": "Fluffy pancakes for breakfast",
                "instructions": "1. Mix batter. 2. Cook pancakes. 3. Serve with syrup.",
                "ingredients": [{"name": "flour", "amount": "2", "unit": "cups"}],
                "difficulty": "Easy"
            },
            {
                "title": "Lunch Salad",
                "description": "Fresh salad for lunch",
                "instructions": "1. Wash vegetables. 2. Chop ingredients. 3. Toss with dressing.",
                "ingredients": [{"name": "lettuce", "amount": "1", "unit": "head"}],
                "difficulty": "Easy"
            },
            {
                "title": "Dinner Steak",
                "description": "Grilled steak for dinner",
                "instructions": "1. Season steak. 2. Grill to preference. 3. Rest and serve.",
                "ingredients": [{"name": "steak", "amount": "2", "unit": "pieces"}],
                "difficulty": "Medium"
            }
        ]
        
        created_recipes = []
        for recipe_data in recipes_data:
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
            created_recipes.append(response.json())
        
        recipe_ids = [r["id"] for r in created_recipes]
        
        # Step 2: Create meal plan
        meal_plan_data = {
            "name": "Integration Test Weekly Plan",
            "recipes": {
                "Monday": [recipe_ids[0], recipe_ids[1]],  # Breakfast + Lunch
                "Tuesday": [recipe_ids[2]],  # Dinner
                "Wednesday": [recipe_ids[0]],  # Breakfast
                "Thursday": [recipe_ids[1], recipe_ids[2]],  # Lunch + Dinner
                "Friday": recipe_ids,  # All meals
                "Saturday": [recipe_ids[0], recipe_ids[2]],  # Breakfast + Dinner
                "Sunday": []  # No meals planned
            }
        }
        
        response = client.post("/api/meal-plans", json=meal_plan_data)
        assert response.status_code == 200
        
        created_meal_plan = response.json()
        meal_plan_id = created_meal_plan["id"]
        
        # Verify meal plan creation
        assert created_meal_plan["name"] == meal_plan_data["name"]
        assert len(created_meal_plan["recipes"]["Monday"]) == 2
        assert len(created_meal_plan["recipes"]["Friday"]) == 3
        assert len(created_meal_plan["recipes"]["Sunday"]) == 0
        
        # Step 3: Read meal plan
        response = client.get(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
        
        retrieved_meal_plan = response.json()
        assert retrieved_meal_plan["id"] == meal_plan_id
        assert retrieved_meal_plan["name"] == meal_plan_data["name"]
        
        # Step 4: List all meal plans
        response = client.get("/api/meal-plans")
        assert response.status_code == 200
        
        meal_plans_list = response.json()
        assert meal_plans_list["total"] >= 1
        
        # Find our meal plan
        found_plan = next((p for p in meal_plans_list["items"] if p["id"] == meal_plan_id), None)
        assert found_plan is not None
        
        # Step 5: Delete meal plan
        response = client.delete(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
        
        # Step 6: Verify deletion
        response = client.get(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 404
        
        # Step 7: Clean up recipes
        for recipe_id in recipe_ids:
            response = client.delete(f"/api/recipes/{recipe_id}")
            assert response.status_code == 200
    
    def test_pagination_with_search_integration(self, client: TestClient):
        """Test pagination integrated with search functionality"""
        # Step 1: Create many recipes with searchable content
        chicken_recipes = []
        beef_recipes = []
        
        # Create 12 chicken recipes
        for i in range(12):
            recipe_data = {
                "title": f"Chicken Recipe {i+1}",
                "description": f"Delicious chicken dish number {i+1}",
                "instructions": f"1. Prepare chicken {i+1}. 2. Cook chicken {i+1}. 3. Serve.",
                "ingredients": [{"name": "chicken", "amount": str(i+1), "unit": "pieces"}],
                "difficulty": "Easy"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
            chicken_recipes.append(response.json())
        
        # Create 8 beef recipes
        for i in range(8):
            recipe_data = {
                "title": f"Beef Recipe {i+1}",
                "description": f"Tasty beef dish number {i+1}",
                "instructions": f"1. Prepare beef {i+1}. 2. Cook beef {i+1}. 3. Serve.",
                "ingredients": [{"name": "beef", "amount": str(i+1), "unit": "pounds"}],
                "difficulty": "Medium"
            }
            
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
            beef_recipes.append(response.json())
        
        # Step 2: Test search with pagination
        # Search for chicken recipes (should find 12)
        response = client.get("/api/recipes/search", params={"q": "chicken", "page": 1, "page_size": 5})
        assert response.status_code == 200
        
        search_results = response.json()
        assert search_results["total"] == 12
        assert len(search_results["items"]) == 5
        assert search_results["pages"] == 3  # ceil(12/5) = 3
        assert search_results["has_next"] == True
        assert search_results["has_prev"] == False
        
        # Get second page
        response = client.get("/api/recipes/search", params={"q": "chicken", "page": 2, "page_size": 5})
        assert response.status_code == 200
        
        search_results_p2 = response.json()
        assert search_results_p2["page"] == 2
        assert len(search_results_p2["items"]) == 5
        assert search_results_p2["has_next"] == True
        assert search_results_p2["has_prev"] == True
        
        # Get third page
        response = client.get("/api/recipes/search", params={"q": "chicken", "page": 3, "page_size": 5})
        assert response.status_code == 200
        
        search_results_p3 = response.json()
        assert search_results_p3["page"] == 3
        assert len(search_results_p3["items"]) == 2  # Remaining 2 recipes
        assert search_results_p3["has_next"] == False
        assert search_results_p3["has_prev"] == True
        
        # Step 3: Test general pagination includes all recipes
        response = client.get("/api/recipes", params={"page": 1, "page_size": 10})
        assert response.status_code == 200
        
        all_recipes = response.json()
        assert all_recipes["total"] == 20  # 12 chicken + 8 beef
        assert len(all_recipes["items"]) == 10
        assert all_recipes["pages"] == 2
        
        # Step 4: Verify no cross-contamination in search results
        response = client.get("/api/recipes/search", params={"q": "beef"})
        assert response.status_code == 200
        
        beef_search = response.json()
        assert beef_search["total"] == 8
        
        # All results should contain "beef"
        for recipe in beef_search["items"]:
            assert "beef" in recipe["title"].lower() or "beef" in recipe["description"].lower()
    
    def test_data_consistency_across_operations(self, client: TestClient):
        """Test data consistency across multiple operations"""
        # Step 1: Create recipe
        original_recipe = {
            "title": "Consistency Test Recipe",
            "description": "Testing data consistency",
            "instructions": "1. Test consistency. 2. Verify data integrity.",
            "ingredients": [
                {"name": "test ingredient", "amount": "1", "unit": "cup", "notes": "for testing"}
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "Easy"
        }
        
        response = client.post("/api/recipes", json=original_recipe)
        assert response.status_code == 200
        
        created_recipe = response.json()
        recipe_id = created_recipe["id"]
        
        # Step 2: Verify data integrity after creation
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        
        retrieved_recipe = response.json()
        assert retrieved_recipe["title"] == original_recipe["title"]
        assert retrieved_recipe["prep_time"] == original_recipe["prep_time"]
        assert len(retrieved_recipe["ingredients"]) == len(original_recipe["ingredients"])
        assert retrieved_recipe["ingredients"][0]["name"] == original_recipe["ingredients"][0]["name"]
        
        # Step 3: Rate recipe and verify consistency
        response = client.put(f"/api/recipes/{recipe_id}/rating", params={"rating": 3.5})
        assert response.status_code == 200
        
        # Verify rating through different endpoints
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        assert response.json()["rating"] == 3.5
        
        # Verify rating in search results
        response = client.get("/api/recipes/search", params={"q": "consistency"})
        assert response.status_code == 200
        
        search_results = response.json()
        found_recipe = next((r for r in search_results["items"] if r["id"] == recipe_id), None)
        assert found_recipe is not None
        assert found_recipe["rating"] == 3.5
        
        # Verify rating in paginated results
        response = client.get("/api/recipes")
        assert response.status_code == 200
        
        paginated_results = response.json()
        found_recipe = next((r for r in paginated_results["items"] if r["id"] == recipe_id), None)
        assert found_recipe is not None
        assert found_recipe["rating"] == 3.5
        
        # Step 4: Use recipe in meal plan
        meal_plan_data = {
            "name": "Consistency Test Plan",
            "recipes": {
                "Monday": [recipe_id],
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
        
        meal_plan = response.json()
        meal_plan_id = meal_plan["id"]
        
        # Verify meal plan contains correct recipe
        assert meal_plan["recipes"]["Monday"] == [recipe_id]
        
        # Step 5: Verify recipe still exists and is consistent
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        
        final_recipe = response.json()
        assert final_recipe["title"] == original_recipe["title"]
        assert final_recipe["rating"] == 3.5
        
        # Step 6: Clean up
        response = client.delete(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
        
        response = client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
    
    def test_error_recovery_workflow(self, client: TestClient):
        """Test error recovery in workflows"""
        # Step 1: Create valid recipe
        recipe_data = {
            "title": "Error Recovery Test",
            "description": "Testing error recovery",
            "instructions": "1. Test error scenarios. 2. Verify recovery.",
            "ingredients": [{"name": "test ingredient", "amount": "1", "unit": "cup"}],
            "difficulty": "Easy"
        }
        
        response = client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        
        recipe_id = response.json()["id"]
        
        # Step 2: Try to create meal plan with invalid recipe ID
        invalid_meal_plan = {
            "name": "Error Test Plan",
            "recipes": {
                "Monday": [recipe_id, 99999],  # One valid, one invalid
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=invalid_meal_plan)
        assert response.status_code == 422  # Should fail validation
        
        # Step 3: Verify original recipe is still intact
        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        
        recipe = response.json()
        assert recipe["title"] == recipe_data["title"]
        
        # Step 4: Create valid meal plan
        valid_meal_plan = {
            "name": "Valid Test Plan",
            "recipes": {
                "Monday": [recipe_id],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []
            }
        }
        
        response = client.post("/api/meal-plans", json=valid_meal_plan)
        assert response.status_code == 200
        
        meal_plan_id = response.json()["id"]
        
        # Step 5: Try to delete recipe that's in meal plan (should work)
        response = client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        
        # Step 6: Verify meal plan handles missing recipe gracefully
        response = client.get(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
        
        # Clean up
        response = client.delete(f"/api/meal-plans/{meal_plan_id}")
        assert response.status_code == 200
    
    def test_bulk_operations_integration(self, client: TestClient):
        """Test bulk operations and their integration"""
        # Step 1: Create multiple recipes in bulk
        recipes_data = []
        for i in range(15):
            recipe_data = {
                "title": f"Bulk Recipe {i+1}",
                "description": f"Recipe {i+1} for bulk testing",
                "instructions": f"1. Prepare bulk recipe {i+1}. 2. Cook. 3. Serve.",
                "ingredients": [{"name": f"ingredient_{i+1}", "amount": str(i+1), "unit": "cup"}],
                "prep_time": 10 + i,
                "cook_time": 20 + i,
                "servings": (i % 4) + 2,
                "difficulty": ["Easy", "Medium", "Hard"][i % 3]
            }
            recipes_data.append(recipe_data)
        
        created_recipes = []
        for recipe_data in recipes_data:
            response = client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 200
            created_recipes.append(response.json())
        
        # Step 2: Verify all recipes were created
        response = client.get("/api/recipes")
        assert response.status_code == 200
        
        all_recipes = response.json()
        assert all_recipes["total"] == 15
        
        # Step 3: Test bulk search
        response = client.get("/api/recipes/search", params={"q": "bulk"})
        assert response.status_code == 200
        
        search_results = response.json()
        assert search_results["total"] == 15
        
        # Step 4: Create meal plans using bulk recipes
        recipe_ids = [r["id"] for r in created_recipes]
        
        meal_plans_data = []
        for i in range(3):
            meal_plan_data = {
                "name": f"Bulk Meal Plan {i+1}",
                "recipes": {
                    "Monday": recipe_ids[i*3:(i+1)*3],
                    "Tuesday": recipe_ids[(i+1)*3:(i+2)*3],
                    "Wednesday": [],
                    "Thursday": [],
                    "Friday": [],
                    "Saturday": [],
                    "Sunday": []
                }
            }
            meal_plans_data.append(meal_plan_data)
        
        created_meal_plans = []
        for meal_plan_data in meal_plans_data:
            response = client.post("/api/meal-plans", json=meal_plan_data)
            assert response.status_code == 200
            created_meal_plans.append(response.json())
        
        # Step 5: Verify meal plans
        response = client.get("/api/meal-plans")
        assert response.status_code == 200
        
        all_meal_plans = response.json()
        assert all_meal_plans["total"] == 3
        
        # Step 6: Clean up in bulk
        for meal_plan in created_meal_plans:
            response = client.delete(f"/api/meal-plans/{meal_plan['id']}")
            assert response.status_code == 200
        
        for recipe in created_recipes:
            response = client.delete(f"/api/recipes/{recipe['id']}")
            assert response.status_code == 200
        
        # Step 7: Verify cleanup
        response = client.get("/api/recipes")
        assert response.status_code == 200
        assert response.json()["total"] == 0
        
        response = client.get("/api/meal-plans")
        assert response.status_code == 200
        assert response.json()["total"] == 0

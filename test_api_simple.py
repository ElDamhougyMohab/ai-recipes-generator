#!/usr/bin/env python3
"""
Simple API Testing Script for AI Recipes Generator
Tests all main API endpoints: POST /api/recipes/generate, GET /api/recipes, POST /api/recipes, DELETE /api/recipes/{id}, GET /api/stats
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return False

def test_recipe_generation():
    """Test POST /api/recipes/generate"""
    print("\n🧪 Testing Recipe Generation (POST /api/recipes/generate)")
    
    test_data = {
        "ingredients": ["chicken", "pasta", "tomatoes", "garlic"],
        "meal_type": "dinner",
        "dietary_preferences": [],
        "cuisine_type": "Italian"
    }
    
    try:
        response = requests.post(f"{API_BASE}/recipes/generate", json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recipe generation successful!")
            print(f"   Generated {len(data.get('recipes', []))} recipes")
            
            if data.get('recipes'):
                first_recipe = data['recipes'][0]
                print(f"   First recipe: {first_recipe.get('title', 'N/A')}")
                print(f"   Difficulty: {first_recipe.get('difficulty', 'N/A')}")
                print(f"   Prep time: {first_recipe.get('prep_time', 'N/A')} min")
            
            return data
        else:
            print(f"❌ Recipe generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Recipe generation error: {str(e)}")
        return None

def test_get_recipes():
    """Test GET /api/recipes"""
    print("\n🧪 Testing Get All Recipes (GET /api/recipes)")
    
    try:
        response = requests.get(f"{API_BASE}/recipes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get recipes successful!")
            print(f"   Total recipes found: {len(data)}")
            
            if data:
                print("   Sample recipes:")
                try:
                    for i, recipe in enumerate(data[:3]):  # Show first 3
                        print(f"   {i+1}. {recipe.get('title', 'N/A')} (ID: {recipe.get('id', 'N/A')})")
                except Exception as e:
                    print(f"   Error displaying recipes: {str(e)}")
            
            return data
        else:
            print(f"❌ Get recipes failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Get recipes error: {str(e)}")
        return None

def test_create_recipe():
    """Test POST /api/recipes"""
    print("\n🧪 Testing Create Recipe (POST /api/recipes)")
    
    test_recipe = {
        "title": "Test Spaghetti Carbonara",
        "description": "A classic Italian pasta dish with eggs, cheese, and pancetta",
        "instructions": "1. Cook spaghetti according to package directions. 2. Mix eggs and cheese in a bowl. 3. Cook pancetta until crispy. 4. Combine all ingredients while pasta is hot.",
        "ingredients": [
            {"name": "spaghetti", "amount": "400", "unit": "g"},
            {"name": "eggs", "amount": "4", "unit": "large"},
            {"name": "parmesan cheese", "amount": "100", "unit": "g"},
            {"name": "pancetta", "amount": "150", "unit": "g"}
        ],
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "difficulty": "Medium",
        "cuisine_type": "Italian"
    }
    
    try:
        response = requests.post(f"{API_BASE}/recipes", json=test_recipe)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recipe creation successful!")
            print(f"   Created recipe ID: {data.get('id')}")
            print(f"   Title: {data.get('title')}")
            print(f"   Difficulty: {data.get('difficulty')}")
            
            return data
        else:
            print(f"❌ Recipe creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Recipe creation error: {str(e)}")
        return None

def test_delete_recipe(recipe_id: int):
    """Test DELETE /api/recipes/{id}"""
    print(f"\n🧪 Testing Delete Recipe (DELETE /api/recipes/{recipe_id})")
    
    try:
        response = requests.delete(f"{API_BASE}/recipes/{recipe_id}")
        
        if response.status_code == 200:
            print(f"✅ Recipe deletion successful!")
            print(f"   Deleted recipe ID: {recipe_id}")
            return True
        elif response.status_code == 404:
            print(f"❌ Recipe not found: {recipe_id}")
            return False
        else:
            print(f"❌ Recipe deletion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Recipe deletion error: {str(e)}")
        return False

def test_get_stats():
    """Test GET /api/stats"""
    print("\n🧪 Testing Get Stats (GET /api/stats)")
    
    try:
        response = requests.get(f"{API_BASE}/stats")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get stats successful!")
            print(f"   Total recipes: {data.get('total_recipes', 'N/A')}")
            print(f"   Average rating: {data.get('average_rating', 'N/A')}")
            print(f"   Most popular cuisine: {data.get('most_popular_cuisine', 'N/A')}")
            print(f"   Recent generations: {data.get('recent_generations', 'N/A')}")
            
            return data
        else:
            print(f"❌ Get stats failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Get stats error: {str(e)}")
        return None

def run_full_test_suite():
    """Run all API tests in sequence"""
    print("🚀 Starting API Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\n❌ Cannot proceed with tests. Please start the API server first.")
        print("Run: docker-compose up -d")
        return
    
    results = {}
    
    # Test 1: Recipe Generation
    results['generation'] = test_recipe_generation()
    
    # Test 2: Get All Recipes (before creating new ones)
    results['get_recipes_before'] = test_get_recipes()
    
    # Test 3: Create Recipe
    results['create_recipe'] = test_create_recipe()
    created_recipe_id = results['create_recipe'].get('id') if results['create_recipe'] else None
    
    # Test 4: Get All Recipes (after creating new one)
    results['get_recipes_after'] = test_get_recipes()
    
    # Test 5: Get Stats
    results['stats'] = test_get_stats()
    
    # Test 6: Delete Recipe (if we created one)
    if created_recipe_id:
        results['delete_recipe'] = test_delete_recipe(created_recipe_id)
        
        # Verify deletion by getting recipes again
        print("\n🧪 Verifying deletion...")
        final_recipes = test_get_recipes()
        if final_recipes:
            deleted_successfully = not any(r.get('id') == created_recipe_id for r in final_recipes)
            if deleted_successfully:
                print("✅ Recipe deletion verified!")
            else:
                print("❌ Recipe still exists after deletion")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    tests = [
        ("Recipe Generation", results.get('generation') is not None),
        ("Get Recipes", results.get('get_recipes_before') is not None),
        ("Create Recipe", results.get('create_recipe') is not None),
        ("Get Stats", results.get('stats') is not None),
        ("Delete Recipe", results.get('delete_recipe', False))
    ]
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
        total += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    run_full_test_suite()

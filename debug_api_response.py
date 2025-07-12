#!/usr/bin/env python3
"""
Debug the exact format of the API response
"""
import requests
import json

def debug_api_response():
    print("🔍 DEBUG: API RESPONSE FORMAT")
    print("=" * 50)
    
    recipe_data = {
        "ingredients": ["chicken", "rice"],
        "dietary_restrictions": [],
        "cuisine_type": "american",
        "meal_type": "dinner"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/recipes/generate", json=recipe_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recipes = data.get("recipes", [])
            
            if recipes:
                first_recipe = recipes[0]
                print(f"\nFirst recipe title: {first_recipe.get('title', 'N/A')}")
                
                # Check instructions format
                instructions = first_recipe.get("instructions")
                print(f"\nInstructions raw type: {type(instructions)}")
                print(f"Instructions value: {instructions}")
                
                if isinstance(instructions, list):
                    print(f"✅ Instructions is a list with {len(instructions)} items")
                    for i, step in enumerate(instructions):
                        print(f"   Step {i+1}: {step}")
                elif isinstance(instructions, str):
                    print(f"✅ Instructions is a string: {instructions[:100]}...")
                else:
                    print(f"❌ Instructions is neither list nor string: {type(instructions)}")
                    
            print(f"\n🔍 Full JSON structure:")
            print(json.dumps(data, indent=2)[:1000] + "...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_api_response()

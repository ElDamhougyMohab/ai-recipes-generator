#!/usr/bin/env python3
"""
Test script for async LLM implementation
Run this to verify that async operations are working correctly
"""

import asyncio
import time
import logging
from backend.app.services.gemini_service import GeminiService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_single_generation():
    """Test single async recipe generation"""
    print("🧪 Testing single recipe generation...")
    
    async with GeminiService() as service:
        start_time = time.time()
        
        recipes = await service.generate_recipes(
            ingredients=["chicken", "rice", "vegetables"],
            dietary_preferences=["gluten-free"],
            cuisine_type="Asian",
            meal_type="dinner"
        )
        
        end_time = time.time()
        
        print(f"✅ Generated {len(recipes)} recipes in {end_time - start_time:.2f} seconds")
        for recipe in recipes:
            print(f"   - {recipe.get('title', 'Untitled Recipe')}")


async def test_concurrent_generation():
    """Test concurrent async recipe generation"""
    print("\n🧪 Testing concurrent recipe generation...")
    
    async with GeminiService() as service:
        # Create multiple tasks
        tasks = [
            service.generate_recipes(
                ingredients=["pasta", "tomatoes", "basil"],
                cuisine_type="Italian"
            ),
            service.generate_recipes(
                ingredients=["beef", "potatoes", "onions"],
                cuisine_type="American"
            ),
            service.generate_recipes(
                ingredients=["salmon", "rice", "soy sauce"],
                cuisine_type="Japanese"
            )
        ]
        
        start_time = time.time()
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        total_recipes = sum(len(result) for result in results)
        print(f"✅ Generated {total_recipes} recipes across {len(tasks)} cuisines in {end_time - start_time:.2f} seconds")
        
        for i, recipes in enumerate(results):
            cuisine = ["Italian", "American", "Japanese"][i]
            print(f"   {cuisine}: {len(recipes)} recipes")


async def test_batch_generation():
    """Test batch recipe generation"""
    print("\n🧪 Testing batch recipe generation...")
    
    requests = [
        {
            'ingredients': ['chicken', 'broccoli'],
            'cuisine_type': 'Chinese'
        },
        {
            'ingredients': ['beans', 'rice'],
            'dietary_preferences': ['vegetarian'],
            'cuisine_type': 'Mexican'
        },
        {
            'ingredients': ['fish', 'lemon'],
            'cuisine_type': 'Mediterranean'
        }
    ]
    
    async with GeminiService() as service:
        start_time = time.time()
        
        results = await service.generate_multiple_recipes(requests)
        
        end_time = time.time()
        
        total_recipes = sum(len(result) for result in results)
        print(f"✅ Batch generated {total_recipes} recipes in {end_time - start_time:.2f} seconds")


async def test_timeout_handling():
    """Test timeout handling"""
    print("\n🧪 Testing timeout handling...")
    
    async with GeminiService() as service:
        try:
            recipes = await service.generate_recipes(
                ingredients=["test"],
                timeout=1  # Very short timeout to trigger fallback
            )
            print(f"✅ Handled timeout gracefully, got {len(recipes)} fallback recipes")
        except Exception as e:
            print(f"❌ Timeout handling failed: {e}")


async def main():
    """Run all async tests"""
    print("🚀 Testing Async LLM Implementation")
    print("=" * 50)
    
    try:
        await test_single_generation()
        await test_concurrent_generation()
        await test_batch_generation()
        await test_timeout_handling()
        
        print("\n" + "=" * 50)
        print("✅ All async tests completed successfully!")
        print("🎉 Async LLM implementation is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async tests
    asyncio.run(main())

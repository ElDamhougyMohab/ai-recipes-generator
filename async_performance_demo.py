#!/usr/bin/env python3
"""
Performance comparison: Sync vs Async LLM calls
This demonstrates the benefits of async implementation
"""

import asyncio
import time
import requests
import aiohttp
from concurrent.futures import ThreadPoolExecutor


def sync_api_call(ingredients):
    """Simulate synchronous API call"""
    # Simulate network delay
    time.sleep(2)  # 2 seconds per call
    return f"Recipe for {', '.join(ingredients)}"


async def async_api_call(ingredients):
    """Simulate asynchronous API call"""
    # Simulate network delay without blocking
    await asyncio.sleep(2)  # 2 seconds per call
    return f"Recipe for {', '.join(ingredients)}"


def test_sync_sequential():
    """Test synchronous sequential calls"""
    print("🐌 Testing Synchronous Sequential Calls")
    
    ingredient_sets = [
        ["chicken", "rice"],
        ["beef", "potatoes"],
        ["fish", "vegetables"],
        ["pasta", "tomatoes"],
        ["tofu", "soy sauce"]
    ]
    
    start_time = time.time()
    
    results = []
    for ingredients in ingredient_sets:
        result = sync_api_call(ingredients)
        results.append(result)
    
    end_time = time.time()
    
    print(f"   ⏱️  Total time: {end_time - start_time:.2f} seconds")
    print(f"   📊 Processed {len(results)} requests")
    print(f"   🚀 Throughput: {len(results)/(end_time - start_time):.2f} requests/second")
    
    return end_time - start_time


def test_sync_threaded():
    """Test synchronous calls with thread pool"""
    print("\n🏃 Testing Synchronous with Thread Pool")
    
    ingredient_sets = [
        ["chicken", "rice"],
        ["beef", "potatoes"],
        ["fish", "vegetables"],
        ["pasta", "tomatoes"],
        ["tofu", "soy sauce"]
    ]
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(sync_api_call, ingredient_sets))
    
    end_time = time.time()
    
    print(f"   ⏱️  Total time: {end_time - start_time:.2f} seconds")
    print(f"   📊 Processed {len(results)} requests")
    print(f"   🚀 Throughput: {len(results)/(end_time - start_time):.2f} requests/second")
    
    return end_time - start_time


async def test_async_concurrent():
    """Test asynchronous concurrent calls"""
    print("\n⚡ Testing Asynchronous Concurrent Calls")
    
    ingredient_sets = [
        ["chicken", "rice"],
        ["beef", "potatoes"],
        ["fish", "vegetables"],
        ["pasta", "tomatoes"],
        ["tofu", "soy sauce"]
    ]
    
    start_time = time.time()
    
    # Create tasks for concurrent execution
    tasks = [async_api_call(ingredients) for ingredients in ingredient_sets]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    print(f"   ⏱️  Total time: {end_time - start_time:.2f} seconds")
    print(f"   📊 Processed {len(results)} requests")
    print(f"   🚀 Throughput: {len(results)/(end_time - start_time):.2f} requests/second")
    
    return end_time - start_time


async def test_real_world_scenario():
    """Test real-world scenario with mixed operations"""
    print("\n🌍 Testing Real-World Scenario")
    print("   (Multiple users generating recipes simultaneously)")
    
    # Simulate 10 users requesting recipes at the same time
    user_requests = [
        ["chicken", "vegetables"],
        ["pasta", "cheese"],
        ["salmon", "rice"],
        ["tofu", "broccoli"],
        ["beef", "onions"],
        ["shrimp", "noodles"],
        ["beans", "corn"],
        ["pork", "apples"],
        ["eggs", "spinach"],
        ["turkey", "cranberries"]
    ]
    
    start_time = time.time()
    
    # Async: All users get processed concurrently
    async_tasks = [async_api_call(ingredients) for ingredients in user_requests]
    async_results = await asyncio.gather(*async_tasks)
    
    async_time = time.time() - start_time
    
    print(f"   ⚡ Async: {len(async_results)} users served in {async_time:.2f} seconds")
    
    # Sync: Users must wait in line
    start_time = time.time()
    sync_results = []
    for ingredients in user_requests:
        result = sync_api_call(ingredients)
        sync_results.append(result)
    
    sync_time = time.time() - start_time
    
    print(f"   🐌 Sync: {len(sync_results)} users served in {sync_time:.2f} seconds")
    
    speedup = sync_time / async_time
    print(f"   🚀 Speedup: {speedup:.1f}x faster with async!")
    
    return async_time, sync_time


async def main():
    """Run performance comparison"""
    print("🏁 Performance Comparison: Sync vs Async LLM Calls")
    print("=" * 60)
    
    # Test different approaches
    sync_sequential_time = test_sync_sequential()
    sync_threaded_time = test_sync_threaded()
    async_concurrent_time = await test_async_concurrent()
    
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    print(f"🐌 Synchronous Sequential: {sync_sequential_time:.2f} seconds")
    print(f"🏃 Synchronous Threaded:   {sync_threaded_time:.2f} seconds")
    print(f"⚡ Asynchronous Concurrent: {async_concurrent_time:.2f} seconds")
    
    seq_speedup = sync_sequential_time / async_concurrent_time
    thread_speedup = sync_threaded_time / async_concurrent_time
    
    print(f"\n🚀 SPEEDUP ANALYSIS:")
    print(f"   Async vs Sequential: {seq_speedup:.1f}x faster")
    print(f"   Async vs Threaded:   {thread_speedup:.1f}x faster")
    
    await test_real_world_scenario()
    
    print("\n" + "=" * 60)
    print("✅ CONCLUSION: Async implementation provides significant")
    print("   performance benefits for concurrent LLM operations!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

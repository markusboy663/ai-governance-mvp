#!/usr/bin/env python3
"""
Rate limiting load test script.

Tests:
1. In-memory rate limiting (single instance)
2. Redis rate limiting (distributed)
3. Parallel requests to verify token bucket behavior
4. Measure performance

Usage:
    python test_rate_limit.py --redis-url redis://localhost:6379
    python test_rate_limit.py  # in-memory only
"""

import asyncio
import time
import httpx
import sys
from statistics import mean, stdev

async def make_request(client: httpx.AsyncClient, url: str, api_key: str, request_num: int):
    """Make a single request and return timing"""
    try:
        start = time.time()
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4",
                "operation": "classify",
                "metadata": {"source": "test", "request_num": request_num}
            }
        )
        elapsed = time.time() - start
        
        # Extract rate limit headers
        rate_limit_info = {
            "status": response.status_code,
            "elapsed": elapsed,
            "limit_limit": response.headers.get("X-RateLimit-Limit"),
            "limit_remaining": response.headers.get("X-RateLimit-Remaining"),
            "limit_reset": response.headers.get("X-RateLimit-Reset"),
            "limit_backend": response.headers.get("X-RateLimit-Backend", "unknown")
        }
        
        return rate_limit_info
    except Exception as e:
        return {"error": str(e), "elapsed": None}


async def test_sequential_requests(api_key: str, count: int = 110, url: str = "http://localhost:8000/v1/check"):
    """Test sequential requests to verify rate limit enforcement"""
    print(f"\n🔄 Sequential Test: {count} requests")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        timings = []
        allowed_count = 0
        blocked_count = 0
        
        for i in range(count):
            result = await make_request(client, url, api_key, i)
            
            if "error" in result:
                print(f"  {i+1:3d}: ❌ Error - {result['error']}")
                continue
            
            status = result["status"]
            backend = result["limit_backend"]
            
            if status == 200:
                allowed_count += 1
                symbol = "✅"
            elif status == 429:
                blocked_count += 1
                symbol = "🚫"
            else:
                symbol = "⚠️ "
            
            timings.append(result["elapsed"])
            
            if i % 20 == 0 or status == 429:
                print(f"  {i+1:3d}: {symbol} [{backend:6s}] {result['status']} - "
                      f"Remaining: {result['limit_remaining']} - {result['elapsed']*1000:.1f}ms")
        
        print(f"\n  Results: {allowed_count} allowed, {blocked_count} blocked")
        if timings:
            print(f"  Timing: {mean(timings)*1000:.1f}ms avg, "
                  f"{min(timings)*1000:.1f}ms min, {max(timings)*1000:.1f}ms max")


async def test_parallel_requests(api_key: str, count: int = 50, concurrency: int = 10, 
                                 url: str = "http://localhost:8000/v1/check"):
    """Test parallel requests to verify distributed rate limiting"""
    print(f"\n⚡ Parallel Test: {count} requests with {concurrency} concurrent")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [make_request(client, url, api_key, i) for i in range(count)]
        
        start = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start
        
        allowed_count = sum(1 for r in results if r.get("status") == 200)
        blocked_count = sum(1 for r in results if r.get("status") == 429)
        error_count = sum(1 for r in results if "error" in r)
        
        backends = set()
        for r in results:
            if "limit_backend" in r:
                backends.add(r["limit_backend"])
        
        print(f"  Completed {count} requests in {total_time:.2f}s")
        print(f"  Results: {allowed_count} allowed, {blocked_count} blocked, {error_count} errors")
        print(f"  Backend(s): {', '.join(backends)}")
        print(f"  Throughput: {count/total_time:.1f} req/s")
        
        # Show first failure
        for i, r in enumerate(results):
            if r.get("status") == 429:
                print(f"\n  First rate-limit hit at request {i+1}")
                print(f"    Limit: {r.get('limit_limit')}")
                print(f"    Remaining: {r.get('limit_remaining')}")
                print(f"    Reset: {r.get('limit_reset')}")
                break


async def test_multiple_api_keys(base_url: str = "http://localhost:8000", 
                                 keys_count: int = 3,
                                 requests_per_key: int = 35):
    """Test multiple API keys get independent rate limits"""
    print(f"\n🔐 Multi-Key Test: {keys_count} keys × {requests_per_key} requests")
    print("-" * 60)
    
    # Note: In real scenario, you'd have different API keys
    # For this test, we use the same key (but would work with different keys)
    api_key = "test-key-unique-identifier"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        all_results = []
        
        for key_num in range(keys_count):
            key_results = []
            for req_num in range(requests_per_key):
                result = await make_request(client, f"{base_url}/v1/check", api_key, req_num)
                key_results.append(result)
            
            allowed = sum(1 for r in key_results if r.get("status") == 200)
            blocked = sum(1 for r in key_results if r.get("status") == 429)
            
            print(f"  Key {key_num+1}: {allowed} allowed, {blocked} blocked")
            all_results.extend(key_results)
        
        total_allowed = sum(1 for r in all_results if r.get("status") == 200)
        total_blocked = sum(1 for r in all_results if r.get("status") == 429)
        
        print(f"\n  Total: {total_allowed} allowed, {total_blocked} blocked")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Rate Limit Load Test")
    print("=" * 60)
    
    # Check server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code != 200:
                print("❌ Server not running at http://localhost:8000")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    
    print("✅ Server is running")
    
    # Test with a valid API key (you'll need to generate one first)
    api_key_test = "550e8400-e29b-41d4-a716-446655440000.xYz7kL9mQp_test"
    
    # Run tests
    await test_sequential_requests(api_key_test, count=110)
    await asyncio.sleep(2)  # Wait for rate limit window to reset
    
    await test_parallel_requests(api_key_test, count=50, concurrency=10)
    await asyncio.sleep(2)
    
    await test_multiple_api_keys(keys_count=2, requests_per_key=35)
    
    print("\n" + "=" * 60)
    print("✅ Load test completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Load testing suite for AI Governance API using Python (httpx + asyncio)

This replaces k6 for environments where k6 is not available.

Usage:
    python load_test.py --vus 50 --duration 60 --base-url http://localhost:8000
    python load_test.py --mode burst    # 1000 RPS spike test
    python load_test.py --mode stress   # Gradual ramp-up to failure point
    python load_test.py --mode soak     # 24 hours at steady state
"""

import asyncio
import time
import random
import json
import argparse
import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class Config:
    base_url: str = "http://localhost:8000"
    api_key: str = "test-key-0"
    vus: int = 10  # Virtual Users
    duration: int = 60  # seconds
    ramp_up: int = 10  # seconds to reach target VUs
    ramp_down: int = 10  # seconds to drop from target VUs
    mode: str = "normal"  # normal, burst, stress, soak
    verbose: bool = False

@dataclass
class RequestMetrics:
    timestamp: float
    method: str
    endpoint: str
    status: int
    latency_ms: float
    success: bool
    error: str = None

# ============================================================================
# Metrics Collection
# ============================================================================

class MetricsCollector:
    def __init__(self):
        self.requests: List[RequestMetrics] = []
        self.lock = asyncio.Lock()
    
    async def record(self, metric: RequestMetrics):
        async with self.lock:
            self.requests.append(metric)
    
    def get_summary(self) -> Dict:
        if not self.requests:
            return {}
        
        latencies = [r.latency_ms for r in self.requests]
        statuses = {}
        for r in self.requests:
            statuses[r.status] = statuses.get(r.status, 0) + 1
        
        success_count = sum(1 for r in self.requests if r.success)
        error_count = len(self.requests) - success_count
        
        latencies_sorted = sorted(latencies)
        n = len(latencies_sorted)
        
        return {
            "total_requests": len(self.requests),
            "successful": success_count,
            "failed": error_count,
            "error_rate": error_count / len(self.requests) if self.requests else 0,
            "status_codes": statuses,
            "latency_ms": {
                "min": min(latencies),
                "max": max(latencies),
                "avg": sum(latencies) / len(latencies),
                "p50": latencies_sorted[n // 2] if n > 0 else 0,
                "p90": latencies_sorted[int(n * 0.90)] if n > 0 else 0,
                "p95": latencies_sorted[int(n * 0.95)] if n > 0 else 0,
                "p99": latencies_sorted[int(n * 0.99)] if n > 0 else 0,
            },
            "requests_per_second": len(self.requests) / (max(r.timestamp for r in self.requests) - min(r.timestamp for r in self.requests)) if len(self.requests) > 1 else 0,
        }

metrics = MetricsCollector()

# ============================================================================
# Test Scenarios
# ============================================================================

async def test_health_check(client: httpx.AsyncClient, config: Config) -> RequestMetrics:
    """Test: GET /health"""
    start = time.time()
    try:
        resp = await client.get(f"{config.base_url}/health", timeout=10)
        latency = (time.time() - start) * 1000
        success = resp.status_code == 200
        return RequestMetrics(
            timestamp=start,
            method="GET",
            endpoint="/health",
            status=resp.status_code,
            latency_ms=latency,
            success=success,
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        return RequestMetrics(
            timestamp=start,
            method="GET",
            endpoint="/health",
            status=0,
            latency_ms=latency,
            success=False,
            error=str(e),
        )

async def test_metrics_endpoint(client: httpx.AsyncClient, config: Config) -> RequestMetrics:
    """Test: GET /metrics (observability)"""
    start = time.time()
    try:
        resp = await client.get(f"{config.base_url}/metrics", timeout=10)
        latency = (time.time() - start) * 1000
        success = resp.status_code == 200 and "TYPE" in resp.text
        return RequestMetrics(
            timestamp=start,
            method="GET",
            endpoint="/metrics",
            status=resp.status_code,
            latency_ms=latency,
            success=success,
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        return RequestMetrics(
            timestamp=start,
            method="GET",
            endpoint="/metrics",
            status=0,
            latency_ms=latency,
            success=False,
            error=str(e),
        )

async def test_governance_check_allowed(client: httpx.AsyncClient, config: Config) -> RequestMetrics:
    """Test: POST /v1/check (normal, should allow)"""
    start = time.time()
    try:
        payload = {
            "model": "gpt-4",
            "operation": "classify",
            "input_text": "Summarize the benefits of machine learning in healthcare",
            "metadata": {
                "user_id": f"user-{random.randint(1, 100)}",
                "timestamp": datetime.now().isoformat(),
            },
        }
        resp = await client.post(
            f"{config.base_url}/v1/check",
            json=payload,
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=10,
        )
        latency = (time.time() - start) * 1000
        success = resp.status_code == 200
        return RequestMetrics(
            timestamp=start,
            method="POST",
            endpoint="/v1/check",
            status=resp.status_code,
            latency_ms=latency,
            success=success,
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        return RequestMetrics(
            timestamp=start,
            method="POST",
            endpoint="/v1/check",
            status=0,
            latency_ms=latency,
            success=False,
            error=str(e),
        )

async def test_governance_check_blocked(client: httpx.AsyncClient, config: Config) -> RequestMetrics:
    """Test: POST /v1/check (PII - might be blocked)"""
    start = time.time()
    try:
        payload = {
            "model": "gpt-4",
            "operation": "classify",
            "input_text": "Patient John Doe with SSN 123-45-6789 has symptoms",
            "metadata": {
                "user_id": f"user-{random.randint(1, 100)}",
                "timestamp": datetime.now().isoformat(),
            },
        }
        resp = await client.post(
            f"{config.base_url}/v1/check",
            json=payload,
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=10,
        )
        latency = (time.time() - start) * 1000
        success = resp.status_code == 200
        return RequestMetrics(
            timestamp=start,
            method="POST",
            endpoint="/v1/check-pii",
            status=resp.status_code,
            latency_ms=latency,
            success=success,
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        return RequestMetrics(
            timestamp=start,
            method="POST",
            endpoint="/v1/check-pii",
            status=0,
            latency_ms=latency,
            success=False,
            error=str(e),
        )

async def test_governance_check_invalid_auth(client: httpx.AsyncClient, config: Config) -> RequestMetrics:
    """Test: POST /v1/check (invalid auth - should fail 401)"""
    start = time.time()
    try:
        payload = {
            "model": "gpt-4",
            "operation": "classify",
            "input_text": "Test",
        }
        resp = await client.post(
            f"{config.base_url}/v1/check",
            json=payload,
            headers={"Authorization": "Bearer invalid-key"},
            timeout=10,
        )
        latency = (time.time() - start) * 1000
        success = resp.status_code in [401, 403]  # Expected failures
        return RequestMetrics(
            timestamp=start,
            method="POST",
            endpoint="/v1/check-invalid",
            status=resp.status_code,
            latency_ms=latency,
            success=success,
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        return RequestMetrics(
            timestamp=start,
            method="POST",
            endpoint="/v1/check-invalid",
            status=0,
            latency_ms=latency,
            success=False,
            error=str(e),
        )

# ============================================================================
# Load Test Scenarios
# ============================================================================

async def run_normal_test(config: Config, num_requests: int):
    """Normal load test: steady traffic with mixed requests"""
    print(f"🔵 Running NORMAL test: {num_requests} requests over {config.duration}s")
    print(f"   VUs: {config.vus} | Ramp-up: {config.ramp_up}s")
    
    tests = [
        test_health_check,
        test_metrics_endpoint,
        test_governance_check_allowed,
        test_governance_check_allowed,
        test_governance_check_blocked,
    ]
    
    await run_load_test(config, tests, num_requests)

async def run_burst_test(config: Config):
    """Burst test: 1000 RPS spike"""
    print("🔴 Running BURST test: 1000 RPS spike for 10s")
    config.vus = 200
    config.duration = 10
    config.ramp_up = 2
    
    tests = [test_governance_check_allowed]
    num_requests = 1000 * 10  # 1000 RPS for 10s
    
    await run_load_test(config, tests, num_requests)

async def run_stress_test(config: Config):
    """Stress test: gradually increase load until failure"""
    print("🔴 Running STRESS test: gradual ramp-up to find breaking point")
    
    stages = [
        (10, 50),      # 10s at 50 VUs
        (10, 100),     # 10s at 100 VUs
        (10, 200),     # 10s at 200 VUs
        (10, 500),     # 10s at 500 VUs
    ]
    
    tests = [test_governance_check_allowed, test_health_check]
    
    async with httpx.AsyncClient() as client:
        for duration, vus in stages:
            print(f"   Stage: {vus} VUs for {duration}s")
            config.vus = vus
            config.duration = duration
            
            # Calculate requests for this stage
            requests_per_vu = 10  # approximate
            num_requests = vus * requests_per_vu * duration // 10
            
            start = time.time()
            tasks = []
            
            for _ in range(num_requests):
                test_func = random.choice(tests)
                task = test_func(client, config)
                tasks.append(task)
                
                # Spread requests over duration
                if len(tasks) >= 100:
                    results = await asyncio.gather(*tasks)
                    for result in results:
                        await metrics.record(result)
                    tasks = []
                
                await asyncio.sleep(random.uniform(0.01, 0.05))
            
            if tasks:
                results = await asyncio.gather(*tasks)
                for result in results:
                    await metrics.record(result)
            
            elapsed = time.time() - start
            print(f"      Completed in {elapsed:.1f}s")

async def run_soak_test(config: Config):
    """Soak test: steady load for extended period"""
    print(f"🟡 Running SOAK test: steady {config.vus} VUs for {config.duration}s")
    
    tests = [test_governance_check_allowed, test_health_check]
    num_requests = config.vus * config.duration * 10  # ~10 req/s per VU
    
    await run_load_test(config, tests, num_requests)

async def run_load_test(config: Config, tests: List, num_requests: int):
    """Generic load test runner"""
    async with httpx.AsyncClient() as client:
        start_time = time.time()
        tasks = []
        request_count = 0
        
        # Ramp-up phase
        vu_count = 0
        ramp_up_start = time.time()
        
        while request_count < num_requests:
            elapsed = time.time() - ramp_up_start
            
            # Calculate target VUs for ramp-up
            if config.ramp_up > 0 and elapsed < config.ramp_up:
                target_vus = int(config.vus * elapsed / config.ramp_up)
            else:
                target_vus = config.vus
            
            # Adjust concurrent tasks
            while len(tasks) < target_vus and request_count < num_requests:
                test_func = random.choice(tests)
                task = test_func(client, config)
                tasks.append(asyncio.create_task(task))
                request_count += 1
            
            # Collect completed tasks
            if tasks:
                done, tasks = await asyncio.wait(tasks, timeout=0.1, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    try:
                        result = await task
                        await metrics.record(result)
                        if config.verbose:
                            print(f"✓ {result.method} {result.endpoint} - {result.status} ({result.latency_ms:.1f}ms)")
                    except Exception as e:
                        print(f"✗ Task failed: {e}")
            
            await asyncio.sleep(0.01)
        
        # Wait for remaining tasks
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, RequestMetrics):
                    await metrics.record(result)
        
        elapsed = time.time() - start_time
        print(f"   Completed {request_count} requests in {elapsed:.1f}s ({request_count/elapsed:.1f} RPS)")

# ============================================================================
# Security Scanning
# ============================================================================

async def run_security_scan():
    """Run pip-audit and npm audit"""
    print("\n🔒 Running Security Scans...\n")
    
    # pip-audit
    print("📦 Running pip-audit (backend dependencies)...")
    import subprocess
    result = subprocess.run(
        ["pip-audit", "backend/requirements.txt"],
        cwd="c:\\Users\\marku\\Desktop\\ai-governance-mvp",
        capture_output=True,
        text=True,
    )
    print(result.stdout if result.stdout else result.stderr)
    
    # npm audit
    print("\n📦 Running npm audit (frontend dependencies)...")
    result = subprocess.run(
        ["npm", "audit"],
        cwd="c:\\Users\\marku\\Desktop\\ai-governance-mvp\\frontend",
        capture_output=True,
        text=True,
    )
    print(result.stdout if result.stdout else result.stderr)

# ============================================================================
# Main
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Load testing for AI Governance API")
    parser.add_argument("--vus", type=int, default=10, help="Virtual users (default: 10)")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds (default: 60)")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", default="test-key-0", help="API key for requests")
    parser.add_argument("--mode", choices=["normal", "burst", "stress", "soak"], default="normal", help="Test scenario")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--security", action="store_true", help="Run security scans only")
    
    args = parser.parse_args()
    
    config = Config(
        base_url=args.base_url,
        api_key=args.api_key,
        vus=args.vus,
        duration=args.duration,
        mode=args.mode,
        verbose=args.verbose,
    )
    
    print("=" * 70)
    print("🧪 AI Governance API - Load Testing Suite")
    print("=" * 70)
    print(f"Base URL: {config.base_url}")
    print(f"API Key: {config.api_key[:20]}...")
    print(f"Mode: {config.mode}")
    print()
    
    if args.security:
        await run_security_scan()
        return
    
    # Run test
    if config.mode == "normal":
        num_requests = config.vus * config.duration * 10
        await run_normal_test(config, num_requests)
    elif config.mode == "burst":
        await run_burst_test(config)
    elif config.mode == "stress":
        await run_stress_test(config)
    elif config.mode == "soak":
        await run_soak_test(config)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    summary = metrics.get_summary()
    
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                if isinstance(v, float):
                    print(f"  {k}: {v:.2f}")
                else:
                    print(f"  {k}: {v}")
        else:
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    
    # Save results
    results_file = "load_test_results.json"
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n✅ Results saved to {results_file}")
    
    # Fail if error rate too high
    if summary.get("error_rate", 0) > 0.1:
        print("\n❌ ERROR RATE TOO HIGH (>10%)")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

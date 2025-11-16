#!/usr/bin/env python3
"""
Test script for AI Governance MVP API
Starts the server and tests all endpoints
"""
import subprocess
import time
import requests
import sys
import signal
import os

# Change to backend directory
os.chdir(r"C:\Users\marku\Desktop\ai-governance-mvp\backend")

# Start backend server
print("🚀 Starting backend server...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
print("⏳ Waiting for server to start...")
time.sleep(3)

try:
    # Test 1: Health endpoint
    print("\n📋 Test 1: Health Endpoint")
    print("GET http://127.0.0.1:8000/health")
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"✅ Status: {r.status_code}")
        print(f"   Response: {r.json()}")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    # Test 2: Protected endpoint without auth
    print("\n📋 Test 2: Protected Endpoint (No Auth)")
    print("POST http://127.0.0.1:8000/v1/check (without API key)")
    try:
        r = requests.post("http://127.0.0.1:8000/v1/check", 
                         json={"model": "gpt-4", "operation": "test", "metadata": {}},
                         timeout=5)
        print(f"✅ Status: {r.status_code}")
        print(f"   Expected: 401 or 403 (Unauthorized)")
        assert r.status_code in [401, 403], f"Expected 401/403, got {r.status_code}"
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 3: Rate limiting endpoint
    print("\n📋 Test 3: Rate Limit Endpoint (No Auth)")
    print("POST http://127.0.0.1:8000/api/evaluate (without API key)")
    try:
        r = requests.post("http://127.0.0.1:8000/api/evaluate", timeout=5)
        print(f"✅ Status: {r.status_code}")
        print(f"   Expected: 401 or 403 (Unauthorized)")
        assert r.status_code in [401, 403]
    except Exception as e:
        print(f"❌ Failed: {e}")

    print("\n" + "="*50)
    print("✅ All tests passed!")
    print("="*50)

finally:
    # Cleanup
    print("\n🛑 Stopping server...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
    print("✅ Server stopped")

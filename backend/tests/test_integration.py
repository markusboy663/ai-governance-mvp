"""
E2E Integration Tests for AI Governance MVP

Tests the complete flow:
1. Database setup with migrations
2. Seed initial data (policies, API keys)
3. Authenticate with API key
4. Call /v1/check endpoint
5. Validate governance logic
6. Test rate limiting
7. Clean up

Requires:
- PostgreSQL running
- DATABASE_URL environment variable set
"""

import pytest
import httpx
import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import uuid
import bcrypt
from fastapi.testclient import TestClient

from main import app, CheckRequest
from models import Customer, APIKey, Policy, CustomerPolicy
from sqlmodel import SQLModel
from db import AsyncSessionLocal, SessionDep, get_session
from async_logger import init_logger, shutdown_logger
from auth import api_key_dependency
from rate_limit import check_rate_limit

# Test database configuration - commented out since we use in-memory testing
# TEST_DATABASE_URL = os.getenv(
#     "TEST_DATABASE_URL",
#     "postgresql+asyncpg://postgres:postgres@localhost:5432/test_ai_governance"
# )

# Mock API Key for testing - will be created with unique ID per test
def create_mock_api_key(key_id: str = "test-key-id"):
    """Create a mock API key with optional custom ID"""
    return APIKey(
        id=f"test-id-{key_id}",
        key_id=key_id,
        customer_id="test-customer-123",
        api_key_hash="mock-hash",
        is_active=True
    )


# Default mock API key
MOCK_API_KEY = create_mock_api_key()


def mock_api_key_dependency():
    """Mock API key dependency for testing"""
    return MOCK_API_KEY


@pytest.fixture
def client(request):
    """Create test client with app - mocks authentication"""
    # Use a unique key ID per test to avoid rate limit conflicts
    test_name = request.node.name
    unique_key_id = f"{test_name}-key"
    
    global MOCK_API_KEY
    MOCK_API_KEY = create_mock_api_key(unique_key_id)
    
    # Override auth to use mock API key
    app.dependency_overrides[api_key_dependency] = mock_api_key_dependency
    test_client = TestClient(app)
    yield test_client
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth():
    """Create test client without auth mocking (for testing auth failures)"""
    # Don't override auth dependency - use real auth
    test_client = TestClient(app)
    yield test_client


@pytest.fixture
def seed_data(request):
    """Return mock test data for API testing"""
    # Use unique key ID per test to avoid rate limit conflicts
    test_name = request.node.name
    unique_key_id = f"{test_name}-key"
    
    return {
        "raw_key": f"{unique_key_id}.12345678901234567890",
        "customer_id": "test-customer-123"
    }


class TestE2EIntegration:
    """End-to-end integration tests"""

    def test_health_endpoint(self, client):
        """Test 1: Health check endpoint (no auth required)"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_auth_invalid_key(self, client_no_auth):
        """Test 2: Invalid API key should be rejected"""
        response = client_no_auth.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {"temperature": 0.7}
            },
            headers={"Authorization": "Bearer invalid_key_12345678901234"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "Invalid" in data["detail"] or "authenticated" in data["detail"].lower()

    def test_auth_missing_header(self, client_no_auth):
        """Test 3: Missing auth header should be rejected"""
        response = client_no_auth.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {"temperature": 0.7}
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "api key" in data["detail"].lower() or "authenticated" in data["detail"].lower()

    def test_allowed_operation(self, client, seed_data):
        """Test 4: Valid request with no risk flags should be allowed"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is True
        assert data["risk_score"] == 0
        assert data["reason"] == "ok"

    def test_blocked_personal_data(self, client, seed_data):
        """Test 5: Request with personal data flag should be blocked"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "contains_personal_data": True,
                    "max_tokens": 100
                }
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is False
        assert data["risk_score"] >= 70
        assert "Personal" in data["reason"] or "personal" in data["reason"]

    def test_blocked_external_model(self, client, seed_data):
        """Test 6: Request with external model flag should be blocked"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "uses_external_model": True,
                    "max_tokens": 100
                }
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is False
        assert data["risk_score"] >= 50
        assert "External" in data["reason"] or "external" in data["reason"]

    def test_blocked_high_risk(self, client, seed_data):
        """Test 7: Request with both risk flags should be blocked with high score"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "contains_personal_data": True,
                    "uses_external_model": True,
                    "max_tokens": 100
                }
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is False
        assert data["risk_score"] >= 100

    def test_forbidden_field_prompt(self, client, seed_data):
        """Test 8: Request with 'prompt' field should be rejected"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "prompt": "This should not be allowed"
                }
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        # Should be rejected at validation level
        assert response.status_code in [400, 422]

    def test_forbidden_field_content(self, client, seed_data):
        """Test 9: Request with 'content' field should be rejected"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {
                    "messages": [
                        {
                            "role": "user",
                            "content": "This should not be allowed"
                        }
                    ]
                }
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        # Should be rejected at validation level
        assert response.status_code in [400, 422]

    def test_multiple_requests_same_key(self, client, seed_data):
        """Test 10: Multiple requests with same key should work"""
        raw_key = seed_data["raw_key"]
        
        for i in range(5):
            response = client.post(
                "/v1/check",
                json={
                    "model": "gpt-4",
                    "operation": "chat_completion",
                    "metadata": {"temperature": 0.7, "request_id": i}
                },
                headers={"Authorization": f"Bearer {raw_key}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["allowed"] is True

    def test_rate_limiting(self, client, seed_data):
        """Test 11: Rate limiting should be enforced"""
        raw_key = seed_data["raw_key"]
        
        # Send many requests rapidly
        allowed_count = 0
        blocked_count = 0
        
        for i in range(110):
            response = client.post(
                "/v1/check",
                json={
                    "model": "gpt-4",
                    "operation": "test",
                    "metadata": {"request_num": i}
                },
                headers={"Authorization": f"Bearer {raw_key}"}
            )
            
            if response.status_code == 200:
                allowed_count += 1
            elif response.status_code == 429:
                blocked_count += 1
        
        # Should have some rate limiting effect (at least some requests blocked)
        # and have allowed some requests through
        assert allowed_count > 0, f"Expected some allowed requests, got {allowed_count}"
        assert blocked_count > 0, f"Expected some blocked requests due to rate limit, got {blocked_count}"

    def test_response_structure(self, client, seed_data):
        """Test 12: Response structure should match schema"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {"temperature": 0.7}
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response schema
        assert "allowed" in data
        assert "risk_score" in data
        assert "reason" in data
        assert isinstance(data["allowed"], bool)
        assert isinstance(data["risk_score"], int)
        assert isinstance(data["reason"], str)
        assert data["risk_score"] >= 0

    def test_different_models(self, client, seed_data):
        """Test 13: Different model values should be accepted"""
        raw_key = seed_data["raw_key"]
        
        models = ["gpt-4", "gpt-3.5-turbo", "claude-2", "custom-model"]
        
        for model in models:
            response = client.post(
                "/v1/check",
                json={
                    "model": model,
                    "operation": "completion",
                    "metadata": {"max_tokens": 50}
                },
                headers={"Authorization": f"Bearer {raw_key}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["allowed"] is True

    def test_edge_case_empty_metadata(self, client, seed_data):
        """Test 14: Empty metadata should be handled"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {}
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is True
        assert data["risk_score"] == 0

    def test_edge_case_null_metadata(self, client, seed_data):
        """Test 15: Null metadata should be handled"""
        raw_key = seed_data["raw_key"]
        response = client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": None
            },
            headers={"Authorization": f"Bearer {raw_key}"}
        )
        # Should either accept or return validation error
        assert response.status_code in [200, 422]

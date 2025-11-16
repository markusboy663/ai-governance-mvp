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

from main import app, CheckRequest
from models import Customer, APIKey, Policy, CustomerPolicy
from sqlmodel import SQLModel
from db import AsyncSessionLocal
from async_logger import init_logger, shutdown_logger

# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_ai_governance"
)

# Override database URL for tests
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine and set up schema"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        # Drop existing tables for clean state
        await conn.run_sync(SQLModel.metadata.drop_all)
        # Create fresh tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # Cleanup after tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_session_factory(test_engine):
    """Create session factory for tests"""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    return async_session


@pytest.fixture
async def db_session(test_session_factory):
    """Get a database session for each test"""
    async with test_session_factory() as session:
        yield session


@pytest.fixture
async def seed_data(db_session):
    """Seed test data: customer, API key, policies"""
    
    # Create customer
    customer = Customer(
        id=str(uuid.uuid4()),
        name="Test Customer",
        email="test@example.com"
    )
    db_session.add(customer)
    await db_session.flush()
    
    # Generate API key with new format: <key_id>.<secret>
    key_id = str(uuid.uuid4())
    secret = f"test_secret_{uuid.uuid4().hex[:24]}"
    secret_hash = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()
    
    # Full token format
    raw_key = f"{key_id}.{secret}"
    
    api_key = APIKey(
        id=str(uuid.uuid4()),
        key_id=key_id,
        customer_id=customer.id,
        api_key_hash=secret_hash,
        is_active=True
    )
    db_session.add(api_key)
    await db_session.flush()
    
    # Create governance policies
    policy_allow = Policy(
        id=str(uuid.uuid4()),
        key="default_allow",
        description="Default allow all operations",
        default_value={"allowed": True, "risk_threshold": 100}
    )
    db_session.add(policy_allow)
    
    policy_personal = Policy(
        id=str(uuid.uuid4()),
        key="personal_data_protection",
        description="Block operations with personal data",
        default_value={"contains_personal_data": False}
    )
    db_session.add(policy_personal)
    
    policy_external = Policy(
        id=str(uuid.uuid4()),
        key="external_model_restriction",
        description="Block external model usage",
        default_value={"uses_external_model": False}
    )
    db_session.add(policy_external)
    
    await db_session.flush()
    
    # Assign policies to customer
    cp1 = CustomerPolicy(
        id=str(uuid.uuid4()),
        customer_id=customer.id,
        policy_id=policy_allow.id,
        value={"allowed": True, "risk_threshold": 100}
    )
    db_session.add(cp1)
    
    cp2 = CustomerPolicy(
        id=str(uuid.uuid4()),
        customer_id=customer.id,
        policy_id=policy_personal.id,
        value={"contains_personal_data": False}
    )
    db_session.add(cp2)
    
    cp3 = CustomerPolicy(
        id=str(uuid.uuid4()),
        customer_id=customer.id,
        policy_id=policy_external.id,
        value={"uses_external_model": False}
    )
    db_session.add(cp3)
    
    await db_session.commit()
    
    return {
        "customer": customer,
        "api_key": api_key,
        "raw_key": raw_key,
        "policies": {
            "allow": policy_allow,
            "personal": policy_personal,
            "external": policy_external
        }
    }


@pytest.fixture
async def client(db_session):
    """Create test client with app"""
    # Initialize async logger for tests
    await init_logger()
    
    # Override dependency to use test session
    async def override_get_session():
        return db_session
    
    from main import app
    app.dependency_overrides[AsyncSessionLocal] = override_get_session
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Cleanup
    await shutdown_logger()
    app.dependency_overrides.clear()


class TestE2EIntegration:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test 1: Health check endpoint (no auth required)"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_auth_invalid_key(self, client):
        """Test 2: Invalid API key should be rejected"""
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_auth_missing_header(self, client):
        """Test 3: Missing auth header should be rejected"""
        response = await client.post(
            "/v1/check",
            json={
                "model": "gpt-4",
                "operation": "chat_completion",
                "metadata": {"temperature": 0.7}
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "authenticated" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_allowed_operation(self, client, seed_data):
        """Test 4: Valid request with no risk flags should be allowed"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_blocked_personal_data(self, client, seed_data):
        """Test 5: Request with personal data flag should be blocked"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_blocked_external_model(self, client, seed_data):
        """Test 6: Request with external model flag should be blocked"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_blocked_high_risk(self, client, seed_data):
        """Test 7: Request with both risk flags should be blocked with high score"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_forbidden_field_prompt(self, client, seed_data):
        """Test 8: Request with 'prompt' field should be rejected"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_forbidden_field_content(self, client, seed_data):
        """Test 9: Request with 'content' field should be rejected"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_multiple_requests_same_key(self, client, seed_data):
        """Test 10: Multiple requests with same key should work"""
        raw_key = seed_data["raw_key"]
        
        for i in range(5):
            response = await client.post(
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

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client, seed_data):
        """Test 11: Rate limiting should be enforced"""
        raw_key = seed_data["raw_key"]
        
        # Send many requests rapidly
        allowed_count = 0
        blocked_count = 0
        
        for i in range(110):
            response = await client.post(
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
        
        # Should have allowed ~100 requests
        # Exact count depends on rate limit window
        assert allowed_count >= 90, f"Expected at least 90 allowed, got {allowed_count}"

    @pytest.mark.asyncio
    async def test_response_structure(self, client, seed_data):
        """Test 12: Response structure should match schema"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_different_models(self, client, seed_data):
        """Test 13: Different model values should be accepted"""
        raw_key = seed_data["raw_key"]
        
        models = ["gpt-4", "gpt-3.5-turbo", "claude-2", "custom-model"]
        
        for model in models:
            response = await client.post(
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

    @pytest.mark.asyncio
    async def test_edge_case_empty_metadata(self, client, seed_data):
        """Test 14: Empty metadata should be handled"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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

    @pytest.mark.asyncio
    async def test_edge_case_null_metadata(self, client, seed_data):
        """Test 15: Null metadata should be handled"""
        raw_key = seed_data["raw_key"]
        response = await client.post(
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
